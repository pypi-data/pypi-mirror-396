from __future__ import annotations

import enum
import os
import threading
from typing import Optional, Union, Iterable

import geopandas as gpd
from shapely import wkb
from shapely.geometry import GeometryCollection, Polygon, MultiPolygon, base as shapely_base
from shapely.ops import unary_union

from digitalarzengine.io.gee.gee_auth import GEEAuth
from digitalarzengine.io.gee.gee_region import GEERegion
from digitalarzengine.io.gee.gpd_vector import GPDVector
from digitalarzengine.settings import BASE_DIR


class GEETags(enum.Enum):
    # Keeping dict payloads is fine if downstream expects them; otherwise prefer plain strings.
    Water = {"modis": "MODIS/061/MOD09A1"}
    Temperature = {"modis": "MODIS/061/MOD11A1"}
    SnowCover = {"modis": "MODIS/061/MOD10A1"}  # MODIS/061/MOD10A1


class GEEPipeline:
    """
    GEE pipeline with a class-level singleton auth and robust AOI normalization.

    Usage:
        pipe = GEEPipeline(aoi=my_gdf)  # or GPDVector
        region = pipe.region
    """

    aoi_gdv: Optional[GPDVector] = None
    region: Optional[GEERegion] = None

    # Class-level singleton authentication
    gee_auth: Optional[GEEAuth] = None
    _auth_lock = threading.Lock()

    def __init__(self, aoi: Union[GPDVector, gpd.GeoDataFrame, None] = None, is_browser: bool = False, config_fp:str=None):
        """Initialize GEE Pipeline, ensuring authentication is initialized once."""
        self.ensure_gee_initialized(is_browser=is_browser, config_fp=config_fp)
        if aoi is not None:
            # gpd.GeoDataFrame has .empty; custom objects may not—guard gently
            if isinstance(aoi, gpd.GeoDataFrame):
                if aoi.empty:
                    raise ValueError("Provided AOI GeoDataFrame is empty.")
            self.set_region(aoi)

    # ---------- Auth ----------

    @classmethod
    def ensure_gee_initialized(cls, is_browser: bool = False, config_fp:str=None) -> None:
        """Ensures Google Earth Engine is authenticated (once per process)."""
        with cls._auth_lock:
            if cls.gee_auth is None or not getattr(cls.gee_auth, "is_initialized", False):
                cls.set_gee_auth(is_browser, config_fp)
            else:
                # print("✅ Google Earth Engine already initialized")
                pass

    @classmethod
    def set_gee_auth(cls, is_browser: bool = False, config_fp=None) -> None:
        """Initializes GEE authentication only once per application run."""
        if is_browser:
            GEEAuth.gee_init_browser()
            # cls.gee_auth should be set by the browser init in your implementation
        else:
            if config_fp is not None:
                service_account_fp = config_fp
            else:
                service_account_fp = os.path.join(BASE_DIR, "config", "ee-atherashraf-cloud-d5226bc2c456.json")
            # NOTE: Your class exposes gee_init_browser and *geo*_init_personal — assuming the latter is correct.
            cls.gee_auth = GEEAuth.geo_init_personal("atherashraf@gmail.com", service_account_fp)

    # ---------- AOI handling ----------

    def set_region(self, aoi: Union[GPDVector, gpd.GeoDataFrame]) -> None:
        """
        Sets the area of interest (AOI) and converts it into GEE Region format.
        - Reprojects to EPSG:4326
        - Drops Z (EE needs 2D)
        - Repairs invalid geometries
        - Unions to a single polygon/multipolygon
        """
        if isinstance(aoi, gpd.GeoDataFrame):
            aoi = GPDVector(aoi)

        gdf = aoi.get_gdf()
        if gdf is None or gdf.empty:
            raise ValueError("AOI GeoDataFrame is empty or None.")

        # Ensure CRS is EPSG:4326
        if gdf.crs is not None and (gdf.crs.to_epsg() != 4326):
            gdf = gdf.to_crs(epsg=4326)
        elif gdf.crs is None:
            # Assume EPSG:4326 if missing; adjust if your data guarantees differ
            gdf = gdf.set_crs(epsg=4326)

        # Drop Z to make 2D geometries (EE does not accept 3D)
        def _force_2d(geom: Optional[shapely_base.BaseGeometry]):
            if geom is None or geom.is_empty:
                return geom
            # Round-trip via WKB to strip Zs robustly
            return wkb.loads(wkb.dumps(geom, output_dimension=2))

        gdf = gdf.set_geometry(gdf.geometry.apply(_force_2d))

        # Fix invalid geometries (zero-buffer trick)
        # buffer(0) is safe in lon/lat here because distance=0 (no unit distortion)
        gdf = gdf.set_geometry(gdf.geometry.buffer(0))

        # Robust union to a single geometry
        polygon = self._union_all(gdf.geometry)

        # For GeometryCollection, extract polygonal parts only
        if isinstance(polygon, GeometryCollection):
            poly_parts = [g for g in polygon.geoms if isinstance(g, (Polygon, MultiPolygon))]
            if not poly_parts:
                raise ValueError(
                    "AOI union resulted in a non-polygonal GeometryCollection with no polygonal parts."
                )
            polygon = unary_union(poly_parts)

        # Ensure geometry is polygonal and not empty
        if polygon is None or polygon.is_empty:
            raise ValueError("AOI is empty after normalization/union.")
        if not isinstance(polygon, (Polygon, MultiPolygon)):
            raise ValueError(f"AOI must be Polygon or MultiPolygon after union, got {polygon.geom_type}.")

        # Build normalized GeoDataFrame (single feature) and serialize to GeoJSON
        gdf_norm = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
        self.aoi_gdv = GPDVector(gdf_norm)
        geojson = self.aoi_gdv.to_geojson(self.aoi_gdv.get_gdf())

        # Hand off to GEE
        self.region = GEERegion.from_geojson(geojson)

    @staticmethod
    def _union_all(geoms: Iterable[shapely_base.BaseGeometry]):
        """
        Union geometries using the most compatible approach across GeoPandas/Shapely versions.
        Prefer GeoSeries.unary_union or shapely.ops.unary_union; avoid relying on
        GeoPandas .union_all (only in newer versions).
        """
        # If geoms is a GeoSeries, unary_union exists as a property/method
        try:
            # geoms may be a GeoSeries; GeoSeries.unary_union returns a single geometry
            return geoms.unary_union  # type: ignore[attr-defined]
        except Exception:
            # Fall back to shapely.ops.unary_union
            return unary_union(list(geoms))
