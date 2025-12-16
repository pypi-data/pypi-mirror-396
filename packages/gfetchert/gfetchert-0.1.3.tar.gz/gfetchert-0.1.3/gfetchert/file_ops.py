"""
file_ops.py
------------
Helper functions for handling CSV or DataFrame inputs in Gfetchert.
"""

import pandas as pd
from tqdm import tqdm
from .core import get_rainfall




def fetch_from_csv(
    csv_file: str,
    date_col: str = "date",
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    save_as: str = "output_with_rain.csv"
):
    """
    Fetch rainfall for each row in a CSV file and save results.

    Parameters
    ----------
    csv_file : str
        Path to input CSV containing date, latitude, and longitude columns.
    date_col : str
        Column name for date values (YYYY-MM-DD).
    lat_col : str
        Column name for latitude.
    lon_col : str
        Column name for longitude.
    save_as : str
        Output CSV file name.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing all original columns plus `rainfall_mm`.
    """

    df = pd.read_csv(csv_file)

    # Ensure required columns exist
    for col in [date_col, lat_col, lon_col]:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in CSV file")

    # Add rainfall column
    rainfall_values = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Fetching rainfall data"):
        rain = get_rainfall(
            float(row[lat_col]),
            float(row[lon_col]),
            str(row[date_col])
        )
        rainfall_values.append(rain)

    df["rainfall_mm"] = rainfall_values
    df.to_csv(save_as, index=False)
    print(f"✅ Rainfall data saved to '{save_as}'")

    return df
