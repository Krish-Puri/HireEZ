"""
CSV Reader Service

Responsible only for reading CSV files.
"""

import pandas as pd


class CSVService:

    def read_csv(self, csv_path: str) -> pd.DataFrame:

        return (
            pd.read_csv(csv_path)
            .fillna("")
        )


csv_service = CSVService()