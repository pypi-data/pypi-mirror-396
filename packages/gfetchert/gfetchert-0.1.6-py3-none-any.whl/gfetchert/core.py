"""
core.py
--------
Main module for Gfetchert.
Provides tools to fetch daily CHIRPS rainfall data for any date range and location.
"""

from dateutil import parser
import os
import gzip
import shutil
import requests
import pandas as pd
import rasterio
from datetime import timedelta
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
        Start date in any recognizable format (e.g. 'YYYY-MM-DD', 'DD/MM/YYYY').
    end : str, optional
        End date. If None, defaults to same as `start`.
    download_dir : str, default='chirps_data'
        Directory to store downloaded CHIRPS .tif files.

    Returns
    -------
    pandas.DataFrame or float
        - If multiple days: DataFrame with columns `date` and `rainfall_mm`.
        - If a single date: single rainfall value (float).
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

    # Smart date parsing
    try:
        start_dt = parser.parse(str(start))
        end_dt = parser.parse(str(end))
    except Exception:
        raise ValueError(f"Unrecognized date format: {start} or {end}")

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
        rain = None
        try:
            with rasterio.open(path_tif) as src:
                try:
                    val = next(src.sample([(lon, lat)]))[0]
                    if val == src.nodata or val < 0 or val > 500:
                        rain = None
                    else:
                        rain = float(val.item())
                except StopIteration:
                    rain = None
        except Exception as e:
            print(f"[Gfetchert] Raster read error for {path_tif}: {e}")
            rain = None

        results.append({"date": current.strftime("%Y-%m-%d"), "rainfall_mm": rain})
        current += timedelta(days=1)

    # ----------------------------------------------------------------
    # Return as DataFrame (ensure correct column order)
    # ----------------------------------------------------------------
    df = pd.DataFrame(results)

    # Enforce correct column order
    if set(["date", "rainfall_mm"]).issubset(df.columns):
        df = df[["date", "rainfall_mm"]]
    else:
        df["date"] = df.get("date")
        df["rainfall_mm"] = df.get("rainfall_mm")
        df = df[["date", "rainfall_mm"]]

    # ----------------------------------------------------------------
    # Smart return: if single record, return scalar rainfall value
    # ----------------------------------------------------------------
    if len(df) == 1:
        value = df["rainfall_mm"].iloc[0]
        print(f"[Gfetchert] Rainfall on {df['date'].iloc[0]}: {value} mm")
        return value

    return df
