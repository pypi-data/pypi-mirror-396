import os
from datetime import datetime
from typing import Literal

import ee
from geopandas import GeoDataFrame

from digitalarzengine.io.gee.gee_image import GEEImage
from digitalarzengine.pipeline.gee_pipeline import GEEPipeline
from settings import MEDIA_DIR


class SoilCapacityAnalysis():
    def __init__(self, gee_pipline: GEEPipeline, aoi_gdv: GeoDataFrame, soil_data_dir: str ):
        self.aoi_gdv = aoi_gdv
        self.gee_pipeline: GEEPipeline = gee_pipline
        # Open Land Map bands and depths
        # Soil depths [in cm] where we have data.
        self.olm_depths = [0, 10, 30, 60, 100, 200]

        # Names of bands associated with reference depths.
        self.olm_bands = ["b" + str(sd) for sd in self.olm_depths]
        self.scale = 250
        self.soil_data_dir = soil_data_dir

    @staticmethod
    def get_soil_prop(param):
        """
        This function returns soil properties image
        param (str): must be one of:
            "sand"     - Sand fraction
            "clay"     - Clay fraction
            "orgc"     - Organic Carbon fraction
        """
        if param == "sand":  # Sand fraction [%w]
            snippet = "OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02"
            # Define the scale factor in accordance with the dataset description.
            scale_factor = 1 * 0.01  # percentage to 0 - 1

        elif param == "clay":  # Clay fraction [%w]
            snippet = "OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02"
            # Define the scale factor in accordance with the dataset description.
            scale_factor = 1 * 0.01  # percentage to 0 - 1

        elif param == "orgc":  # Organic Carbon fraction [g/kg]
            snippet = "OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02"
            # Define the scale factor in accordance with the dataset description.
            scale_factor = 5 * 0.001  # to get kg/kg
        else:
            return print("error")

        # Apply the scale factor to the ee.Image.
        dataset = ee.Image(snippet).multiply(scale_factor)

        return dataset

    def get_soil_data(self):
        if self.gee_pipeline is None:
            self.gee_pipeline = GEEPipeline(self.aoi_gdv)
        # Image associated with the sand content.
        sand = self.get_soil_prop("sand")

        # Image associated with the clay content.
        clay = self.get_soil_prop("clay")

        # Image associated with the organic carbon content.
        orgc = self.get_soil_prop("orgc")

        # Conversion of organic carbon content into organic matter content using the
        # corrective factor known as the Van Bemmelen factor:
        # OM = 1.724 * orgc
        orgm = orgc.multiply(1.724)
        return sand, clay, orgc, orgm

    def calculate_field_capacity_and_wilting_point(self):
        if self.gee_pipeline is None:
            self.gee_pipeline = GEEPipeline(self.aoi_gdv)

        # Initialization of two constant images for wilting point and field capacity.
        wilting_point = ee.Image(0)
        field_capacity = ee.Image(0)
        sand, clay, orgc, orgm = self.get_soil_data()
        # Calculation for each standard depth using a loop.
        for key in self.olm_bands:
            # Getting sand, clay and organic matter at the appropriate depth.
            si = sand.select(key)
            ci = clay.select(key)
            oi = orgm.select(key)

            # Calculation of the wilting point.
            # The theta_1500t parameter is needed for the given depth.
            theta_1500ti = (
                ee.Image(0)
                .expression(
                    "-0.024 * S + 0.487 * C + 0.006 * OM + 0.005 * (S * OM)\
                - 0.013 * (C * OM) + 0.068 * (S * C) + 0.031",
                    {
                        "S": si,
                        "C": ci,
                        "OM": oi,
                    },
                )
                .rename("T1500ti")
            )

            # Final expression for the wilting point.
            wpi = theta_1500ti.expression(
                "T1500ti + ( 0.14 * T1500ti - 0.002)", {"T1500ti": theta_1500ti}
            ).rename("wpi")

            # Add as a new band of the global wilting point ee.Image.
            # Do not forget to cast the type with float().
            wilting_point = wilting_point.addBands(wpi.rename(key).float())

            # Same process for the calculation of the field capacity.
            # The parameter theta_33t is needed for the given depth.
            theta_33ti = (
                ee.Image(0)
                .expression(
                    "-0.251 * S + 0.195 * C + 0.011 * OM +\
                0.006 * (S * OM) - 0.027 * (C * OM)+\
                0.452 * (S * C) + 0.299",
                    {
                        "S": si,
                        "C": ci,
                        "OM": oi,
                    },
                )
                .rename("T33ti")
            )

            # Final expression for the field capacity of the soil.
            fci = theta_33ti.expression(
                "T33ti + (1.283 * T33ti * T33ti - 0.374 * T33ti - 0.015)",
                {"T33ti": theta_33ti.select("T33ti")},
            )

            # Add a new band of the global field capacity ee.Image.
            field_capacity = field_capacity.addBands(fci.rename(key).float())

        sc_fp = self.get_raster_path(self.soil_data_dir, 'field_capacity')
        if not os.path.exists(sc_fp):
            GEEImage(field_capacity).download_image(sc_fp, self.gee_pipeline.region, self.scale,
                                                    save_metadata=False)
        sc_fp = self.get_raster_path(self.soil_data_dir,'wilting_point')
        if not os.path.exists(sc_fp):
            GEEImage(wilting_point).download_image(sc_fp, self.gee_pipeline.region, self.scale,
                                                   save_metadata=False)

        return field_capacity, wilting_point

    def calculate_soil_capacity_per_depth(self):
        if self.gee_pipeline is None:
            self.gee_pipeline = GEEPipeline(self.aoi_gdv)

        field_capacity, wilting_point = self.calculate_field_capacity_and_wilting_point()
        soil_capacity_per_depth = field_capacity.subtract(wilting_point)  # Use the subtract() method
        # Select bands corresponding to the depths
        bands_to_sum = [f'b{depth}' for depth in self.olm_depths]
        soil_capacity_per_depth = soil_capacity_per_depth.select(bands_to_sum)
        sc_fp = self.get_raster_path(self.soil_data_dir, 'soil_capacity_per_depth')
        if not os.path.exists(sc_fp):
            GEEImage(soil_capacity_per_depth).download_image(sc_fp, self.gee_pipeline.region, self.scale,
                                                             save_metadata=False)

        return soil_capacity_per_depth

    def calculate_total_soil_capacity(self):
        if self.gee_pipeline is None:
            self.gee_pipeline = GEEPipeline(self.aoi_gdv)
        soil_capacity_per_depth = self.calculate_soil_capacity_per_depth()
        # Sum across depths to get total soil capacity
        total_soil_capacity = soil_capacity_per_depth.reduce(ee.Reducer.sum()).rename('total_soil_capacity')
        sc_fp = self.get_raster_path(self.soil_data_dir, 'total_soil_capacity')
        if not os.path.exists(sc_fp):
            GEEImage(total_soil_capacity).download_image(sc_fp, self.gee_pipeline.region, self.scale,
                                                         save_metadata=False)
        return total_soil_capacity

    @staticmethod
    def get_band_name(depth):
        olm_depths = [0, 10, 30, 60, 100, 200]

        # Names of bands associated with reference depths.
        olm_bands = ["b" + str(sd) for sd in olm_depths]
        if depth in olm_bands:
            return "b" + str(depth)
        raise ValueError(f"depth {depth} doesn't exists")


    @staticmethod
    def get_raster_path(soil_data_dir, param: Literal["total_soil_capacity", "soil_capacity_per_depth", "field_capacity", "wilting_point"]):
        # soil_data_dir = os.path.join(MEDIA_DIR, 'soil_data', 'gee')
        os.makedirs(soil_data_dir, exist_ok=True)

        if param == 'total_soil_capacity':
            sc_fp = os.path.join(soil_data_dir, 'total_soil_capacity.tif')
        elif param == 'soil_capacity_per_depth':
            sc_fp = os.path.join(soil_data_dir, 'soil_capacity_per_depth.tif')
        elif param == 'field_capacity':
            sc_fp = os.path.join(soil_data_dir, 'field_capacity.tif')
        elif param == 'wilting_point':
            sc_fp = os.path.join(soil_data_dir, 'wilting_point.tif')
        else:
            raise Exception('soil surface param doesnt exist')
        return sc_fp


if __name__ == "__main__":
    # start_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
    # end_date = datetime.strptime('2024-12-31', '%Y-%m-%d')
    # aoi_gdv = AOIUtils.get_aoi()
    aoi_gdv = GeoDataFrame()
    gee_pipeline = GEEPipeline(aoi_gdv)
    soil_analysis = SoilCapacityAnalysis(gee_pipeline, aoi_gdv)
    soil_analysis.calculate_total_soil_capacity()
