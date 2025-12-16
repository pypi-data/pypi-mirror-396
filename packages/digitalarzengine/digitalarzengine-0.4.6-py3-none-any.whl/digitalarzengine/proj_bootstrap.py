"""
Zero-import PROJ/GDAL bootstrap for Windows to avoid PostGIS collisions.
MUST be imported before anything geospatial (rasterio/pyproj/rio-tiler).

We do NOT import pyproj/rasterio to discover paths (that could load wrong DLLs);
instead, we compute the site-packages layout and set PATH/DLL dirs/envs first.
"""

import os, sys, pathlib, platform

# ---- locate site-packages for this Python
def _find_site_packages() -> pathlib.Path:
    # prefer explicit 'site-packages' entries in sys.path
    for p in sys.path:
        if p and ("site-packages" in p or "dist-packages" in p):
            return pathlib.Path(p)
    # fallback: <prefix>/Lib/site-packages (Windows venv)
    return pathlib.Path(sys.prefix) / "Lib" / "site-packages"

sp = _find_site_packages()

# expected wheels layout
pyproj_pkg      = sp / "pyproj"
pyproj_proj_bin = pyproj_pkg / "proj_dir" / "bin"
pyproj_proj_db  = pyproj_pkg / "proj_dir" / "share" / "proj"

rasterio_pkg    = sp / "rasterio"
rasterio_gdal   = rasterio_pkg / "gdal_data"

def _has_postgis(path_str: str) -> bool:
    s = path_str.lower()
    return ("postgresql" in s) or ("postgis" in s) or ("osgeo4w" in s)

# ---- 1) scrub bad env
for key in ("PROJ_LIB", "PROJ_DATA", "GDAL_DATA"):
    v = os.environ.get(key, "")
    print(f"{key}={v}")
    if v and _has_postgis(v):
        os.environ.pop(key, None)


# ---- 2) scrub PATH of PostGIS/OSGeo entries
if "PATH" in os.environ:
    os.environ["PATH"] = ";".join(p for p in os.environ["PATH"].split(";")
                                  if p and not _has_postgis(p))

# ---- 3) prepend venv DLL dirs and add to DLL search (Win10+)
def _add_dir(p: pathlib.Path):
    if not p or not p.exists():
        return
    p_str = str(p)
    os.environ["PATH"] = p_str + ";" + os.environ.get("PATH", "")
    if platform.system() == "Windows":
        try:
            os.add_dll_directory(p_str)  # Python 3.8+
        except Exception:
            pass

# Add pyproj proj/bin (proj_*.dll), rasterio pkg dir (gdal*.dll), and site-packages
_add_dir(pyproj_proj_bin)
_add_dir(rasterio_pkg)
_add_dir(sp)

# ---- 4) set envs to venv copies (no imports)
if pyproj_proj_db.exists():
    os.environ["PROJ_LIB"]  = str(pyproj_proj_db)
    os.environ["PROJ_DATA"] = str(pyproj_proj_db)
os.environ.setdefault("PROJ_NETWORK", "ON")

if rasterio_gdal.exists():
    os.environ["GDAL_DATA"] = str(rasterio_gdal)

# ---- 5) (optional) enable debug to see which proj.db is used
# os.environ["PROJ_DEBUG"] = "3"

# ---- 6) DO NOT test with pyproj/rasterio here; import in caller after bootstrap
