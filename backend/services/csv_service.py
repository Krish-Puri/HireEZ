"""
CSV/Excel Reader Service

Reads CSV and Excel files and parses candidate/test data.
Column names are matched case-insensitively and with common aliases.
"""

from dataclasses import dataclass
from typing import Any, Optional
import re

import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# Column name normalizer
# ─────────────────────────────────────────────────────────────────────────────

def _normalize_column(col: str) -> str:
    """Lowercase and strip whitespace from column name."""
    return col.lower().strip()


def _find_col(df_columns: list[str], *aliases: str) -> Optional[str]:
    """
    Find a column by any of its aliases (case-insensitive).
    Returns the actual column name from the dataframe, or None.
    """
    aliases_lower = {a.lower().strip(): a for a in aliases}
    for col in df_columns:
        if _normalize_column(col) in aliases_lower:
            return col  # Return actual column name from dataframe, not the alias
    # Try partial match
    for col in df_columns:
        col_norm = _normalize_column(col)
        for alias in aliases:
            if alias.lower().strip() in col_norm or col_norm in alias.lower().strip():
                return col
    return None


def _get_row_val(row: pd.Series, df_cols: list[str], *aliases: str) -> Any:
    """Get a row value by column aliases (case-insensitive)."""
    actual = _find_col(df_cols, *aliases)
    if actual is None:
        return ""
    val = row.get(actual, "")
    if pd.isna(val):
        return ""
    return str(val).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Dataclasses
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CandidateParseReport:
    candidates: list[dict]
    statistics: dict[str, Any]
    errors: list[dict[str, Any]]


@dataclass
class TestResultParseReport:
    results: list[dict]
    statistics: dict[str, Any]
    errors: list[dict[str, Any]]


# ─────────────────────────────────────────────────────────────────────────────
# CSV Service
# ─────────────────────────────────────────────────────────────────────────────

class CSVService:

    def read_file(self, file_path: str) -> pd.DataFrame:
        """Read CSV or Excel file, returning a DataFrame with normalized columns."""
        lower = file_path.lower()
        if lower.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        # Normalize column names: strip whitespace, lowercase
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("")
        return df

    def parse_candidates(self, csv_path: str) -> CandidateParseReport:
        """
        Parse candidate CSV/Excel.
        Flexible column matching (case-insensitive, common aliases).
        Required: Name (or Candidate Name, Full Name), Email (or Email Address)
        """
        df = self.read_file(csv_path)
        df_cols = list(df.columns)
        errors = []

        # Check required columns
        name_col = _find_col(df_cols, "name", "candidate name", "full name", "candidate")
        email_col = _find_col(df_cols, "email", "email address", "e-mail", "mail")

        missing = []
        if not name_col:
            missing.append("Name (or 'Candidate Name', 'Full Name')")
        if not email_col:
            missing.append("Email (or 'Email Address', 'E-mail')")

        if missing:
            raise ValueError(
                f"Missing required column(s): {', '.join(missing)}. "
                f"Found columns: {df_cols}"
            )

        candidates = []
        valid_rows = 0
        invalid_rows = 0

        for idx, row in df.iterrows():
            row_num = idx + 2
            email = _get_row_val(row, df_cols, "email", "email address", "e-mail", "mail")
            name  = _get_row_val(row, df_cols, "name", "candidate name", "full name", "candidate")

            if not email or email in ("nan", ""):
                errors.append({"row": row_num, "error": "Missing email"})
                invalid_rows += 1
                continue
            if "@" not in email or "." not in email:
                errors.append({"row": row_num, "error": f"Invalid email: {email}"})
                invalid_rows += 1
                continue

            # CGPA — handle various formats
            cgpa_raw = _get_row_val(row, df_cols, "cgpa", "c.g.p.a", "gpa", "sgpa", "cgpa score")
            try:
                cgpa = float(cgpa_raw) if cgpa_raw and cgpa_raw not in ("nan", "") else None
            except (ValueError, TypeError):
                cgpa = None

            def clean(val: str) -> Optional[str]:
                return val if val and val not in ("nan", "") else None

            candidates.append({
                "name":              clean(_get_row_val(row, df_cols, "name", "candidate name", "full name")),
                "email":             email.lower(),
                "college":           clean(_get_row_val(row, df_cols, "college", "university", "institution", "college name")),
                "branch":            clean(_get_row_val(row, df_cols, "branch", "department", "stream", "discipline")),
                "cgpa":              cgpa,
                "best_ai_project":   clean(_get_row_val(row, df_cols, "best ai project", "best ai work", "ai project", "ai project")),
                "research_work":      clean(_get_row_val(row, df_cols, "research work", "research", "publications", "research paper")),
                "github_url":         clean(_get_row_val(row, df_cols, "github profile", "github", "github url", "github link", "github_username")),
                "resume_url":         clean(_get_row_val(row, df_cols, "resume link", "resume", "resume url", "resume link", "cv", "cv link")),
            })
            valid_rows += 1

        statistics = {
            "total_rows":    len(df),
            "valid_rows":    valid_rows,
            "invalid_rows":  invalid_rows,
            "columns_found": df_cols,
        }
        return CandidateParseReport(
            candidates=candidates,
            statistics=statistics,
            errors=errors,
        )

    def parse_test_results(self, csv_path: str) -> TestResultParseReport:
        """
        Parse test results CSV/Excel.
        Flexible column matching (case-insensitive).
        Required: Email, test_la (or logical aptitude score), test_code (or coding test score)
        """
        df = self.read_file(csv_path)
        df_cols = list(df.columns)
        errors = []

        email_col = _find_col(df_cols, "email", "email address", "e-mail", "mail")
        if not email_col:
            raise ValueError(
                f"Missing required column: 'Email'. Found columns: {df_cols}"
            )

        results = []
        valid_rows = 0
        invalid_rows = 0

        for idx, row in df.iterrows():
            row_num = idx + 2
            email = _get_row_val(row, df_cols, "email", "email address", "e-mail", "mail")

            if not email or email in ("nan", ""):
                errors.append({"row": row_num, "error": "Missing email"})
                invalid_rows += 1
                continue

            def safe_float(val: str) -> Optional[float]:
                try:
                    return float(val) if val and val not in ("nan", "") else None
                except (ValueError, TypeError):
                    return None

            # test_la — Logical Aptitude score
            test_la = safe_float(_get_row_val(
                row, df_cols,
                "test_la", "test la", "logical aptitude", "logical aptitude score",
                "aptitude", "aptitude score", "la", "logical"
            ))

            # test_code — Coding Test score
            test_code = safe_float(_get_row_val(
                row, df_cols,
                "test_code", "test code", "coding", "coding test", "coding test score",
                "code", "code score", "programming", "programming score"
            ))

            results.append({
                "email":    email.lower(),
                "test_la":  test_la,
                "test_code": test_code,
            })
            valid_rows += 1

        statistics = {
            "total_rows":   len(df),
            "valid_rows":   valid_rows,
            "invalid_rows": invalid_rows,
            "columns_found": df_cols,
        }
        return TestResultParseReport(
            results=results,
            statistics=statistics,
            errors=errors,
        )


csv_service = CSVService()
