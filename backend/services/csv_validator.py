"""
CSV Validation Service
"""

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = [
    "Name",
    "Email",
    "College",
    "Branch",
    "CGPA",
    "Best AI Project",
    "Research Work",
    "GitHub Profile",
    "Resume Link",
]


@dataclass
class ValidationReport:

    dataframe: pd.DataFrame

    total_rows: int

    valid_rows: int

    invalid_rows: int

    errors: list[str]


class CSVValidator:

    def validate(
        self,
        dataframe: pd.DataFrame
    ) -> ValidationReport:

        missing = [

            column

            for column in REQUIRED_COLUMNS

            if column not in dataframe.columns

        ]

        if missing:

            raise ValueError(
                f"Missing columns: {missing}"
            )

        dataframe = dataframe.dropna(how="all")

        return ValidationReport(

            dataframe=dataframe,

            total_rows=len(dataframe),

            valid_rows=len(dataframe),

            invalid_rows=0,

            errors=[]

        )


csv_validator = CSVValidator()