import pandas as pd
import numpy as np
from pathlib import Path

INPUT_PATH = Path("data/processed/credit_data_clean.csv")
OUTPUT_PATH = Path("data/processed/credit_time_series.csv")

N_MONTHS = 6
RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)


def load_data():
    print("Loading cleaned dataset...")
    return pd.read_csv(INPUT_PATH)


def simulate_monthly_variation(df, month):
    df = df.copy()
    df["month"] = month

    # Simulate small drift (±5%)
    drift_factor = np.random.normal(loc=1.0, scale=0.05, size=len(df))

    monetary_cols = [c for c in df.columns if "bill_amt" in c or "pay_amt" in c]

    for col in monetary_cols:
        df[col] = (df[col] * drift_factor).clip(lower=0)

    # Slight age increase over time
    if "age" in df.columns:
        df["age"] = df["age"] + (month // 12)

    return df


def generate_time_series(df):
    print("Simulating monthly snapshots...")
    snapshots = []

    for month in range(1, N_MONTHS + 1):
        month_df = simulate_monthly_variation(df, month)
        snapshots.append(month_df)

    return pd.concat(snapshots, ignore_index=True)


def main():
    df = load_data()
    time_series_df = generate_time_series(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    time_series_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved time-series dataset to: {OUTPUT_PATH}")
    print("Shape:", time_series_df.shape)


if __name__ == "__main__":
    main()
