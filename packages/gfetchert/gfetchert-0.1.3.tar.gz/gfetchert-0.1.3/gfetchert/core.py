"""
core.py
--------
Main module for Gfetchert.
Provides tools to fetch daily CHIRPS rainfall data for any date range and location.
"""

import os
import gzip
import shutil
import requests
import pandas as pd
import rasterio
from datetime import datetime, timedelta
from .geocode import get_coordinates


# --------------------------------------------------------------------
# CHIRPS data configuration
# --------------------------------------------------------------------
BASE_URL = (
    "https://data.chc.ucsb.edu/products/CHIRPS-2.0/"
    "global_daily/tifs/p05/{year}/chirps-v2.0.{year}.{month:02d}.{day:02d}.tif.gz"
)


def get_rainfall(
    *,
    lat: float | None = None,
    lon: float | None = None,
    location: str | None = None,
    start: str,
    end: str | None = None,
    download_dir: str = "chirps_data",
) -> pd.DataFrame:
    """
    Fetch CHIRPS daily rainfall data for a given coordinate or location and date range.

    Parameters
    ----------
    lat, lon : float, optional
        Geographic coordinates (in decimal degrees). Required if `location` not provided.
    location : str, optional
        Place name to geocode into coordinates (uses geopy internally).
    start : str
        Start date in 'YYYY-MM-DD' format.
    end : str, optional
        End date in 'YYYY-MM-DD' format. If None, defaults to same as `start`.
    download_dir : str, default='chirps_data'
        Directory to store downloaded CHIRPS .tif files.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns:
        - `date` : str, YYYY-MM-DD
        - `rainfall_mm` : float or None
    """
    # ----------------------------------------------------------------
    # Input validation and coordinate resolution
    # ----------------------------------------------------------------
    if location and (lat is None or lon is None):
        lat, lon, resolved = get_coordinates(location)
        print(f"[Gfetchert] Resolved location: {resolved} -> ({lat}, {lon})")
    elif lat is None or lon is None:
        raise ValueError("Provide either (lat, lon) or a valid location name.")

    if end is None:
        end = start

    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in 'YYYY-MM-DD' format.")

    if start_dt > end_dt:
        raise ValueError("Start date must not be after end date.")

    os.makedirs(download_dir, exist_ok=True)

    # ----------------------------------------------------------------
    # Iterate through each date and fetch rainfall
    # ----------------------------------------------------------------
    results = []
    current = start_dt

    while current <= end_dt:
        y, m, d = current.year, current.month, current.day
        file_gz = f"chirps-v2.0.{y}.{m:02d}.{d:02d}.tif.gz"
        file_tif = file_gz[:-3]
        path_gz = os.path.join(download_dir, file_gz)
        path_tif = os.path.join(download_dir, file_tif)
        url = BASE_URL.format(year=y, month=m, day=d)

        # ------------------------------------------------------------
        # Download & decompress
        # ------------------------------------------------------------
        if not os.path.exists(path_tif):
            try:
                r = requests.get(url, timeout=60)
                if r.status_code != 200:
                    results.append({"date": current.strftime("%Y-%m-%d"), "rainfall_mm": None})
                    current += timedelta(days=1)
                    continue
                with open(path_gz, "wb") as f:
                    f.write(r.content)
                with gzip.open(path_gz, "rb") as fin, open(path_tif, "wb") as fout:
                    shutil.copyfileobj(fin, fout)
                os.remove(path_gz)
            except Exception as e:
                print(f"[Gfetchert] Download error for {url}: {e}")
                results.append({"date": current.strftime("%Y-%m-%d"), "rainfall_mm": None})
                current += timedelta(days=1)
                continue

        # ------------------------------------------------------------
        # Extract rainfall value
        # ------------------------------------------------------------
        try:
            with rasterio.open(path_tif) as src:
                # safer and simpler than manual index
                val = next(src.sample([(lon, lat)]))[0]
                if val == src.nodata or val < 0 or val > 500:
                    rain = None
                else:
                    rain = float(val)
        except Exception as e:
            print(f"[Gfetchert] Raster read error for {path_tif}: {e}")
            rain = None

        results.append({"date": current.strftime("%Y-%m-%d"), "rainfall_mm": rain})
        current += timedelta(days=1)

    # ----------------------------------------------------------------
    # Return as DataFrame
    # ----------------------------------------------------------------
    return pd.DataFrame(results)
