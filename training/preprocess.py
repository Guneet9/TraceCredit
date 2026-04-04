import pandas as pd
import numpy as np
from typing import Tuple, List


class DataPreprocessor:
    def __init__(self, train_test_split_ratio: float = 0.8, random_state: int = 42):
        self.train_test_split_ratio = train_test_split_ratio
        self.random_state = random_state
        self.feature_names = None
        self.target_name = 'default_next_month'

    def load_data(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        base_features = [
            'age', 'gender', 'education', 'marital_status',
            'pay_status_m1', 'pay_status_m2', 'pay_status_m3',
            'pay_status_m4', 'pay_status_m5', 'pay_status_m6',
            'bill_amt_m1', 'bill_amt_m2', 'bill_amt_m3',
            'bill_amt_m4', 'bill_amt_m5', 'bill_amt_m6',
            'pay_amt_m1', 'pay_amt_m2', 'pay_amt_m3',
            'pay_amt_m4', 'pay_amt_m5', 'pay_amt_m6',
            'credit_limit'
        ]

        bill_cols = [f'bill_amt_m{i}' for i in range(1, 7)]
        pay_cols = [f'pay_amt_m{i}' for i in range(1, 7)]
        status_cols = [f'pay_status_m{i}' for i in range(1, 7)]

        df['avg_bill_6m'] = df[bill_cols].mean(axis=1)
        df['avg_pay_6m'] = df[pay_cols].mean(axis=1)
        df['max_bill_6m'] = df[bill_cols].max(axis=1)
        df['default_status_count'] = (df[status_cols] < 0).sum(axis=1)
        df['utilization_ratio'] = df['max_bill_6m'] / (df['credit_limit'] + 1)
        df['payment_to_bill_ratio'] = df['avg_pay_6m'] / (df['avg_bill_6m'] + 1)

        engineered = ['avg_bill_6m', 'avg_pay_6m', 'max_bill_6m',
                      'default_status_count', 'utilization_ratio', 'payment_to_bill_ratio']

        self.feature_names = base_features + engineered
        return df[self.feature_names + [self.target_name]]

    def split_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = df.drop('month', axis=1, errors='ignore')
        split = int(len(df) * self.train_test_split_ratio)
        return df.iloc[:split].reset_index(drop=True), df.iloc[split:].reset_index(drop=True)

    def prepare_training_data(self, data_path: str) -> Tuple[
        np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]
    ]:
        df = self.load_data(data_path)
        df = self.prepare_features(df)
        train_df, test_df = self.split_data(df)

        X_train = train_df[self.feature_names].values
        y_train = train_df[self.target_name].values
        X_test = test_df[self.feature_names].values
        y_test = test_df[self.target_name].values

        return X_train, X_test, y_train, y_test, self.feature_names

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        return df
