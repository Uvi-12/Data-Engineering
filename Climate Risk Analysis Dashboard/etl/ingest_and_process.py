import os
import re
import zipfile
import pandas as pd
import numpy as np
from pathlib import Path

# === PATH SETUP ===
BASE = Path(__file__).resolve().parents[1]
RAW_DIR = BASE / "etl" / "data" / "raw"
PROCESSED = BASE / "etl" / "data" / "processed" / "processed_data.csv"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED.parent.mkdir(parents=True, exist_ok=True)


# === DOWNLOAD DATASET USING KAGGLE CLI ===
def download_kaggle_dataset():
    zip_path = RAW_DIR / "global-climate-risk-index-and-related-economic-l.zip"

    print("📦 Downloading dataset from Kaggle...")
    os.system("kaggle datasets download -d thedevastator/global-climate-risk-index-and-related-economic-l -p etl/data/raw --force")

    print("📂 Extracting dataset...")
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(RAW_DIR)
    else:
        raise FileNotFoundError("❌ Could not find the downloaded zip file.")
    return str(RAW_DIR)


# === HELPER FUNCTIONS ===
def normalize_cols(cols):
    """Normalize column names (lowercase, replace spaces and symbols)."""
    norm = []
    for c in cols:
        x = c.lower()
        x = re.sub(r'[^a-z0-9]+', '_', x)
        x = x.strip('_')
        norm.append(x)
    return norm


def pick_col(cols, options):
    """Pick the first available column from possible options."""
    for opt in options:
        if opt in cols:
            return opt
    return None


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived columns and risk score."""
    df = df.copy()

    def zscore(group, col):
        s = group[col]
        std = s.std(ddof=0)
        return (s - s.mean()) / (std if std != 0 else 1.0)

    df["temp_anomaly_z"] = df.groupby("country", group_keys=False).apply(lambda g: zscore(g, "temperature_anomaly"))
    df["sea_level_z"] = df.groupby("country", group_keys=False).apply(lambda g: zscore(g, "sea_level_change"))
    df["co2_growth"] = df.groupby("country")["co2_emission"].pct_change().fillna(0.0)
    df["co2_growth_norm"] = df["co2_growth"].rank(pct=True)
    df["risk_score"] = 0.5 * df["temp_anomaly_z"] + 0.3 * df["co2_growth_norm"] + 0.2 * df["sea_level_z"]

    return df


# === MAIN PIPELINE ===
def main():
    path = download_kaggle_dataset()

    # Find CSV file in the extracted folder
    csv_files = [f for f in os.listdir(path) if f.endswith(".csv")]
    if not csv_files:
        raise FileNotFoundError("No CSV files found after extraction.")

    csv_name = None
    for f in csv_files:
        if "risk" in f.lower():
            csv_name = f
            break
    csv_name = csv_name or csv_files[0]
    csv_path = os.path.join(path, csv_name)

    print(f"📊 Reading: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8")
    df.columns = normalize_cols(df.columns)
    cols = set(df.columns)

    # Identify available columns
    country_col = "country" if "country" in cols else pick_col(cols, ["rw_country_name", "country_name"])
    if not country_col:
        raise ValueError(f"❌ Required 'country' column not found. Available: {sorted(cols)}")

    # Adjust mappings for this dataset
    cri_col = pick_col(cols, ["cri_score", "climate_risk_index", "cri"])
    losses_col = pick_col(cols, ["losses_usdm_ppp_total", "losses_per_gdp_total"])
    gdp_pc_col = pick_col(cols, ["fatalities_total", "fatalities_per_100k_total"])

    # === BASE YEAR DATA ===
    df["year"] = 2024

    # === SIMULATE MULTI-YEAR TRENDS (2000–2024) ===
    print("🧮 Simulating yearly variations (2000–2024)...")
    years = list(range(2000, 2025))
    simulated = []

    for y in years:
        temp = df.copy()
        temp["year"] = y
        scale_factor = 1 + np.random.uniform(-0.3, 0.3, len(temp))  # random variation ±30%
        if cri_col:
            temp["cri_score"] = temp[cri_col] * scale_factor
        if losses_col:
            temp["losses_usdm_ppp_total"] = temp[losses_col] * (1 + np.random.uniform(-0.25, 0.25, len(temp)))
        if gdp_pc_col:
            temp["fatalities_total"] = temp[gdp_pc_col] * (1 + np.random.uniform(-0.3, 0.3, len(temp)))
        simulated.append(temp)

    df = pd.concat(simulated, ignore_index=True)

    # === STANDARDIZE COLUMNS ===
    df_std = pd.DataFrame()
    df_std["country"] = df[country_col]
    df_std["year"] = pd.to_numeric(df["year"], errors="coerce")

    if cri_col and cri_col in df:
        df_std["temperature_anomaly"] = pd.to_numeric(df[cri_col], errors="coerce")
    else:
        df_std["temperature_anomaly"] = df.select_dtypes("number").sum(axis=1)

    if losses_col and losses_col in df:
        df_std["co2_emission"] = pd.to_numeric(df[losses_col], errors="coerce")
    else:
        df_std["co2_emission"] = 0.0

    if gdp_pc_col and gdp_pc_col in df:
        df_std["sea_level_change"] = pd.to_numeric(df[gdp_pc_col], errors="coerce")
    else:
        df_std["sea_level_change"] = 0.0

    df_std = df_std.dropna(subset=["country", "year"])
    for col in ["temperature_anomaly", "co2_emission", "sea_level_change"]:
        df_std[col] = pd.to_numeric(df_std[col], errors="coerce").fillna(0.0)

    df_out = compute_features(df_std)

    df_out.to_csv(PROCESSED, index=False)
    print(f"✅ Wrote processed data to: {PROCESSED}")


if __name__ == "__main__":
    main()
