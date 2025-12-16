
import os
import traceback
from pathlib import Path
from typing import Optional

import numpy as np
import rasterio
from geopandas import GeoDataFrame
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from rasterio import DatasetReader, Env
from rasterio.merge import merge
from scipy.stats import genextreme


from digitalarzengine.io.file_io import FileIO
from digitalarzengine.io.rio_raster import RioRaster
from typing import  Union, List

from digitalarzengine.utils.singletons import da_logger

import folium
import matplotlib.cm as cm
import matplotlib.colors as colors
import base64
import io
import webbrowser
import tempfile

class RioProcess:

    @staticmethod
    def read_raster_ds(img_folder: str):
        ds_files: [DatasetReader] = []
        path = Path(img_folder)
        issues_folder = os.path.join(img_folder, "issue_in_files")
        os.makedirs(issues_folder,exist_ok=True)
        # count = FileIO.get_file_count(img_folder)
        # test = [str(p) for p in path.iterdir() if p.suffix == ".tif"]
        # ds_files = []
        for p in path.iterdir():
            if p.suffix == ".tif":
                try:
                    ds_files.append(RioRaster(str(p)).get_dataset())
                except Exception as e:
                    traceback.print_exc()
                    print(str(e))
                    FileIO.mvFile(str(p), issues_folder)
        return ds_files

    @classmethod
    def mosaic_images(cls, img_folder: str = None, ds_files: [DatasetReader] = (),  ext="tif") -> RioRaster:
        is_limit_changed = False
        if img_folder is not None:
            # count = FileIO.get_file_count(img_folder)
            count = FileIO.get_file_count(img_folder)
            # get file reading limits
            soft, hard = FileIO.get_file_reading_limit()
            # print("soft", soft, "hard", hard)
            if count > soft:
                if count * 2 < hard:
                    """
                    default limit is  soft: 12544 hard:9223372036854775807
                    """
                    FileIO.set_file_reading_limit(count * 2)

                    is_limit_changed = True
                else:
                    raise IOError(f"you are trying to read {count} files. Cannot read more than {hard} files.")
            ds_files = cls.read_raster_ds(img_folder)
            # problem_files.append(str(p))
        if len(ds_files) > 0:
            with Env(CHECK_DISK_FREE_SPACE=False):
                mosaic, out_trans = merge(ds_files)
                crs = ds_files[0].crs
                raster = RioRaster.raster_from_array(mosaic, crs=crs, g_transform=out_trans)
            if is_limit_changed:
                FileIO.set_file_reading_limit(soft)
            return raster

    @staticmethod
    def get_return_period_surfaces(raster: RioRaster, output_path, return_periods=(2, 5, 10, 25, 50, 100)):

        data = raster.get_data_array()
        no_datavalue = raster.get_nodata_value()

        # Prepare output array (bands = number of return periods, height, width)
        return_level_raster = np.full((len(return_periods), data.shape[1], data.shape[2]), no_datavalue,
                                      dtype=np.float32)

        # GEV Fit for each pixel
        for i in range(data.shape[1]):  # Loop over rows
            for j in range(data.shape[2]):  # Loop over columns
                pixel_values = data[:, i, j]  # Extract yearly max precipitation for this pixel

                # Exclude nodata values
                valid_values = pixel_values[pixel_values != no_datavalue]

                if valid_values.size == 0 or np.all(np.isnan(valid_values)):  # Skip if no valid values
                    continue

                # Fit GEV distribution (shape, location, scale)
                shape, loc, scale = genextreme.fit(valid_values)

                # Compute return level for each return period
                for band_idx, rp in enumerate(return_periods):
                    return_level_raster[band_idx, i, j] = genextreme.ppf(1 - 1 / rp, shape, loc=loc, scale=scale)

        # Save the single raster with multiple bands

        profile = raster.get_profile().copy()
        profile.update(dtype=rasterio.float32, count=len(return_periods),
                       nodata=no_datavalue)  # Ensure nodata value is set

        with rasterio.open(output_path, "w", **profile) as dst:
            for band_idx, rp in enumerate(return_periods):
                dst.write(return_level_raster[band_idx], band_idx + 1)  # Write each return period to a band
                dst.set_band_description(band_idx + 1, f"Return Period {rp} years")  # Set band name

            dst.update_tags(return_periods=str(return_periods))  # Store metadata

        print(f"Saved: {output_path}")

    @staticmethod
    def _extent_from_transform(transform, width, height):
        xmin = transform.c
        ymax = transform.f
        xmax = xmin + transform.a * width
        ymin = ymax + transform.e * height
        # normalize so (xmin, xmax, ymin, ymax)
        return (min(xmin, xmax), max(xmin, xmax), min(ymin, ymax), max(ymin, ymax))

    from typing import Optional, Sequence, Union

    @staticmethod
    def create_collage_images(
            raster: RioRaster,
            title: str,
            output_fp: str,
            no_of_rows: int = 2,
            cmap: str = 'Blues',
            edgecolor: str = 'green',
            linewidth: float = 1.0,
            gdf: Optional[GeoDataFrame] = None,
            sub_titles: Optional[Sequence[str]] = None,
            vmin: Optional[Union[float, str]] = None,
            vmax: Optional[Union[float, str]] = None,
    ):
        """
        Create a multi-band image collage for a raster.

        This function visualizes each band of a raster in a grid layout. Bands are
        rendered using a shared colormap, optional vector boundaries, and per-band
        color limits (absolute or percentile-based).

        Parameters
        ----------
        raster : RioRaster
            Raster object providing bands, metadata, transform, CRS, and nodata.
        title : str
            Main title prefix applied to each subplot (band name appended).
        output_fp : str
            Destination file path for the saved image (PNG, JPG, etc.).
        no_of_rows : int, default=2
            Number of rows in the figure grid. Columns are computed automatically.
        cmap : str, default='Blues'
            Matplotlib colormap name.
        edgecolor : str, default='green'
            Boundary color for overlaying vector geometries (if provided).
        linewidth : float, default=1.0
            Line thickness for vector boundaries.
        gdf : GeoDataFrame, optional
            Vector layer to plot on top of each band. Reprojected if CRS differs.
        sub_titles : Sequence[str], optional
            Custom subtitles for each band. Falls back to raster band names.
        vmin : float or str, optional
            Lower limit for color scaling. Can be:
                - a float (absolute value), e.g. 0
                - a percentile string, e.g. "5%" or "2.5%"
            Percentiles are computed **per band** ignoring nodata.
        vmax : float or str, optional
            Upper limit for color scaling. Same rules as `vmin`.

        Notes
        -----
        - If both `vmin` and `vmax` are None, each band is autoscaled by its own min/max.
        - Percentile inputs like "90%" use `numpy.nanpercentile` internally.
        - Nodata values are converted to `NaN` and displayed with the colormap's
          "bad" color (white).
        - Subplots exceeding the number of bands are hidden.

        Returns
        -------
        str
            The same `output_fp` provided, after saving the figure.

        Examples
        --------
        # Absolute color limits
        create_collage_images(raster, "My Raster", "out.png", vmin=0, vmax=500)

        # Percentile stretch (per band)
        create_collage_images(raster, "My Raster", "out.png", vmin="2%", vmax="98%")

        # Mixed: fixed lower bound + percentile upper bound
        create_collage_images(raster, "My Raster", "out.png", vmin=0, vmax="99%")
        """

        def _resolve_limit(limit: Optional[Union[float, str]], band: np.ndarray):
            """
            - If limit is None → None
            - If float/int → use as absolute value
            - If string ending with '%' (e.g. '90%') → use that percentile of this band
            """
            if limit is None:
                return None

            # Percentile case like "90%" or "2.5%"
            if isinstance(limit, str) and limit.endswith('%'):
                try:
                    p = float(limit[:-1])
                except ValueError:
                    raise ValueError(f"Invalid percentile string for vmin/vmax: {limit!r}")
                return float(np.nanpercentile(band, p))

            # Absolute numeric value
            return float(limit)

        sub_titles = [] if sub_titles is None else list(sub_titles)
        no_of_bands = raster.get_spectral_resolution()
        no_of_cols = int(np.ceil(no_of_bands / no_of_rows))

        fig, axes = plt.subplots(
            no_of_rows,
            no_of_cols,
            figsize=(5 * no_of_cols, 4 * no_of_rows),
            constrained_layout=True
        )
        if isinstance(axes, np.ndarray):
            axes = axes.ravel()
        else:
            axes = np.array([axes])

        raster_crs = raster.get_crs()
        transform = raster.get_geo_transform()
        nodata_value = raster.get_nodata_value()

        if gdf is not None and not gdf.empty and getattr(gdf, "crs", None) is not None:
            if gdf.crs != raster_crs:
                gdf = gdf.to_crs(raster_crs, inplace=False)

        cmap_obj = plt.get_cmap(cmap).copy()
        cmap_obj.set_bad(color='white')

        for i in range(no_of_bands):
            band = raster.get_data_array(i + 1).astype(float)

            if nodata_value is not None:
                band[band == nodata_value] = np.nan

            band_name = raster.get_band_name(i + 1)
            da_logger.debug(f"Working on band name: {band_name}")


            h, w = band.shape
            extent = RioProcess._extent_from_transform(transform, w, h)

            # 👇 compute per-band limits (absolute or percentile)
            vmin_resolved = _resolve_limit(vmin, band)
            vmax_resolved = _resolve_limit(vmax, band)
            # min_val = np.nanmin(band)
            # max_val = np.nanmax(band)
            da_logger.debug(f"Band min value: {vmin_resolved} Band max value: {vmax_resolved}")

            ax = axes[i]
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.1)

            # 👇 use vmin/vmax directly so colorbar matches the scale
            im = ax.imshow(
                band,
                cmap=cmap_obj,
                interpolation='nearest',
                extent=extent,
                origin='upper',
                vmin=vmin_resolved,
                vmax=vmax_resolved,
            )

            if gdf is not None and not gdf.empty:
                gdf.boundary.plot(ax=ax, edgecolor=edgecolor, linewidth=linewidth)

            band_title = (
                sub_titles[i]
                if (sub_titles and i < len(sub_titles))
                else raster.get_band_name(i + 1)
            )
            ax.set_title(f'{title} – {band_title}' if title else band_title)
            ax.set_xticks([])
            ax.set_yticks([])

            fig.colorbar(im, cax=cax)

        for j in range(no_of_bands, len(axes)):
            axes[j].set_visible(False)

        fig.savefig(output_fp, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return output_fp

    # @staticmethod
    # def create_collage(self, bands, rp, aoi_gdf: GeoDataFrame):
    #     # band_data = np.asarray(list(bands.values()))
    #     height, width = bands[f"Runoff_volume_return_period_{rp}_year"].shape
    #     band_data = []
    #     sub_titles = []
    #     for value, data in bands.items():
    #         data = cv2.resize(data, (width, height), interpolation=cv2.INTER_LINEAR)
    #         print(value, data.shape)
    #         band_data.append(data)
    #         sub_titles.append(value.replace("_", " "))
    #     band_data = np.asarray(band_data)
    #     print(band_data.shape)
    #     fp = self.get_raster_fp(rp, "surplus_water")
    #
    #     # cat_level_7_gdv = AOIUtils.get_catchment_boundary_data(level=7)
    #     # cat_level_7_gdv = GPDVector.multipolygon_to_polygon(cat_level_7_gdv)
    #     # cat_level_7_gdv = cat_level_7_gdv.spatial_join(input_gdf=self.aoi_gdf, predicate='within')
    #
    #     ref_raster = RioRaster(fp)
    #     raster = ref_raster.rio_raster_from_array(band_data)
    #     out_collage = os.path.join(os.path.dirname(fp), f"collage/runoff_analysis_{rp}_rp.jpg")
    #     os.makedirs(os.path.dirname(out_collage), exist_ok=True)
    #     RioProcess.create_collage_images(raster, "", out_collage, no_of_rows=2, gdf=cat_level_7_gdv,
    #                                      sub_titles=sub_titles)
    #     print("collage created at ", out_collage)

    @staticmethod
    def stack_rasters_in_memory(
            sources: Sequence[Union[RioRaster, np.ndarray]],
            reference: RioRaster = None,
            band_names: List[str] = None,
            resampling: str = "nearest"
    ) -> RioRaster:
        """
        Align and stack sources into a new multiband *in-memory* RioRaster.
        - Forces float32 (NaN-safe).
        - Cleans meta so there is no weird scaling.
        Nothing is written to disk.
        """

        def _as_raster_like(ref: RioRaster, x):
            if isinstance(x, RioRaster):
                return x
            arr = x if x.ndim in (2, 3) else np.asarray(x)
            return RioRaster.raster_from_array(
                img_arr=arr,
                crs=ref.get_crs(),
                g_transform=ref.get_geo_transform(),
                nodata_value=ref.get_nodata_value()
            )

        def _ensure_aligned(src: RioRaster, ref: RioRaster, resampling="nearest") -> RioRaster:
            r = src
            if r.get_crs() != ref.get_crs():
                r = r.reproject_to(ref.get_crs(), in_place=False, resampling=resampling)
            r = r.pad_raster(ref, in_place=False) or r
            return r

        # def _ensure_aligned(src: RioRaster, ref: RioRaster, resampling: str = "nearest") -> RioRaster:
        #     r = src
        #
        #     # 0) Make sure internal data is float32 so NaNs survive
        #     # Only if you have such a method; otherwise you can skip or handle after read.
        #     if hasattr(r, "astype"):
        #         r = r.astype(np.float32, in_place=False) or r
        #
        #     # 1) Reproject to reference CRS if needed
        #     if r.get_crs() != ref.get_crs():
        #         # If reproject_to supports dst_nodata, pass a float nodata
        #         ref_nodata = ref.get_nodata_value()
        #         dst_nodata = ref_nodata if ref_nodata is not None else np.nan
        #
        #         r = r.reproject_to(
        #             ref.get_crs(),
        #             in_place=False,
        #             resampling=resampling,
        #             dst_nodata=dst_nodata  # <- important if supported
        #         )
        #
        #     # 2) Pad to reference extent/grid if needed.
        #     # Make sure padding uses NaN, not 0.
        #     pad_kwargs = {}
        #     # if your pad_raster supports fill_value or similar, set it:
        #     # pad_kwargs["fill_value"] = np.nan
        #
        #     padded = r.pad_raster(ref, in_place=False, **pad_kwargs)
        #
        #     if padded is not None:
        #         r = padded
        #
        #     return r

        def _read_as_bands(r: RioRaster) -> np.ndarray:
            arr = r.get_data_array()
            if arr.ndim == 2:
                arr = arr[np.newaxis, ...]
            return arr

        if not sources:
            raise ValueError("No sources provided.")

        # Use given reference, or turn first source into a raster
        ref_r = reference or _as_raster_like(sources[0], sources[0])

        # 1) Convert → align → read
        # ref_r = reference if reference is not None else _as_raster_like(sources[0], sources[0])
        arrays = []
        for s in sources:
            r = _as_raster_like(ref_r, s)
            r = _ensure_aligned(r, ref_r, resampling=resampling)
            arrays.append(_read_as_bands(r))

        # 2) Force everything to float32 (NaN-safe)
        arrays = [np.asarray(a, dtype=np.float32) for a in arrays]
        stacked = np.concatenate(arrays, axis=0)  # (B, H, W)

        # Debug: verify the values are still OK here
        # print("stacked dtype:", stacked.dtype, "max:", np.nanmax(stacked))

        # 3) Build a clean metadata profile
        meta = ref_r.get_meta().copy()

        # Remove keys that can mess with scaling / size
        for k in ("dtype", "count", "height", "width", "nodata",
                  "transform", "crs", "scales", "offsets"):
            meta.pop(k, None)

        ref_nodata = ref_r.get_nodata_value()
        nodata = ref_nodata if ref_nodata is not None else np.nan  # keep float nodata

        meta.update({
            "count": stacked.shape[0],
            "dtype": "float32",  # valid rasterio dtype string
            "height": stacked.shape[1],
            "width": stacked.shape[2],
            "transform": ref_r.get_geo_transform(),
            "crs": ref_r.get_crs(),
            "nodata": nodata,
        })

        ds_reader = RioRaster.rio_dataset_from_array(stacked, meta, band_names or [])
        return RioRaster(ds_reader)

    @staticmethod
    def view_raster_on_folium(
        raster,
        tiles: str = "OpenStreetMap",
        gdf: GeoDataFrame = None,
        show_legend: bool = True,
        legend_title: str = "Raster Values",
        colormap="viridis",
        vmin=None,
        vmax=None,
        opacity: float = 0.7,
        output_html: str = None,
    ):
        """
        Display a single-band raster on an interactive Folium web map.

        Parameters
        ----------
        raster : RioRaster
            Raster object containing at least one band.
        tiles : str, optional (default="OpenStreetMap")
            Basemap tile provider used in the Folium map.

            Supported built-in tile names include:
                - "OpenStreetMap"                  → Standard OSM basemap
                - "Stamen Terrain"                 → Terrain / relief style
                - "Stamen Toner"                   → High-contrast B&W map
                - "Stamen Watercolor"              → Artistic watercolor map
                - "CartoDB positron"               → Clean light basemap
                - "CartoDB dark_matter"            → Dark background basemap
                - "Wikimedia"                      → Wikimedia OSM tiles

            You may also use **custom XYZ tile providers** using `folium.TileLayer`, e.g.:

            - Google Maps (roadmap)
              URL: "https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}"

            - Google Satellite
              URL: "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"

            - Esri World Imagery (satellite)
              URL: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

            - Esri Topographic
              URL: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"

            Notes
            -----
            • XYZ tile URLs must include placeholders: {x}, {y}, {z}.
            • Google and ESRI tiles may impose use restrictions.
            • Tile choice does not affect raster computation — only the visual background.

        gdf : GeoDataFrame, optional
            A vector boundary (single GeoDataFrame) to overlay on the map.
        show_legend : bool, default=True
            Whether to display a dynamic legend matching raster colormap.
        legend_title : str, optional
        colormap : str or callable, default="viridis"
            Name of matplotlib colormap.
        vmin, vmax : float, optional
            Color range limits. If None → computed from raster.
        opacity : float, default=0.7
            Opacity of raster overlay.
        output_html : str, optional
            If provided, the map is saved to an HTML file.

        Returns
        -------
        folium.Map
            Folium map object with raster overlay.

        Usage:
            r = RioRaster("tests/data/terrain/merit_dem.tif")
            aoi_gdf = your_aoi_gdf   # e.g. catchment boundary, villages, etc.

            m = RioProcess.view_raster_on_folium(
                raster=r,
                band=1,
                cmap="terrain",
                opacity=0.8,
                show_legend=True,
                legend_label="Elevation (m)",
                gdf=aoi_gdf,
                edgecolor="red",
                linewidth=1.0,
            )

            m.save("dem_with_aoi.html")

        """


        # ---------------------------------------------
        # Read raster data
        # ---------------------------------------------
        arr = raster.get_data_array(1).astype(float)
        nodata = raster.get_nodata_value()
        arr[arr == nodata] = np.nan

        vmin = np.nanmin(arr) if vmin is None else vmin
        vmax = np.nanmax(arr) if vmax is None else vmax

        cmap = cm.get_cmap(colormap)
        norm = colors.Normalize(vmin=vmin, vmax=vmax)

        rgba_img = cmap(norm(arr))
        rgba_img = (rgba_img * 255).astype("uint8")

        # encode PNG
        buf = io.BytesIO()
        plt_img = rasterio.plot.show
        import matplotlib.pyplot as plt

        plt.imsave(buf, rgba_img, format="png")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")

        # bounding box
        transform = raster.get_geo_transform()
        h, w = arr.shape
        xmin = transform.c
        ymax = transform.f
        xmax = xmin + transform.a * w
        ymin = ymax + transform.e * h

        bounds = [[ymin, xmin], [ymax, xmax]]

        # ---------------------------------------------
        # Create Folium map centered on raster
        # ---------------------------------------------
        center_lat = (ymin + ymax) / 2
        center_lon = (xmin + xmax) / 2

        m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles=tiles)

        # ---------------------------------------------
        # Add raster overlay
        # ---------------------------------------------
        folium.raster_layers.ImageOverlay(
            image="data:image/png;base64," + img_b64,
            bounds=bounds,
            opacity=opacity,
            name="Raster",
        ).add_to(m)

        # ---------------------------------------------
        # Add vector overlay if provided
        # ---------------------------------------------
        if gdf is not None and not gdf.empty:
            if gdf.crs != raster.get_crs():
                gdf = gdf.to_crs(raster.get_crs())

            folium.GeoJson(
                gdf,
                name="Vector Overlay",
                style_function=lambda x: {
                    "color": "green",
                    "weight": 2,
                    "fillOpacity": 0,
                },
            ).add_to(m)

        # ---------------------------------------------
        # Add legend
        # ---------------------------------------------
        if show_legend:
            gradient = "".join(
                [
                    f'<div style="background: rgb{tuple(int(c*255) for c in cmap(i/100)[:3])}; width: 100%; height: 3px"></div>'
                    for i in range(100)
                ]
            )

            legend_html = f"""
            <div style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: white;
                padding: 10px;
                border: 2px solid grey;
                z-index: 999999;
                font-size: 12px;
            ">
                <b>{legend_title}</b><br>
                {gradient}
                <div style="display:flex; justify-content:space-between;">
                    <span>{vmin:.2f}</span>
                    <span>{vmax:.2f}</span>
                </div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

        folium.LayerControl().add_to(m)

        if output_html:
            m.save(output_html)

        return m

    @staticmethod
    def open_folium_in_browser(folium_map):
        """
        Open a Folium map in the default web browser without manually saving a file.
        Usage:
            m = RioProcess.view_raster_on_folium(raster)
            open_folium_in_browser(m)
        """
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        folium_map.save(tmp.name)
        webbrowser.open(tmp.name)