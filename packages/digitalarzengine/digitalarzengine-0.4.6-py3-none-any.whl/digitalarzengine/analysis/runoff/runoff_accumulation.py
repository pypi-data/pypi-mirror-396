import math
import os
from typing import Literal

import numpy as np
import pandas as pd
from geopandas import GeoDataFrame
from rasterio.transform import xy
from tqdm import tqdm

from digitalarzengine.analysis.meteo_analysis import MeteoAnalysis
from digitalarzengine.analysis.runoff.runoff_coefficient import RunoffCoefficient
from digitalarzengine.analysis.soil_capacity_analysis import SoilCapacityAnalysis
from digitalarzengine.io.rio_raster import RioRaster
from digitalarzengine.pipeline.gee_pipeline import GEEPipeline
import geopandas as gpd

from digitalarzengine.processing.raster.band_process import BandProcess

RunoffParams =Literal[
                          "excessive_precipitation", "effective_precipitation",
                          "runoff_volume", "surplus_water", "accumulated_runoff",
                          "discharge_m3s","data_dir"]

class RunoffAccumulation:

    def __init__(self, aoi_gdf: gpd.GeoDataFrame, init_gee_pipeline, data_dir: str, scale: float=100):
        """

        :param aoi_gdf:  Geodataframe of AOI
        :param init_gee_pipeline:  Function to initialize GEE Pipeline where needed
        :param data_dir:  directory to extract and save data
        :param scale: spatial resolution of the data
        """
        self.init_pipeline = init_gee_pipeline
        self.aoi_gdf = aoi_gdf
        self.data_dir = data_dir
        self.scale = scale
        self.gee_pipline = None

    @staticmethod
    def get_raster_fp(data_dir: str, rp=None,param: RunoffParams = None):
        # data_dir = str(GeoDataCatalog.get_runoff_modeling_dir())
        os.makedirs(data_dir, exist_ok=True)

        if param == "excessive_precipitation":
            fp = os.path.join(data_dir, f"excessive_precipitation_{rp}_years.tif")
        elif param == "effective_precipitation":
            fp = os.path.join(data_dir, f"effective_precipitation_{rp}_years.tif")
        elif param == "runoff_volume":
            fp = os.path.join(data_dir, f"runoff_volume_{rp}_years.tif")
        elif param == "surplus_water":
            fp = os.path.join(data_dir, f"surplus_water_{rp}_years.tif")
        elif param == "accumulated_runoff":
            fp = os.path.join(data_dir, f"accumulated_runoff_{rp}_years.tif")
        elif param == "discharge_m3s":
            fp = os.path.join(data_dir, f"discharge_m3s_{rp}_years.tif")
        else:
            # raise ValueError(f"no such parameter: {param}")
            return data_dir
        return fp

    def get_excessive_precipitation(self, rp, ref_raster: RioRaster, meteo_dir, soil_data_dir):
        """
        Compute Effective and Excessive Precipitation rasters for a given return period.
        (docstring unchanged for brevity)
        """

        # -------------------------------------------------------------------------
        # 0. Check if results already exist on disk
        # -------------------------------------------------------------------------
        eff_fp = self.get_raster_fp(self.data_dir, rp, "effective_precipitation")
        exc_fp = self.get_raster_fp(self.data_dir, rp, "excessive_precipitation")

        if os.path.exists(eff_fp) and os.path.exists(exc_fp):
            # Load already computed rasters
            eff_raster = RioRaster(eff_fp)
            exc_raster = RioRaster(exc_fp)

            effective_precipitation_data = eff_raster.get_data_array(1)
            excessive_precipitation_data = exc_raster.get_data_array(1)

            # Optionally still load meteo data (cheap compared to full recompute)
            pr_rp_raster, et_rp_raster, band_name = MeteoAnalysis.get_meteo_data(meteo_dir, rp)
            pr_data = pr_rp_raster.get_data_array_by_band_name([band_name])
            et_data = et_rp_raster.get_data_array_by_band_name([band_name])

            return effective_precipitation_data, excessive_precipitation_data, pr_data, et_data

        # -------------------------------------------------------------------------
        # 1. Load precipitation (P_T) and evapotranspiration (ET_T)
        # -------------------------------------------------------------------------
        pr_rp_raster, et_rp_raster, band_name = MeteoAnalysis.get_meteo_data(meteo_dir, rp)
        pr_data = pr_rp_raster.get_data_array_by_band_name([band_name])
        et_data = et_rp_raster.get_data_array_by_band_name([band_name])

        # Effective Precipitation
        # -----------------------
        # P_e(i,j) = max(P_T(i,j) - ET_T(i,j), 0)
        effective_precipitation_data = pr_data - et_data
        print(effective_precipitation_data.shape)

        # Save Effective Precipitation Raster
        eff_fp = self.get_raster_fp(self.data_dir, rp, "effective_precipitation")
        effective_precipitation_raster = ref_raster.rio_raster_from_array(effective_precipitation_data)
        effective_precipitation_raster.save_to_file(eff_fp)

        # -------------------------------------------------------------------------
        # 2. Soil Capacity Raster
        # -------------------------------------------------------------------------
        if self.gee_pipline is None:
            self.gee_pipline = self.init_pipeline()
        soil_analysis = SoilCapacityAnalysis(self.gee_pipline, self.aoi_gdf, soil_data_dir)
        soil_analysis.calculate_total_soil_capacity()
        sc_fp = SoilCapacityAnalysis.get_raster_path(soil_data_dir, "total_soil_capacity")

        sc_raster = RioRaster(sc_fp)
        sc_raster.resample(self.scale, resampling="nearest")
        sc_raster_data = sc_raster.clip_raster(self.aoi_gdf).get_data_array(1)
        print(sc_raster_data.shape)

        sc_raster_data, effective_precipitation_data = BandProcess.resize_to_match(
            sc_raster_data,
            effective_precipitation_data,
        )

        # -------------------------------------------------------------------------
        # 3. Excessive Precipitation
        # -------------------------------------------------------------------------
        # P_x(i,j) = max(P_e(i,j) - S(i,j), 0)
        excessive_precipitation_data = np.maximum(effective_precipitation_data - sc_raster_data, 0)
        print(excessive_precipitation_data.shape)

        # Save Excessive Precipitation Raster
        exc_fp = self.get_raster_fp(self.data_dir, rp, "excessive_precipitation")
        excessive_precipitation_raster = sc_raster.rio_raster_from_array(excessive_precipitation_data)
        excessive_precipitation_raster.save_to_file(exc_fp)

        return effective_precipitation_data, excessive_precipitation_data, pr_data, et_data


    def calculate_runoff_volume(self, rp, meteo_dir, soil_data_dir, bands: dict):
        """
        Compute and save Runoff Volume (depth, mm) and Surplus Water (mm) rasters
        for a given return period, using the runoff coefficient and excessive
        precipitation. Also appends intermediate bands into the provided dict.

        If the output rasters already exist, they are loaded and added to `bands`
        instead of recalculating.
        """
        # ------------------------------------------------------------------
        # 1. File paths
        # ------------------------------------------------------------------
        runoff_volume_fp = self.get_raster_fp(self.data_dir, rp, "runoff_volume")
        surplus_water_fp = self.get_raster_fp(self.data_dir, rp, "surplus_water")

        # ------------------------------------------------------------------
        # 2. Short-circuit: if outputs exist, just load & fill `bands`
        # ------------------------------------------------------------------
        if os.path.exists(runoff_volume_fp) and os.path.exists(surplus_water_fp):
            # Load existing rasters
            runoff_volume_raster = RioRaster(runoff_volume_fp)
            surplus_water_raster = RioRaster(surplus_water_fp)

            runoff_volume = runoff_volume_raster.get_data_array(1)
            surplus_water = surplus_water_raster.get_data_array(1)

            # Store in bands so downstream code still works
            bands[f"Runoff_volume_return_period_{rp}_year"] = runoff_volume
            bands[f"Surplus_water_return_period_{rp}_year"] = surplus_water

            # If you *also* need precipitation/ET/etc. when files exist,
            # you could optionally recompute them here by calling
            # `get_excessive_precipitation` – otherwise we skip heavy work.
            return  # nothing more to do

        # ------------------------------------------------------------------
        # 3. Normal path: compute everything and write new rasters
        # ------------------------------------------------------------------
        ro_coff_fp = RunoffCoefficient.get_raster_fp(self.data_dir)
        if not os.path.exists(ro_coff_fp):
            runoff_coeff = RunoffCoefficient()
            runoff_coeff.calculate_runoff_coefficient(self.aoi_gdf)

        ro_coff_raster = RioRaster(ro_coff_fp)
        ro_coff_raster.resample(self.scale, resampling="nearest")
        ro_coff_raster.clip_raster(self.aoi_gdf)
        ro_coff_data = ro_coff_raster.get_data_array(1)

        min_coff = np.nanmin(ro_coff_data)
        max_coff = np.nanmax(ro_coff_data)
        print("runoff_coff min", min_coff)
        print("runoff_coff max", max_coff)
        print("runoff_coff shape", ro_coff_data.shape)

        (
            effective_precipitation_data,
            excessive_precipitation_data,
            pr_data,
            et_data,
        ) = self.get_excessive_precipitation(rp, ro_coff_raster, meteo_dir, soil_data_dir)

        bands[f"Precipitation_return_period_{rp}_year"] = pr_data
        bands[f"ET_return_period_{rp}_year"] = et_data
        bands[f"Effective_precipitation_return_period_{rp}_year"] = effective_precipitation_data
        bands[f"Excessive_precipitation_return_period_{rp}_year"] = excessive_precipitation_data

        excessive_precipitation_data, ro_coff_data = BandProcess.resize_to_match(
            excessive_precipitation_data, ro_coff_data
        )

        # Runoff depth (mm): R_mm = C * P_x
        runoff_volume = excessive_precipitation_data * ro_coff_data

        runoff_volume_raster = ro_coff_raster.rio_raster_from_array(runoff_volume)
        runoff_volume_raster.save_to_file(runoff_volume_fp)

        # Surplus water (mm): S_sur = max(P_x - R_mm, 0)
        surplus_water = np.maximum(excessive_precipitation_data - runoff_volume, 0)
        excess_water_raster = ro_coff_raster.rio_raster_from_array(surplus_water)
        excess_water_raster.save_to_file(surplus_water_fp)

        bands[f"Runoff_volume_return_period_{rp}_year"] = runoff_volume
        bands[f"Surplus_water_return_period_{rp}_year"] = surplus_water

    def calculate_runoff_accumulation(self, rp: int, flow_dir_fp: str) -> str:
        """
        Calculate cumulative runoff (weighted flow accumulation) from flow direction raster.

        A_runoff(i,j) = R(i,j) + Σ_{(m,n) ∈ U(i,j)} R(m,n)

        Parameters
        ----------
        rp : int
            Return period.
        flow_dir_fp : str
            Path to flow direction raster (D8 encoded).

        Returns
        -------
        runoff_acc_fp : str
            File path of the runoff accumulation raster.
        """

        # -------------------------------------------------------------------------
        # 0. Check if result already exists
        # -------------------------------------------------------------------------
        runoff_acc_fp = self.get_raster_fp(self.data_dir, rp, "accumulated_runoff")
        if os.path.exists(runoff_acc_fp):
            print(f"Cumulative runoff raster already exists: {runoff_acc_fp}")
            return runoff_acc_fp

        # -------------------------------------------------------------------------
        # 1. Load rasters and align grids
        # -------------------------------------------------------------------------
        runoff_volume_fp = self.get_raster_fp(self.data_dir, rp, "runoff_volume")
        runoff_raster = RioRaster(runoff_volume_fp)

        # Use masked array to respect NoData
        runoff_ma = runoff_raster.get_masked_array(1)
        runoff = runoff_ma.filled(0).astype(np.float32)  # numeric array for accumulation
        valid_mask = ~runoff_ma.mask  # True where runoff is valid

        flow_dir_raster = RioRaster(flow_dir_fp)
        # ensure flow_dir has SAME grid (CRS, transform, width, height) as runoff
        flow_dir_raster = flow_dir_raster.make_coincident(runoff_raster, resampling="nearest")
        flow_dir = flow_dir_raster.get_data_array(1).astype(np.int16)

        # combine validity with flow_dir nodata
        fd_nodata = flow_dir_raster.get_nodata_value()
        if fd_nodata is not None:
            if np.issubdtype(flow_dir.dtype, np.floating) and np.isnan(fd_nodata):
                valid_mask &= ~np.isnan(flow_dir)
            else:
                valid_mask &= (flow_dir != fd_nodata)

        rows, cols = runoff.shape  # == flow_dir.shape

        # D8 direction encoding
        d8_dict = {
            1: (0, 1),  # east
            2: (1, 1),  # southeast
            4: (1, 0),  # south
            8: (1, -1),  # southwest
            16: (0, -1),  # west
            32: (-1, -1),  # northwest
            64: (-1, 0),  # north
            128: (-1, 1),  # northeast
            # 0, -1 handled as sinks (no outflow)
        }

        runoff_acc = np.zeros_like(runoff, dtype=np.float32)

        # -------------------------------------------------------------------------
        # 2. Calculate number of inflowing neighbors (in-degree)
        # -------------------------------------------------------------------------
        inflow_count = np.zeros_like(runoff, dtype=np.int32)

        for code, (dr, dc) in d8_dict.items():
            # donors are cells with this code
            mask = (flow_dir == code) & valid_mask  # donors must be valid

            # shift donors into their downstream receivers
            shifted = np.roll(np.roll(mask, dr, axis=0), dc, axis=1)

            # kill wrap-around artifacts from np.roll
            if dr == 1:
                shifted[0, :] = False  # came from outside top
            elif dr == -1:
                shifted[-1, :] = False  # came from outside bottom

            if dc == 1:
                shifted[:, 0] = False  # came from outside left
            elif dc == -1:
                shifted[:, -1] = False  # came from outside right

            # receivers must also be valid
            shifted &= valid_mask

            inflow_count += shifted.astype(np.int32)

        # -------------------------------------------------------------------------
        # 3. Queue-based accumulation (topological order)
        # -------------------------------------------------------------------------
        from collections import deque
        q = deque()

        # Initialize with source pixels (no inflow) that are valid
        src_rows, src_cols = np.where((inflow_count == 0) & valid_mask)
        for r, c in zip(src_rows, src_cols):
            q.append((r, c))
            runoff_acc[r, c] = runoff[r, c]

        while q:
            r, c = q.popleft()

            if not valid_mask[r, c]:
                continue

            fd = flow_dir[r, c]

            # Skip sinks / depressions and any unknown codes
            if fd in (0, -1) or fd not in d8_dict:
                continue

            dr, dc = d8_dict[fd]
            rr, cc = r + dr, c + dc

            if 0 <= rr < rows and 0 <= cc < cols and valid_mask[rr, cc]:
                runoff_acc[rr, cc] += runoff_acc[r, c]
                inflow_count[rr, cc] -= 1
                if inflow_count[rr, cc] == 0:
                    q.append((rr, cc))

        # -------------------------------------------------------------------------
        # 4. Apply NoData to invalid cells
        # -------------------------------------------------------------------------
        out_nodata = runoff_raster.get_nodata_value()
        if out_nodata is not None:
            # ensure type compatibility
            if not np.issubdtype(runoff_acc.dtype, np.floating) and isinstance(out_nodata, float) and np.isnan(
                    out_nodata):
                runoff_acc = runoff_acc.astype(np.float32)
            runoff_acc[~valid_mask] = out_nodata

        # -------------------------------------------------------------------------
        # 5. Save result
        # -------------------------------------------------------------------------
        runoff_raster.rio_raster_from_array(runoff_acc).save_to_file(runoff_acc_fp)
        print(f"Cumulative runoff raster saved: {runoff_acc_fp}")

        return runoff_acc_fp

    import math
    from typing import Tuple, Optional

    # def calculate_longest_flow_path(
    #         self,
    #         flow_dir_fp: str,
    #         rp: int = 0,
    #         save_raster: bool = False,
    # ) -> Tuple[float, Optional[str]]:
    #     """
    #     Compute the longest flow path length [m] from a D8 flow direction raster.
    #
    #     This uses the same D8 encoding as in your accumulation code:
    #
    #         1   : east      (0,  1)
    #         2   : southeast (1,  1)
    #         4   : south     (1,  0)
    #         8   : southwest (1, -1)
    #         16  : west      (0, -1)
    #         32  : northwest (-1, -1)
    #         64  : north     (-1,  0)
    #         128 : northeast (-1,  1)
    #         0   : sink / outlet (no outflow)
    #         -1  : depression (no outflow)
    #
    #     Algorithm
    #     ---------
    #     1. Compute for each cell the number of inflowing neighbors (in-degree)
    #        using the D8 directions (like you did for runoff accumulation).
    #     2. Initialize a queue with all *source* cells (those with zero inflow).
    #        Their initial flow length = 0.
    #     3. Process cells in topological order (from headwaters to sinks):
    #        For each cell, add step-distance to its downstream neighbor and
    #        update that neighbor's flow length as the maximum from all its
    #        upstream contributors.
    #     4. The longest flow path L is simply max(flow_length).
    #
    #     Parameters
    #     ----------
    #     flow_dir_fp : str
    #         Path to the D8 flow direction raster.
    #     rp : int, optional
    #         Return period used only for naming the output flow-length raster
    #         if `save_raster=True`. Hydrologically, L does not depend on rp.
    #     save_raster : bool, optional
    #         If True, also save a flow-length raster [m] to disk and return
    #         its file path.
    #
    #     Returns
    #     -------
    #     L_max_m : float
    #         Longest flow path length in meters (maximal flow length in the raster).
    #     flow_length_fp : str or None
    #         File path of the saved flow-length raster (if save_raster=True),
    #         otherwise None.
    #     """
    #
    #     # -------------------------------------------------------------------------
    #     # 1. Load flow direction raster
    #     # -------------------------------------------------------------------------
    #     flow_dir_raster = RioRaster(flow_dir_fp)
    #     flow_dir = flow_dir_raster.get_data_array(1).astype(np.int16)
    #     rows, cols = flow_dir.shape
    #
    #     fd_nodata = flow_dir_raster.get_nodata_value()
    #     valid_mask = np.ones_like(flow_dir, dtype=bool)
    #     if fd_nodata is not None:
    #         if np.issubdtype(flow_dir.dtype, np.floating) and np.isnan(fd_nodata):
    #             valid_mask &= ~np.isnan(flow_dir)
    #         else:
    #             valid_mask &= (flow_dir != fd_nodata)
    #
    #     # D8 directions (same as your earlier code, but without 0/-1 here)
    #     d8_dict = {
    #         1: (0, 1),  # east
    #         2: (1, 1),  # southeast
    #         4: (1, 0),  # south
    #         8: (1, -1),  # southwest
    #         16: (0, -1),  # west
    #         32: (-1, -1),  # northwest
    #         64: (-1, 0),  # north
    #         128: (-1, 1),  # northeast
    #     }
    #
    #     # Pixel spacing in meters
    #     px_x, px_y = flow_dir_raster.get_spatial_resolution(in_meter=True)
    #     px_x = float(px_x)
    #     px_y = float(px_y)
    #     dist_cardinal = math.hypot(px_x if px_x != 0 else 0.0,
    #                                0.0 if px_y == 0 else 0.0)  # essentially |px_x|
    #     # but to be robust, we’ll compute per direction below using hypot(px_x*dc, px_y*dr)
    #
    #     # -------------------------------------------------------------------------
    #     # 2. Compute inflow count (in-degree) for each cell
    #     # -------------------------------------------------------------------------
    #     inflow_count = np.zeros_like(flow_dir, dtype=np.int32)
    #
    #     for code, (dr, dc) in d8_dict.items():
    #         # donors: cells whose flow_dir == code
    #         mask = (flow_dir == code) & valid_mask
    #
    #         # shift donors into their downstream receivers
    #         shifted = np.roll(np.roll(mask, dr, axis=0), dc, axis=1)
    #
    #         # remove wrap-around artifacts
    #         if dr == 1:
    #             shifted[0, :] = False
    #         elif dr == -1:
    #             shifted[-1, :] = False
    #
    #         if dc == 1:
    #             shifted[:, 0] = False
    #         elif dc == -1:
    #             shifted[:, -1] = False
    #
    #         # receivers must also be valid
    #         shifted &= valid_mask
    #
    #         inflow_count += shifted.astype(np.int32)
    #
    #     # -------------------------------------------------------------------------
    #     # 3. Topological traversal to compute flow length
    #     # -------------------------------------------------------------------------
    #     from collections import deque
    #
    #     flow_len = np.zeros_like(flow_dir, dtype=np.float32)
    #
    #     # Initialize queue with headwater cells (no inflow, but valid)
    #     q = deque()
    #     src_rows, src_cols = np.where((inflow_count == 0) & valid_mask)
    #     for r, c in zip(src_rows, src_cols):
    #         q.append((r, c))
    #         flow_len[r, c] = 0.0
    #
    #     while q:
    #         r, c = q.popleft()
    #
    #         if not valid_mask[r, c]:
    #             continue
    #
    #         fd = flow_dir[r, c]
    #
    #         # sinks / depressions / invalid codes have no outflow
    #         if fd in (0, -1) or fd not in d8_dict:
    #             continue
    #
    #         dr, dc = d8_dict[fd]
    #         rr, cc = r + dr, c + dc
    #
    #         if 0 <= rr < rows and 0 <= cc < cols and valid_mask[rr, cc]:
    #             # compute step distance using actual pixel spacing
    #             dx = px_x * dc
    #             dy = px_y * dr
    #             step_dist = math.hypot(dx, dy)  # [m]
    #
    #             candidate = flow_len[r, c] + step_dist
    #             if candidate > flow_len[rr, cc]:
    #                 flow_len[rr, cc] = candidate
    #
    #             inflow_count[rr, cc] -= 1
    #             if inflow_count[rr, cc] == 0:
    #                 q.append((rr, cc))
    #
    #     # -------------------------------------------------------------------------
    #     # 4. Longest flow path = maximum flow_len over valid cells
    #     # -------------------------------------------------------------------------
    #     if valid_mask.any():
    #         L_max_m = float(flow_len[valid_mask].max())
    #     else:
    #         L_max_m = 0.0
    #
    #     flow_length_fp = None
    #
    #     # -------------------------------------------------------------------------
    #     # 5. Optionally save flow-length raster [m]
    #     # -------------------------------------------------------------------------
    #     if save_raster:
    #         # Mask invalid cells as nodata
    #         if fd_nodata is None:
    #             # choose a nodata value if not defined
    #             fd_nodata = -9999.0
    #
    #         flow_len_out = flow_len.copy()
    #         # set nodata for invalid pixels
    #         flow_len_out[~valid_mask] = fd_nodata
    #
    #         # align metadata with flow_dir raster and save
    #         flow_len_raster = flow_dir_raster.rio_raster_from_array(flow_len_out.astype(np.float32))
    #
    #         # use your own helper to get file path
    #         flow_length_fp = self.get_raster_fp(self.data_dir, rp, "flow_length_m")
    #         flow_len_raster.save_to_file(flow_length_fp, nodata_value=fd_nodata)
    #         print(f"Flow-length raster saved: {flow_length_fp}")
    #
    #     return L_max_m, flow_length_fp



    def estimate_time_of_concentration(
            self,
            L_m: float,
            S: float,
            method: str = "kirpich"
    ) -> float:
        """
        Estimate time of concentration Tc [hours] for a catchment.

        Currently implements the metric Kirpich formula:

            Tc(min) = 0.01947 * L_m^0.77 * S^(-0.385)

        where:
            L_m : longest flow path [m]
            S   : average slope along that path [m/m]

        Parameters
        ----------
        L_m : float
            Longest flow path length in meters.
        S : float
            Average slope (dimensionless, m/m).
        method : {"kirpich"}, optional
            Empirical method to use (only "kirpich" implemented for now).

        Returns
        -------
        Tc_hours : float
            Time of concentration in hours.

        Usage:
            Tc_hours = self.estimate_time_of_concentration(L_m=longest_flow_path_m, S=avg_slope)
            self.calculate_discharge_raster(
                rp=10,
                event_duration_hours=Tc_hours,
                units="volume_m3",  # or "depth_mm", depending on your raster
            )

        """
        if method.lower() == "kirpich":
            if L_m <= 0 or S <= 0:
                raise ValueError("L_m and S must be > 0 for Kirpich Tc computation.")
            Tc_min = 0.01947 * (L_m ** 0.77) * (S ** -0.385)
            return Tc_min / 60.0  # convert minutes → hours

        raise ValueError(f"Unsupported Tc method: {method}")

    def calculate_discharge_raster(
            self,
            rp: int,
            event_duration_hours: float,
            units: str = "volume_m3",
    ) -> str:
        """
        Calculate a discharge raster [m³/s] from accumulated runoff.

        This function converts an accumulated runoff raster (per-cell) into
        an average discharge raster over a given event duration:

            Q = V / T

        where
            Q : discharge [m³/s]
            V : total runoff volume at the cell [m³]
            T : event duration [s]

        The accumulated runoff raster can be interpreted in two ways,
        controlled by the `units` argument:

        1) units = "volume_m3" (default)
           - The accumulated raster stores total runoff volume per cell [m³].
           - Q(i,j) = V(i,j) / T

        2) units = "depth_mm"
           - The accumulated raster stores accumulated runoff depth [mm]
             over the contributing area of the cell.
           - The function converts depth [mm] → depth [m], multiplies by
             the cell area [m²] to get volume [m³], then divides by T.

        Parameters
        ----------
        rp : int
            Return period (used for file naming, consistent with other methods).
        event_duration_hours : float
            Duration of the runoff event or model time step, in hours.
            This is used to convert total volume into average discharge:
                T = event_duration_hours * 3600 [s]
        units : {"volume_m3", "depth_mm"}, optional
            Interpretation of the accumulated runoff raster:
            - "volume_m3": accumulated values are in m³ per cell.
            - "depth_mm": accumulated values are in mm (depth) per cell.

        Returns
        -------
        discharge_fp : str
            File path of the discharge raster [m³/s].

        Usage:
            Tc_hours = self.estimate_time_of_concentration(L_m=longest_flow_path_m, S=avg_slope)
            self.calculate_discharge_raster(
                rp=10,
                event_duration_hours=Tc_hours,
                units="volume_m3",  # or "depth_mm", depending on your raster
            )
        """

        # -------------------------------------------------------------------------
        # 0. File paths & early exit
        # -------------------------------------------------------------------------
        runoff_acc_fp = self.get_raster_fp(self.data_dir, rp, "accumulated_runoff")
        discharge_fp = self.get_raster_fp(self.data_dir, rp, "discharge_m3s")

        if os.path.exists(discharge_fp):
            print(f"Discharge raster already exists: {discharge_fp}")
            return discharge_fp

        if not os.path.exists(runoff_acc_fp):
            raise FileNotFoundError(f"Accumulated runoff raster not found: {runoff_acc_fp}")

        if event_duration_hours <= 0:
            raise ValueError("event_duration_hours must be > 0.")

        # -------------------------------------------------------------------------
        # 1. Load accumulated runoff raster
        # -------------------------------------------------------------------------
        acc_raster = RioRaster(runoff_acc_fp)

        # Use masked array to respect NoData
        acc_ma = acc_raster.get_masked_array(1)  # values + mask
        nodata = acc_raster.get_nodata_value()

        # -------------------------------------------------------------------------
        # 2. Convert accumulated values → volume [m³] per cell
        # -------------------------------------------------------------------------
        if units == "volume_m3":
            # Values already represent volume [m³]
            V_m3 = acc_ma.astype(np.float32)

        elif units == "depth_mm":
            # Values are accumulated depth [mm] → convert to volume [m³]
            acc_mm = acc_ma.astype(np.float32)

            # cell area from spatial resolution in meters
            px_x, px_y = acc_raster.get_spatial_resolution(in_meter=True)  # [m], [m]
            cell_area = float(px_x) * float(px_y)  # [m²]

            depth_m = acc_mm / 1000.0  # [mm] → [m]
            V_m3 = depth_m * cell_area  # [m] * [m²] = [m³]

        else:
            raise ValueError("units must be 'volume_m3' or 'depth_mm'.")

        # -------------------------------------------------------------------------
        # 3. Volume → discharge [m³/s]
        # -------------------------------------------------------------------------
        T_sec = float(event_duration_hours) * 3600.0  # [s]
        Q_m3s_ma = V_m3 / T_sec  # masked array [m³/s]

        # Fill masked values with nodata (if defined), otherwise 0 (or keep as is)
        if nodata is not None:
            Q_data = Q_m3s_ma.filled(nodata).astype(np.float32)
        else:
            Q_data = Q_m3s_ma.filled(0.0).astype(np.float32)

        # -------------------------------------------------------------------------
        # 4. Save discharge raster (same grid / CRS as accumulated runoff)
        # -------------------------------------------------------------------------
        discharge_raster = acc_raster.rio_raster_from_array(Q_data)
        discharge_raster.save_to_file(discharge_fp, nodata_value=nodata)

        print(f"Discharge raster saved: {discharge_fp}")
        return discharge_fp

    def extract_stats(self, cat_gdf: GeoDataFrame, rp: int, meteo_dir)->pd.DataFrame:
        params = ["excessive_precipitation", "effective_precipitation", "runoff_volume", "surplus_water"]
        # cat_gdf = AOIUtils.get_catchment_boundary_data(level)
        cat_gdf.to_crs(self.aoi_gdf.crs)

        res = list()
        pr_rp_region_raster, et_rp_region_raster, band_name = MeteoAnalysis.get_meteo_data(meteo_dir,rp, self.scale)

        for index, row in tqdm(cat_gdf.iterrows(),desc="Extracting catchment stats", total=cat_gdf.shape[0]):
            polygon = row[cat_gdf.geometry.name]
            intersects = self.aoi_gdf.intersects(polygon).any()
            if not intersects:
                continue
            info = dict()
            info["hybas_id"] = row['HYBAS_ID']
            info["return_period"] = rp

            aoi_gdf = GeoDataFrame(geometry=[polygon], crs=self.aoi_gdf.crs)

            pr_rp_raster = pr_rp_region_raster.clip_raster(aoi_gdf,in_place=False)
            if pr_rp_raster.empty:
                continue
            pr_summary = BandProcess.get_summary_data(pr_rp_raster.get_data_array_by_band_name([band_name]))
            info["pr_min"] = pr_summary["min"]
            info["pr_max"] = pr_summary["max"]
            info["pr_mean"] = pr_summary["mean"]
            info["pr_std"] = pr_summary["std"]

            et_rp_raster = et_rp_region_raster.clip_raster(aoi_gdf, in_place=False)
            summary_data = None
            if not et_rp_raster.empty:
                summary_data = BandProcess.get_summary_data(et_rp_raster.get_data_array_by_band_name([band_name]))
            info["et_min"] = summary_data["min"] or "-"
            info["et_max"] = summary_data["max"] or "-"
            info["et_mean"] = summary_data["mean"] or "-"
            info["et_std"] = summary_data["std"] or "-"

            for param in params:
                fp = self.get_raster_fp(self.data_dir, rp, param)
                raster = RioRaster(fp)
                raster.clip_raster(aoi_gdf)
                if not raster.empty:
                    summary_data = BandProcess.get_summary_data(raster.get_data_array(1))
                info[f"{param}_min"] = summary_data["min"] or "-"
                info[f"{param}_max"] = summary_data["max"] or "-"
                info[f"{param}_mean"] = summary_data["mean"] or "-"
                info[f"{param}_std"] = summary_data["std"] or "-"
            # print(info)
            res.append(info)

        df = pd.DataFrame(res)
        return df


if __name__ == '__main__':
    rps = (2, 5, 10)
    final_df = pd.DataFrame()
    # catalog = GeoDataCatalog()
    for rp in rps:
        aoi_gdf = GeoDataFrame()
        runoff_accumulation = RunoffAccumulation(aoi_gdf)
        bands = dict()
        runoff_accumulation.calculate_runoff_volume(rp, bands)
        # runoff_accumulation.create_collage(bands, rp)
        df = runoff_accumulation.extract_stats(7, rp)
        final_df = pd.concat([final_df,df])
    data_dir = RunoffAccumulation.get_raster_fp()
    xlsx_fp = os.path.join(data_dir, f"runoff_stats.xlsx")
    final_df.to_excel(xlsx_fp , index=False)
    print("xlsx file saved to {}".format(xlsx_fp))
