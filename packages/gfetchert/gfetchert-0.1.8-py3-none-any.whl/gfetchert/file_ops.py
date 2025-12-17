"""
file_ops.py
------------
Utility functions for handling CSV, Excel, or PDF files and
automatically fetching rainfall data via Gfetchert.
"""

import os
import pandas as pd
from tqdm import tqdm
import tabula
from .core import get_rainfall


def fetch_from_file(
    file_path: str,
    date_col: str = "date",
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    save_as: str | None = None
):
    """
    Fetch rainfall for each row in a file (CSV, Excel, or PDF) and save results.

    Parameters
    ----------
    file_path : str
        Path to the input file (supports .csv, .xlsx, .xls, .pdf)
    date_col : str
        Column name for the event date.
    lat_col : str
        Column name for latitude.
    lon_col : str
        Column name for longitude.
    save_as : str, optional
        Output file name for results. Defaults to '<filename>_with_rainfall.csv'

    Returns
    -------
    pandas.DataFrame
        DataFrame containing all original columns plus `rainfall_mm`.
    """

    # ----------------------------------------------------------------
    # Detect file type
    # ----------------------------------------------------------------
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif ext == ".pdf":
        tables = tabula.read_pdf(file_path, pages="all", multiple_tables=True)
        if not tables:
            raise ValueError("No tables found in the PDF.")
        df = pd.concat(tables, ignore_index=True)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    # ----------------------------------------------------------------
    # Verify required columns
    # ----------------------------------------------------------------
    for col in [date_col, lat_col, lon_col]:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in input file.")

    # ----------------------------------------------------------------
    # Fetch rainfall values
    # ----------------------------------------------------------------
    rainfall_values = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc=f"Fetching rainfall from {ext.upper()}"):
        try:
            # Normalize date (remove time if present)
            date_str = str(row[date_col]).split(" ")[0].strip()

            rain_df = get_rainfall(
                lat=float(row[lat_col]),
                lon=float(row[lon_col]),
                start=date_str,
                end=date_str
            )

            # ✅ Handle both DataFrame and single float
            if isinstance(rain_df, pd.DataFrame):
                rain = rain_df["rainfall_mm"].iloc[0] if not rain_df.empty else None
            else:
                rain = float(rain_df) if rain_df is not None else None

            print(f"[Gfetchert] Rainfall for {date_str}: {rain} mm")

        except Exception as e:
            print(f"[Gfetchert] Error processing row: {e}")
            rain = None

        rainfall_values.append(rain)

    # ----------------------------------------------------------------
    # Save output
    # ----------------------------------------------------------------
    df["rainfall_mm"] = rainfall_values
    save_as = save_as or f"{os.path.splitext(file_path)[0]}_with_rainfall.csv"
    df.to_csv(save_as, index=False)

    print(f"✅ Rainfall data saved to '{save_as}'")
    return df
