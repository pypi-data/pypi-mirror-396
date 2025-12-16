import os
from typing import Literal, List

import ee
import pandas as pd
from geopandas import GeoDataFrame

from digitalarzengine.io.gee.gee_image import GEEImage
from digitalarzengine.io.rio_raster import RioRaster
from digitalarzengine.pipeline.gee_pipeline import GEEPipeline
from digitalarzengine.processing.raster.rio_process import RioProcess
from digitalarzengine.utils.singletons import da_logger

Stats = Literal["max", "mean", "total"]

class MeteoAnalysis:
    def __init__(self, gee_pipeline: GEEPipeline,  start_date, end_date, data_dir):
        self.start_date = start_date
        self.end_date = end_date
        self.gee_pipeline: GEEPipeline = gee_pipeline
        self.meteo_data_dir = data_dir
        os.makedirs(self.meteo_data_dir, exist_ok=True)
        self.rps =  (2, 5, 10, 25, 50, 100)

    @staticmethod
    def get_precipitation_surface(start_date, end_date, region):
        pr = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterDate(start_date, end_date) \
            .filterBounds(region).select('precipitation')
        return pr

    @staticmethod
    def get_et_surface(start_date, end_date, region):
        et = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001") \
            .filterBounds(region) \
            .filterDate(start_date, end_date) \
            .select('Evap_tavg')
        return et

    @staticmethod
    def calculate_annual_stats_meteo(year, meteo_img_coll, stats):
        """Extracts max, min (ignoring zero), mean, both types of standard deviation, and number of dry days for a given year."""
        year_start = ee.Date.fromYMD(year, 1, 1)
        year_end = ee.Date.fromYMD(year, 12, 31)

        # Filter Data
        meteo_annual_data = meteo_img_coll.filterDate(year_start, year_end)
        if stats == 'mean':
            annual_meteo_image = meteo_annual_data.mean().rename(f"{year}")
        elif stats == 'min':
            annual_meteo_image = meteo_annual_data.min().rename(f"{year}")
        elif stats == 'total':
            annual_meteo_image = meteo_annual_data.sum().rename(f"{year}")
        else:
            annual_meteo_image = meteo_annual_data.max().rename(f"{year}")  # .rename(['max_precip'])

        return annual_meteo_image

    def get_annual_combined_image(self, meteo_img_coll, start_year, end_year, stats):
        """
        Function to calculate annual maximum values for a given meteorological parameter
        and return a combined image with each year's max as a band.
        """
        # Generate annual maximum precipitation images
        years = list(range(start_year, end_year + 1))
        annual_images_list = [self.calculate_annual_stats_meteo(year, meteo_img_coll, stats) for year in years]

        # Combine annual maximum images into a single image with bands
        combined_image = annual_images_list[0]
        for i in range(1, len(annual_images_list)):
            combined_image = combined_image.addBands(annual_images_list[i])

        return combined_image

    @staticmethod
    def get_df_from_combined_image(combined_image, region, scale, xlsx_fp):
        """
        Function to extract statistics from combined image and return a DataFrame.
        Saves the DataFrame to an Excel file if not already saved.
        """
        if not os.path.exists(xlsx_fp):
            info = GEEImage.get_band_stats(combined_image, region, scale)
            df = pd.DataFrame(info).T  # Transpose to get years as rows
            df.index.name = 'Year'  # Set index name to 'Year'
            if xlsx_fp is not None:
                df.to_excel(xlsx_fp)
        else:
            df = pd.read_excel(xlsx_fp, index_col=0)
        return df

    # def aggregated_precipitation(self, scale, cat_gdv: GeoDataFrame):
    #     fp = os.path.join(self.meteo_data_dir, f'pr_aggregated_from_{self.start_date.year}_to_{self.end_date.year}.tif')
    #     # cat_gdv = AOIUtils.get_catchment_aoi()
    #     if not os.path.exists(fp):
    #         if self.gee_pipeline is None:
    #             self.gee_pipeline = GEEPipeline(cat_gdv)
    #         pr = self.get_precipitation_surface(self.start_date, self.end_date, self.gee_pipeline.region.get_aoi())
    #         agg_img = pr.sum()
    #         GEEImage(agg_img).download_image(fp, self.gee_pipeline.region, scale, save_metadata=False)
    #
    #     raster = RioRaster(fp)
    #     raster = raster.clip_raster(cat_gdv)
    #
    #     cat_level_7_gdv = AOIUtils.get_catchment_boundary_data(level=7)
    #     cat_level_7_gdv = GPDVector.multipolygon_to_polygon(cat_level_7_gdv)
    #     cat_level_7_gdv = cat_level_7_gdv.spatial_join(input_gdf=cat_gdv, predicate='within')
    #
    #     output_fp = os.path.join(self.meteo_data_dir, 'plots',
    #                              f'pr_aggregated_from_{self.start_date.year}_to_{self.end_date.year}.jpg')
    #     os.makedirs(os.path.dirname(output_fp), exist_ok=True)
    #     RioProcess.create_collage_images(raster, f'Aggregated Precipitation(mm)  Surface', output_fp, no_of_rows=1,
    #                                      cmap='Blues',
    #                                      gdf=cat_level_7_gdv.get_gdf())

    @staticmethod
    def get_raster_fp(media_dir, param: Literal["pr", "et"], is_return_periods: bool = True,
                      stat: Stats= None):
        if os.path.basename(media_dir) == "meteo_data":
            meteo_data_dir = media_dir
        else:
            meteo_data_dir = os.path.join(media_dir, "meteo_data")
        start_year = 2000
        end_year = 2024
        # fp = os.path.join(self.meteo_data_dir, f'{param}_annual_{stat}_{start_year}-{end_year}.tif')

        if is_return_periods:
            fp = os.path.join(meteo_data_dir, f'{param}_return_periods.tif')
        else:
            fp = os.path.join(meteo_data_dir, f'{param}_annual_{stat}_{start_year}-{end_year}.tif')
        return fp

    @staticmethod
    def get_meteo_data(media_dir, rp, scale=None) -> (RioRaster, RioRaster, str):
        band_name = f'Return Period {rp} years'
        pr_rp_fp = MeteoAnalysis.get_raster_fp(media_dir,"pr", is_return_periods=True)
        pr_rp_raster = RioRaster(pr_rp_fp)
        if scale is not None:
            pr_rp_raster.resample(scale,resampling="nearest")
        # pr_rp_raster.clip_raster(self.aoi_gdf)
        # pr_data = pr_rp_raster.get_data_array(1, convert_no_data_2_nan=False)

        et_rp_fp = MeteoAnalysis.get_raster_fp(media_dir,"et", is_return_periods=True)
        et_rp_raster = RioRaster(et_rp_fp)
        if scale is not None:
            et_rp_raster.resample(scale, resampling="nearest")
        # et_rp_raster.clip_raster(self.aoi_gdf)
        # et_data = et_rp_raster.get_data_array(1, convert_no_data_2_nan=False)
        return pr_rp_raster, et_rp_raster, band_name

    def set_rps(self, rps):
        self.rps = rps

    def get_rps(self):
        return self.rps

    def process_annual_images(self, param, aoi_gdv: GeoDataFrame, scale, return_periods=None) -> str:
        start_year = self.start_date.year
        end_year = self.end_date.year
        stats: List[Stats] = ['max', 'mean', 'total']
        self.rps = return_periods if return_periods is not None else self.rps
        if param == 'et':
            meteo_name = 'ET'
            cbar = 'BrBG_r'
            units = 'mm'
        else:
            meteo_name = 'Precipitation'
            cbar = 'Blues'
            units = 'mm'
        for stat in stats:
            # fp = os.path.join(self.meteo_data_dir, f'{param}_annual_{stat}_{start_year}-{end_year}.tif')
            fp = self.get_raster_fp(self.meteo_data_dir, param, is_return_periods=False, stat=stat)
            if not os.path.exists(fp):
                if self.gee_pipeline is None:
                    self.gee_pipeline = GEEPipeline(aoi_gdv)

                if param == 'et':
                    meteo_img_coll = self.get_et_surface(self.start_date, self.end_date,
                                                         self.gee_pipeline.region.get_aoi())
                else:
                    meteo_img_coll = self.get_precipitation_surface(self.start_date, self.end_date,
                                                                    self.gee_pipeline.region.get_aoi())

                meteo_combined_image = self.get_annual_combined_image(meteo_img_coll, start_year, end_year, stat)
                if param == 'et':
                    meteo_combined_image = meteo_combined_image.multiply(86400)
                meteo_combined_image = meteo_combined_image.clip(self.gee_pipeline.region.get_aoi())

                GEEImage(meteo_combined_image).download_image(fp, self.gee_pipeline.region, scale, save_metadata=False)

            raster = RioRaster(fp)
            # cat_gdv = AOIUtils.get_catchment_aoi()
            raster = raster.clip_raster(aoi_gdv)

            # cat_level_7_gdv = AOIUtils.get_catchment_boundary_data(level=7)
            # cat_level_7_gdv = GPDVector.multipolygon_to_polygon(cat_level_7_gdv)
            # cat_level_7_gdv = cat_level_7_gdv.spatial_join(input_gdf=aoi_gdv, predicate='within')

            # output_fp = os.path.join(self.meteo_data_dir, 'plots', f'{param}_annual_{stat}_{start_year}-{end_year}.jpg')
            # os.makedirs(os.path.dirname(output_fp), exist_ok=True)
            # RioProcess.create_collage_images(raster, f'{stat} {meteo_name} ({units})  Surface', output_fp, no_of_rows=4,
            #                                  cmap=cbar,
            #                                  gdf=cat_level_7_gdv.get_gdf())

            # output_fp = os.path.join(self.meteo_data_dir, f'{param}_return_periods.tif')
            output_fp = self.get_raster_fp(self.meteo_data_dir, param, is_return_periods=True, stat=stat)
            if not os.path.exists(output_fp):
                da_logger.debug(f"calculating return periods of {stat} stasts")
                RioProcess.get_return_period_surfaces(raster, output_fp, return_periods=self.rps)

            # rp_raster = RioRaster(output_fp)
            output_fp = os.path.join(self.meteo_data_dir, 'plots', f'{param}_return_periods.jpg')
            os.makedirs(os.path.dirname(output_fp), exist_ok=True)

            # RioProcess.create_collage_images(rp_raster, f'{meteo_name} ({units})', output_fp, no_of_rows=3, cmap=cbar,
            #                                  gdf=cat_level_7_gdv.get_gdf())
            return output_fp


# if __name__ == "__main__":
#     # Define the time period
#
#     catalog = GeoDataCatalog()
#     start_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
#     end_date = datetime.strptime('2025-12-31', '%Y-%m-%d')
#     # cat_aoi_gdv = AOIUtils.get_catchment_governorate_combined_aoi()
#     cat_aoi_gdv = catalog.get_combined_aoi()
#     data_dir = GeoDataCatalog.get_meteo_data_dir()
#     gee_pipeline = init_gee_pipeline(cat_aoi_gdv)
#     meteo_analysis = MeteoAnalysis(gee_pipeline,start_date, end_date, data_dir)
#     scale = 1000
#     da_logger.debug("processing annual precipitation")
#     meteo_analysis.process_annual_images('pr', cat_aoi_gdv,  scale)
#     da_logger.debug("processing annual evapotranspiration")
#     meteo_analysis.process_annual_images('et', cat_aoi_gdv, scale)
#     meteo_analysis.aggregated_precipitation(scale)
