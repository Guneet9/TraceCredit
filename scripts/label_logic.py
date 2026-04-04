import pandas as pd
import numpy as np
import os


def generate_baseline_credit_limit(customer):
    """
    Generate an initial credit limit using:
    - income (simulated)
    - risk_score (simulated)
    - age (from dataset)
    """
    income = customer.get("income", 0)
    risk = customer.get("risk_score", 5)
    age = customer.get("age", 25)

    base_limit = income * 0.20
    risk_adjustment = (5 - risk) * 1000
    age_bonus = (age - 25) * 100

    initial_limit = max(0, base_limit + risk_adjustment + age_bonus)
    return round(initial_limit, 2)


def apply_credit_limit_logic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds:
    - income (simulated)
    - risk_score (simulated)
    - initial_limit (calculated)
    """
    np.random.seed(42)

    df["income"] = np.random.randint(30000, 200000, size=len(df))
    df["risk_score"] = np.random.randint(1, 10, size=len(df))

    df["initial_limit"] = df.apply(generate_baseline_credit_limit, axis=1)
    return df


def main():
    input_path = "data/processed/credit_time_series.csv"
    output_path = "data/processed/baseline_credit_limit.csv"

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing input file: {input_path}")

    print("Loading Day 4 dataset...")
    df = pd.read_csv(input_path)

    print("Applying Day 5 credit limit logic...")
    df = apply_credit_limit_logic(df)

    df.to_csv(output_path, index=False)
    print(f"Day 5 complete Saved to: {output_path}")


if __name__ == "__main__":
    main()
