import pandas as pd
import os

def list_prefixes(df: pd.DataFrame) -> list:
    """Return all distinct prefixes in the dataframe."""
    return df["prefix"].dropna().unique().tolist()


def filter_by_prefix(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Return all rows that match a given prefix exactly."""
    return df[df["prefix"] == prefix]


def filter_prefix_contains(df: pd.DataFrame, text: str) -> pd.DataFrame:
    """Return all rows where prefix contains the given text."""
    return df[df["prefix"].str.contains(text, na=False)]


def find_by_uid_suffix(df: pd.DataFrame, uid_suffix: str) -> pd.DataFrame:
    """Return all rows that match a given uid_suffix."""
    return df[df["uid_suffix"] == uid_suffix]


def find_by_uid_full(df: pd.DataFrame, uid_full: str) -> pd.DataFrame:
    """Return all rows that match a given uid_full."""
    return df[df["uid_full"] == uid_full]


def holter_only(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows where holter == True."""
    return df[df["holter"] == True]


def non_holter_only(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows where holter == False."""
    return df[df["holter"] == False]


def get_path_by_uid_suffix(df: pd.DataFrame, uid_suffix: str) -> str | None:
    """
    Return the path for a given uid_suffix.
    If there are multiple rows, returns the first one.
    If nothing is found, returns None.
    """
    rows = df[df["uid_suffix"] == uid_suffix]
    if rows.empty:
        return None
    return rows.iloc[0]["path"]


def get_paths_by_prefix(df: pd.DataFrame, prefix: str, holter_only_flag: bool | None = None) -> list:
    """
    Return a list of paths filtered by prefix and optionally holter flag.
    - holter_only_flag = True  → only holter rows
    - holter_only_flag = False → only non-holter rows
    - holter_only_flag = None  → ignore holter column
    """
    subset = df[df["prefix"] == prefix]
    if holter_only_flag is not None:
        subset = subset[subset["holter"] == holter_only_flag]
    return subset["path"].dropna().tolist()


def check_missing_files(df):
    """
    Return subset of rows whose 'path' does not point to an existing file.
    """
    mask = ~df["path"].astype(str).apply(os.path.exists)
    return df[mask]


def check_existing_files(df):
    """
    Return subset of rows whose 'path' exists.
    """
    mask = df["path"].astype(str).apply(os.path.exists)
    return df[mask]
