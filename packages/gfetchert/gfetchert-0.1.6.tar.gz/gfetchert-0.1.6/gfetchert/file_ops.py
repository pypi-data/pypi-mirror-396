
import tabula
import os
import pandas as pd
from tqdm import tqdm
from .core import get_rainfall


def fetch_from_file(
        file_path: str,
        date_col: str = "date",
        lat_col: str = "latitude",
        lon_col: str = "longitude",
        save_as: str | None = None
        
):
    
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif ext == ".pdf":
        tables = tabula.read_pdf(file_path, pages="all", multiple_tables=True)
        if not tables:
            raise ValueError("no tables found in the PDF.")
        df = pd.concat(tables, ignore_index=True)
    else:
        raise ValueError(f"Unsupported format: {ext}")
    

    for col in [date_col, lat_col, lon_col]:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}'")
        
        
    rainfall_values = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc=f"Fetching rainfall from {ext.upper()}"):
        try:
            rain_df = get_rainfall(
                lat=float(row[lat_col]),
                lon=float(row[lon_col]),
                start=str(row[date_col]),
                end=str(row[date_col])
            )
            rain = rain_df["rainfall_mm"].iloc[0] if not rain_df.empty else None
        except Exception:
            rain = None
        rainfall_values.append(rain)
    
    df["rainfall_mm"] = rainfall_values
    save_as = save_as or f"{os.path.splitext(file_path)[0]}_with_rainfall.csv"
    df.to_csv(save_as, index=False)
    print(f"Rainfall data saved to '{save_as}'")

    return df




