import os

import ee
from geopandas import GeoDataFrame


from digitalarzengine.io.gee.gee_image import GEEImage
from digitalarzengine.pipeline.gee_pipeline import GEEPipeline
from digitalarzengine.utils.singletons import da_logger
from settings import APP_DATA_DIR


class RunoffCoefficient:
    def __init__(self, gee_pipline: GEEPipeline, data_dir: str, scale: float = 100):
        self.gee_pipline = gee_pipline
        self.scale = scale
        self.data_dir = data_dir

    @staticmethod
    def get_landcover_image(region):
        # Load OpenLandMap land cover (e.g., ESA CCI land cover)
        land_cover = ee.ImageCollection("ESA/WorldCover/v200") \
            .sort('system:time_start', False) \
            .first() \
            .clip(region)
        return land_cover

    @staticmethod
    def get_soil_texture(region):
        # Load OpenLandMap soil texture (clay, sand, silt percentages)
        soil_texture = ee.Image("OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02").clip(region)
        return soil_texture

    @staticmethod
    def get_slop_map(region):
        dem = ee.Image("MERIT/DEM/v1_0_3").clip(region)
        slope = ee.Terrain.slope(dem)
        return slope

    def calculate_runoff_coefficient(self, aoi_gdf):

        region = self.gee_pipline.region.get_aoi()

        soil_texture = self.get_soil_texture(region)
        land_cover = self.get_landcover_image(region)
        slope = self.get_slop_map(region)

        # Assign Runoff Coefficients Based on `b0`
        runoffCoefficientSoil = soil_texture.expression(
            "(b0 == 1) ? 0.8 : "  # Clay (Cl)
            "(b0 == 2) ? 0.7 : "  # Silty Clay (SiCl)
            "(b0 == 3) ? 0.6 : "  # Sandy Clay (SaCl)
            "(b0 == 4) ? 0.5 : "  # Clay Loam (ClLo)
            "(b0 == 5) ? 0.45 : "  # Silty Clay Loam (SiClLo)
            "(b0 == 6) ? 0.4 : "  # Sandy Clay Loam (SaClLo)
            "(b0 == 7) ? 0.35 : "  # Loam (Lo)
            "(b0 == 8) ? 0.3 : "  # Silt Loam (SiLo)
            "(b0 == 9) ? 0.25 : "  # Sandy Loam (SaLo)
            "(b0 == 10) ? 0.2 : "  # Silt (Si)
            "(b0 == 11) ? 0.15 : "  # Loamy Sand (LoSa)
            "(b0 == 12) ? 0.1 : "  # Sand (Sa)
            "0.3",  # Default value if no match
            {'b0': soil_texture.select('b0')}  # Use soilTexture instead of landCover to access 'b0'
        )
        # Assign Runoff Coefficient Based on Updated Land Cover Classes
        runoffCoefficientLandCover = land_cover.expression(
            "(b('Map') == 10) ? 0.2 : "  # Tree Cover = Low Runoff
            "(b('Map') == 20) ? 0.3 : "  # Shrubland = Moderate Runoff
            "(b('Map') == 30) ? 0.25 : "  # Grassland = Moderate Runoff
            "(b('Map') == 40) ? 0.5 : "  # Cropland = Moderate-High Runoff
            "(b('Map') == 50) ? 0.9 : "  # Urban / Built-up = High Runoff
            "(b('Map') == 60) ? 0.7 : "  # Bare Soil = High Runoff
            "(b('Map') == 70) ? 0.0 : "  # Snow & Ice = No Runoff
            "(b('Map') == 80) ? 0.0 : "  # Permanent Water Bodies = No Runoff
            "(b('Map') == 90) ? 0.1 : "  # Herbaceous Wetland = Very Low Runoff
            "(b('Map') == 95) ? 0.15 : "  # Mangroves = Low Runoff
            "(b('Map') == 100) ? 0.2 : 0.3",  # Moss & Lichen = Low Runoff, Default runoff coefficient
            {'Map': land_cover.select('Map')}
        )
        # Optional: Calculate Slope Adjustment Factor
        slopeFactor = slope.expression(
            "b('slope') < 5 ? 0.8 : "  # Gentle slope, less runoff
            "b('slope') < 15 ? 1.0 : "  # Moderate slope, normal runoff
            "1.2",  # Steep slope, increased runoff
            {'slope': slope.select('slope')}
        )

        # Compute Final Runoff Coefficient Including Slope Factor
        finalRunoffCoefficient = runoffCoefficientSoil \
            .multiply(runoffCoefficientLandCover) \
            .multiply(slopeFactor) \
            .clip(region)
        fp = self.get_raster_fp(self.data_dir)
        if not os.path.exists(fp):
            GEEImage(finalRunoffCoefficient).download_image(fp, self.gee_pipline.region, self.scale,
                                                            within_aoi_only=False, save_metadata=False)
        # return finalRunoffCoefficient
        return fp

    @staticmethod
    def get_raster_fp(data_dir: str):
        # data_dir = os.path.join(MEDIA_DIR, 'soil_data/gee')
        # data_dir = APP_DATA_DIR / 'combined/runoff/'
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, f'runoff_coefficient.tif')


if __name__ == '__main__':
    # if self.gee_pipline is None:
    #     self.gee_pipline = init_gee_pipeline(aoi_gdf)
    aoi_gdf = GeoDataFrame()
    gee_pipeline= None
    runoff_coeff = RunoffCoefficient(gee_pipeline, "")
    fp = runoff_coeff.calculate_runoff_coefficient(aoi_gdf)
    da_logger.debug("complete runoff coefficient at {fp}")
