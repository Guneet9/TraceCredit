import pandas as pd
from pathlib import Path

RAW_DATA_PATH = Path("data/raw/raw_dataset.xls")
PROCESSED_DATA_PATH = Path("data/processed/credit_data_clean.csv")

def load_raw_data(path: Path) -> pd.DataFrame:
    print("Loading raw dataset...")
    return pd.read_excel(path, header=1)
    # df = df.drop(index=0).reset_index(drop=True)
    # df.columns = df.iloc[0]
    # df = df.drop(index=0).reset_index(drop=True)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning dataset...")

    column_mapping = {
        "LIMIT_BAL": "credit_limit",
        "SEX": "gender",
        "EDUCATION": "education",
        "MARRIAGE": "marital_status",
        "AGE": "age",
        "PAY_0": "pay_status_m1",
        "PAY_2": "pay_status_m2",
        "PAY_3": "pay_status_m3",
        "PAY_4": "pay_status_m4",
        "PAY_5": "pay_status_m5",
        "PAY_6": "pay_status_m6",
        "BILL_AMT1": "bill_amt_m1",
        "BILL_AMT2": "bill_amt_m2",
        "BILL_AMT3": "bill_amt_m3",
        "BILL_AMT4": "bill_amt_m4",
        "BILL_AMT5": "bill_amt_m5",
        "BILL_AMT6": "bill_amt_m6",
        "PAY_AMT1": "pay_amt_m1",
        "PAY_AMT2": "pay_amt_m2",
        "PAY_AMT3": "pay_amt_m3",
        "PAY_AMT4": "pay_amt_m4",
        "PAY_AMT5": "pay_amt_m5",
        "PAY_AMT6": "pay_amt_m6",
        "default_payment_next_month": "default_next_month"
    }

    df = df.rename(columns=column_mapping)

    selected_columns = list(column_mapping.values())
    df = df[selected_columns]

    df["gender"] = df["gender"].astype(int)
    df["education"] = df["education"].astype(int)
    df["marital_status"] = df["marital_status"].astype(int)
    df["default_next_month"] = df["default_next_month"].astype(int)

    return df

def save_processed_data(df: pd.DataFrame, path: Path):
    print("Saving cleaned dataset...")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def main():
    df_raw = load_raw_data(RAW_DATA_PATH)
    df_clean = clean_data(df_raw)
    save_processed_data(df_clean, PROCESSED_DATA_PATH)
    print("Data cleaning complete")

if __name__ == "__main__":
    main()
