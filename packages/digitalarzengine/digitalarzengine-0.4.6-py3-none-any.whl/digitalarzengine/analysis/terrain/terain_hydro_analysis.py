import os, math
import ee
from typing import Tuple, Optional

from geopandas import GeoDataFrame
from rasterio.transform import xy
from whitebox.whitebox_tools import WhiteboxTools
import rasterio
import numpy as np

from digitalarzengine.io.gee.gee_image import GEEImage
from digitalarzengine.io.rio_raster import RioRaster
from digitalarzengine.pipeline.gee_pipeline import GEEPipeline


class TerrainHydroAnalysis:
    def __init__(self, aoi_gdv: GeoDataFrame, data_dir: str):
        self.aoi_gdf = aoi_gdv
        # self.gee_pipeline: GEEPipeline = gee_pipline
        self.data_dir = data_dir
        self.scale = 30  # target pixel size (m). MERIT is ~90m; this will resample.
        self._eps = 1e-6

        # ensure folders
        os.makedirs(os.path.join(self.data_dir, "dem"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "indices"), exist_ok=True)
        # whitebox work dir
        self.wbt = WhiteboxTools()
        self.wbt.work_dir = os.path.join(self.data_dir, "indices")

    # ---------------- DEM ----------------
    @staticmethod
    def get_flow_dir(data_dir, scale=90, gee_pipeline=None) -> str:
        """
        Download MERIT flow direction (if missing), ensure ~target resolution, and return its file path.
            Flow Direction (Local Drainage Direction)
                1: east
                2: southeast
                4: south
                8: southwest
                16: west
                32: northwest
                64: north
                128: northeast
                0: river mouth
                -1: inland depression
        """
        fp = os.path.join(data_dir, "dem", "merit_flow_dir.tif")
        if not os.path.exists(fp):
            if gee_pipeline is None:
                raise ValueError(f"gee_pipeline must be provided or download dem at {fp}")
            region = gee_pipeline.region
            img = ee.Image("MERIT/Hydro/v1_0_1").select("dir")  # or v1_0_3, but pick one
            GEEImage(img).download_image(fp, region, scale, within_aoi_only=False, save_metadata=False)

        raster = RioRaster(fp)
        x_res, y_res = raster.get_spatial_resolution()
        if not (math.isclose(x_res, scale, rel_tol=0.1) and math.isclose(y_res, scale, rel_tol=0.1)):
            raster.resample(scale, resampling="nearest")

        return fp


    @staticmethod
    def get_hnd_dem_fp(data_dir, scale=90, gee_pipeline = None) -> str:
        """Download MERIT DEM (if missing), ensure ~target resolution, and return its file path."""
        fp = os.path.join(data_dir, "dem", "merit_dem.tif")
        if not os.path.exists(fp):
            if gee_pipeline is None:
                raise ValueError(f"gee_pipeline must be provided or download dem at {fp}")
            region = gee_pipeline.region
            img = ee.Image("MERIT/DEM/v1_0_3").select("dem")
            GEEImage(img).download_image(
                fp, region, scale, within_aoi_only=False, save_metadata=False
            )

        raster = RioRaster(fp)
        x_res, y_res = raster.get_spatial_resolution()
        # approx check; allow ~10% slack
        if not (math.isclose(x_res, scale, rel_tol=0.1) and math.isclose(y_res, scale, rel_tol=0.1)):
            raster.resample(scale, resampling="nearest")  # <-- missing ')' fixed

        return fp  # return path (needed by WhiteboxTools)


    @staticmethod
    def sanitize_for_whitebox(src_path: str, dst_path: str = None, compress="DEFLATE", tiled=True) -> str:
        """
        Rewrites a GeoTIFF so WhiteboxTools can read it:
          - removes floating-point predictor (forces predictor=1)
          - optional compression (default DEFLATE)
          - sets valid tile sizes (multiples of 16) if tiling is enabled
        """
        if dst_path is None:
            base, ext = os.path.splitext(src_path)
            dst_path = f"{base}_wb.tif"

        with rasterio.open(src_path) as src:
            data = src.read(1)
            profile = src.profile

        # Start with clean profile
        profile.update(
            dtype="float32",
            BIGTIFF="IF_SAFER",
        )

        # Handle nodata value - use -9999 instead of np.nan for better compatibility
        profile.update(nodata=-9999.0)
        
        # Replace NaN values in data with nodata value
        data = np.where(np.isnan(data), -9999.0, data)

        # Compression & predictor settings
        if compress:
            profile.update(compress=compress, predictor=1)
        else:
            profile.update(compress=None, predictor=1)

        # Configure tiling or strips
        if tiled:
            # Valid tile sizes: multiples of 16 (commonly 256)
            profile.update(tiled=True, blockxsize=256, blockysize=256)
        else:
            # Strip organization - let rasterio handle it automatically
            profile.update(tiled=False)
            # Remove tile-specific keys
            profile.pop("blockxsize", None)
            profile.pop("blockysize", None)
            # Don't set rowsperstrip - let rasterio use defaults

        # Write the sanitized file
        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(data.astype("float32"), 1)

        return dst_path

    # ---------------- SPI/TWI ----------------
    def calculate_SPI(self) -> str:
        """
        Calculates the Stream Power Index (SPI).

        SPI = As * tan(slope)

        Where:
            - As is the specific catchment area
            - tan(slope) is slope steepness (flow energy indicator)

        Purpose:
            - SPI measures the erosive power of flowing water.
            - High SPI areas indicate strong flow energy → higher erosion risk.
            - Useful for detecting risk areas like gully formation, bank erosion,
              embankment failure zones, and dangerous flow paths near villages.

        Why SPI matters with flood modeling:
            - Even if runoff is high, flat areas may not have destructive flows.
            - SPI helps separate slow flood ponding vs. high-energy destructive floods.

        Returns:
            Path to the generated 'spi.tif' raster.
        """

        dem_fp = self.get_hnd_dem_fp(self.data_dir)
        dem_fp = self.sanitize_for_whitebox(dem_fp)
        sca_path, slope_rad_path = self._prep_sca_and_slope(dem_fp)
        spi_path = os.path.join(self.data_dir, "indices", "spi.tif")
        self._write_spi(sca_path, slope_rad_path, spi_path)
        return spi_path

    def calculate_TWI(self) -> str:
        """
        Calculates the Topographic Wetness Index (TWI).

        TWI = ln(As / tan(slope))

        Where:
            - As is the specific catchment area (flow accumulation per unit contour length)
            - tan(slope) is the local slope in radians

        Purpose:
            - TWI identifies areas that are likely to accumulate surface water due to terrain.
            - Higher TWI = wetter areas → greater chance of waterlogging/flood ponding.
            - Useful in flood susceptibility, hydrological modeling, and runoff analysis.
            - Important when ranking villages for flood risk because it explains how
              much water is likely to stay (not just how much is produced as runoff).

        Returns:
            Path to the generated 'twi.tif' raster.
        """

        dem_fp = self.get_hnd_dem_fp(self.data_dir)
        dem_fp = self.sanitize_for_whitebox(dem_fp)
        sca_path, slope_rad_path = self._prep_sca_and_slope(dem_fp)
        twi_path = os.path.join(self.data_dir, "indices", "twi.tif")
        self._write_twi(sca_path, slope_rad_path, twi_path)
        return twi_path

    # ---------------- internals ----------------
    def _prep_sca_and_slope(self, dem_path: str) -> Tuple[str, str]:
        """Fill sinks → D8 specific contributing area (SCA) → slope (radians). Returns (sca_path, slope_path)."""
        dem_filled = os.path.join(self.data_dir, "indices", "dem_filled.tif")
        sca_path   = os.path.join(self.data_dir, "indices", "sca_m2_per_m.tif")
        slope_path = os.path.join(self.data_dir, "indices", "slope_rad.tif")

        if not os.path.exists(dem_filled):
            self.wbt.fill_depressions_wang_and_liu(dem=dem_path, output=dem_filled)

        if not os.path.exists(sca_path):
            self.wbt.d8_flow_accumulation(
                i=dem_filled, output=sca_path, out_type="Specific Contributing Area"
            )

        if not os.path.exists(slope_path):
            self.wbt.slope(dem=dem_filled, output=slope_path, zfactor=1.0, units="radians")

        return sca_path, slope_path

    def _write_twi(self, sca_path: str, slope_path: str, out_path: str) -> None:
        """TWI = ln( SCA / (tan(slope) + eps) )"""
        with rasterio.open(sca_path) as rs, rasterio.open(slope_path) as sl:
            As = rs.read(1).astype("float64")
            beta = sl.read(1).astype("float64")
            prof = rs.profile

        As = np.where(np.isfinite(As) & (As > 0), As, np.nan)
        tanb = np.tan(beta)
        tanb = np.where(np.isfinite(tanb) & (tanb >= 0), tanb, 0)

        twi = np.log(As / (tanb + self._eps))

        # robust clip to remove extreme tails (optional)
        lo, hi = np.nanpercentile(twi, 1), np.nanpercentile(twi, 99)
        twi = np.clip(twi, lo, hi)

        prof.update(dtype="float32", nodata=np.nan)
        with rasterio.open(out_path, "w", **prof) as dst:
            dst.write(twi.astype("float32"), 1)

    def _write_spi(self, sca_path: str, slope_path: str, out_path: str) -> None:
        """SPI = SCA * tan(slope)"""
        with rasterio.open(sca_path) as rs, rasterio.open(slope_path) as sl:
            As = rs.read(1).astype("float64")
            beta = sl.read(1).astype("float64")
            prof = rs.profile

        As = np.where(np.isfinite(As) & (As > 0), As, np.nan)
        tanb = np.tan(beta)
        tanb = np.where(np.isfinite(tanb) & (tanb >= 0), tanb, 0)

        spi = As * tanb

        # robust clip (optional)
        lo, hi = np.nanpercentile(spi, 1), np.nanpercentile(spi, 99)
        spi = np.clip(spi, lo, hi)

        prof.update(dtype="float32", nodata=np.nan)
        with rasterio.open(out_path, "w", **prof) as dst:
            dst.write(spi.astype("float32"), 1)


    def get_longest_flow_path_and_slope(
            self,
            flow_dir_fp: str,  # input D8 flow directions (MERIT dir)
            dem_fp: str,  # input DEM
            flow_length_fp: str = None,  # optional output path for flow length [m]
            longest_path_fp: str = None,  # optional output path for longest path mask
    ) -> Tuple[
        float,  # L_max_m
        float,  # S_avg
        Tuple[float, float],  # outlet_xy
        Tuple[float, float],  # head_xy
        Optional["RioRaster"],  # flow_len_raster
        Optional["RioRaster"],  # path_raster
    ]:
        """
        Compute the longest flow path length [m], its average slope [m/m],
        and the main pour point (outlet of that path) from D8 flow directions
        and a DEM.

        Parameters
        ----------
        flow_dir_fp : str
            Path to D8 flow-direction raster (MERIT dir).
        dem_fp : str
            Path to DEM raster.
        flow_length_fp : str, optional
            If provided, flow-length raster will be written to this path.
        longest_path_fp : str, optional
            If provided, longest-path mask will be written to this path.

        Returns
        -------
        L_max_m : float
            Longest flow path length in meters.
        S_avg : float
            Average slope [m/m] along the longest flow path.
        outlet_xy : (float, float)
            Coordinates (x, y) of the pour point (outlet) in the raster CRS.
        head_xy : (float, float)
            Coordinates (x, y) of the headwater (start) of the longest path.
        flow_len_raster : Optional[RioRaster]
            Flow-length raster as RioRaster (may be None if no valid path).
        path_raster : Optional[RioRaster]
            Longest-path mask raster as RioRaster (may be None if no valid path).

        Usage:
            L, S, outlet_xy, head_xy, flow_len_rr, path_rr = tha.get_longest_flow_path_and_slope(
                flow_dir_fp=flow_dir_fp,
                dem_fp=dem_fp,
                flow_length_fp=os.path.join(data_dir, "indices", "flow_length_m.tif"),
                longest_path_fp=os.path.join(data_dir, "indices", "longest_flow_path_mask.tif"),
            )

            print("Longest path L [m] =", L)
            print("Average slope S [-] =", S)
            print("Pour point (x, y)  =", outlet_xy)
            print("Headwater (x, y)    =", head_xy)

        """

        # ------------------------------------------------------------------
        # 1. Load flow direction raster
        # ------------------------------------------------------------------
        flow_dir_raster = RioRaster(flow_dir_fp)
        flow_dir = flow_dir_raster.get_data_array(1).astype(np.int16)
        rows, cols = flow_dir.shape

        fd_nodata = flow_dir_raster.get_nodata_value()
        valid_mask = np.ones_like(flow_dir, dtype=bool)
        if fd_nodata is not None:
            if np.issubdtype(flow_dir.dtype, np.floating) and np.isnan(fd_nodata):
                valid_mask &= ~np.isnan(flow_dir)
            else:
                valid_mask &= (flow_dir != fd_nodata)

        # D8 directions: only the 8 valid flow codes.
        d8_dict = {
            1: (0, 1),  # E
            2: (1, 1),  # SE
            4: (1, 0),  # S
            8: (1, -1),  # SW
            16: (0, -1),  # W
            32: (-1, -1),  # NW
            64: (-1, 0),  # N
            128: (-1, 1),  # NE
        }

        # Pixel spacing in meters
        px_x, px_y = flow_dir_raster.get_spatial_resolution(in_meter=True)
        px_x = float(px_x)
        px_y = float(px_y)

        # ------------------------------------------------------------------
        # 2. Load DEM and make it coincident with flow_dir grid
        # ------------------------------------------------------------------
        dem_raster = RioRaster(dem_fp)
        dem_raster = dem_raster.make_coincident(flow_dir_raster, resampling="bilinear")
        dem = dem_raster.get_data_array(1).astype(np.float32)

        dem_nodata = dem_raster.get_nodata_value()
        if dem_nodata is not None:
            if np.issubdtype(dem.dtype, np.floating) and np.isnan(dem_nodata):
                valid_mask &= ~np.isnan(dem)
            else:
                valid_mask &= (dem != dem_nodata)

        # ------------------------------------------------------------------
        # 3. Compute inflow count (in-degree) for each cell
        # ------------------------------------------------------------------
        inflow_count = np.zeros_like(flow_dir, dtype=np.int32)
        for code, (dr, dc) in d8_dict.items():
            # donors: cells whose flow_dir == code
            mask = (flow_dir == code) & valid_mask

            # shift donors into their downstream receivers
            shifted = np.roll(np.roll(mask, dr, axis=0), dc, axis=1)

            # kill wrap-around artifacts at borders
            if dr == 1:
                shifted[0, :] = False
            elif dr == -1:
                shifted[-1, :] = False
            if dc == 1:
                shifted[:, 0] = False
            elif dc == -1:
                shifted[:, -1] = False

            shifted &= valid_mask
            inflow_count += shifted.astype(np.int32)

        # ------------------------------------------------------------------
        # 4. Topological traversal to compute flow length [m]
        # ------------------------------------------------------------------
        from collections import deque
        flow_len = np.zeros_like(flow_dir, dtype=np.float32)
        q = deque()

        # Headwater cells: valid cells with no inflow
        src_rows, src_cols = np.where((inflow_count == 0) & valid_mask)
        for r, c in zip(src_rows, src_cols):
            q.append((r, c))
            flow_len[r, c] = 0.0

        while q:
            r, c = q.popleft()
            if not valid_mask[r, c]:
                continue

            fd = flow_dir[r, c]
            # sinks: 0 / -1 and invalid codes → no outflow
            if fd in (0, -1) or fd not in d8_dict:
                continue

            dr, dc = d8_dict[fd]
            rr, cc = r + dr, c + dc

            if 0 <= rr < rows and 0 <= cc < cols and valid_mask[rr, cc]:
                dx = px_x * dc
                dy = px_y * dr
                step_dist = math.hypot(dx, dy)

                candidate = flow_len[r, c] + step_dist
                if candidate > flow_len[rr, cc]:
                    flow_len[rr, cc] = candidate

                inflow_count[rr, cc] -= 1
                if inflow_count[rr, cc] == 0:
                    q.append((rr, cc))

        # ------------------------------------------------------------------
        # 5. Longest flow path length and outlet cell
        # ------------------------------------------------------------------
        if not valid_mask.any():
            return 0.0, 0.0, (np.nan, np.nan), (np.nan, np.nan), None, None

        masked_lengths = np.where(valid_mask, flow_len, -np.inf)
        flat_index = np.argmax(masked_lengths)
        outlet_r, outlet_c = divmod(flat_index, cols)
        L_max_m = float(flow_len[outlet_r, outlet_c])

        if L_max_m <= 0:
            return 0.0, 0.0, (np.nan, np.nan), (np.nan, np.nan), None, None

        transform = flow_dir_raster.get_geo_transform()
        # rasterio.transform.xy(transform, row, col)
        outlet_x, outlet_y = xy(transform, outlet_r, outlet_c)

        # ------------------------------------------------------------------
        # 6. Backtrack upstream to find the headwater cell for this path
        # ------------------------------------------------------------------
        def upstream_neighbors(r: int, c: int):
            """Yield (rr, cc) cells that drain into (r, c)."""
            for code, (dr, dc) in d8_dict.items():
                rr = r - dr
                cc = c - dc
                if 0 <= rr < rows and 0 <= cc < cols and valid_mask[rr, cc]:
                    if flow_dir[rr, cc] == code:
                        yield rr, cc

        path_cells = []
        r, c = outlet_r, outlet_c
        while True:
            path_cells.append((r, c))
            candidates = list(upstream_neighbors(r, c))
            if not candidates:
                break  # reached headwater
            # choose upstream neighbor with largest flow length
            r, c = max(candidates, key=lambda rc: flow_len[rc[0], rc[1]])

        head_r, head_c = r, c
        head_x, head_y = xy(transform, head_r, head_c)

        # ------------------------------------------------------------------
        # 7. Average slope along that path
        # ------------------------------------------------------------------
        z_head = float(dem[head_r, head_c])
        z_out = float(dem[outlet_r, outlet_c])
        dz = max(z_head - z_out, 0.0)
        S_avg = dz / L_max_m if L_max_m > 0 else 0.0

        # ------------------------------------------------------------------
        # 8. Build RioRaster for flow-length and path mask (consistent nodata)
        # ------------------------------------------------------------------
        out_nodata = -9999.0

        # Flow-length raster
        flow_len_out = flow_len.copy()
        flow_len_out[~valid_mask] = out_nodata
        flow_len_raster = RioRaster.raster_from_array(
            img_arr=flow_len_out.astype(np.float32),
            crs=flow_dir_raster.get_crs(),
            g_transform=flow_dir_raster.get_geo_transform(),
            nodata_value=out_nodata,
        )

        # Longest-path mask raster (1 on path, 0 elsewhere, nodata outside valid_mask)
        path_mask = np.zeros_like(flow_len, dtype=np.uint8)
        for (pr, pc) in path_cells:
            path_mask[pr, pc] = 1
        path_mask_out = path_mask.copy()
        # Optional: if you want outside valid_mask to be nodata instead of 0
        path_mask_out[~valid_mask] = 0

        path_raster = RioRaster.raster_from_array(
            img_arr=path_mask_out.astype(np.uint8),
            crs=flow_dir_raster.get_crs(),
            g_transform=flow_dir_raster.get_geo_transform(),
            nodata_value=0,  # 0 = background / nodata
        )

        # Optionally save to disk if file paths provided
        if flow_length_fp is not None and flow_len_raster is not None:
            flow_len_raster.save_to_file(flow_length_fp, nodata_value=out_nodata)
        if longest_path_fp is not None and path_raster is not None:
            path_raster.save_to_file(longest_path_fp, nodata_value=0)

        outlet_xy = (float(outlet_x), float(outlet_y))
        head_xy = (float(head_x), float(head_y))

        return L_max_m, S_avg, outlet_xy, head_xy, flow_len_raster, path_raster


if __name__ == '__main__':
    # catalog = GeoDataCatalog()
    # data_dir = catalog.get_terrain_data_dir()
    data_dir = "tests/data/terrain"
    aoi_gdf = GeoDataFrame()
    gee_pipeline = None
    tha = TerrainHydroAnalysis(aoi_gdf, data_dir)
    dem_fp = TerrainHydroAnalysis.get_hnd_dem_fp(data_dir, scale=30, gee_pipeline=gee_pipeline)
    tha.calculate_SPI()
    tha.calculate_TWI()