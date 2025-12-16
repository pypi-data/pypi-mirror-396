"""Data cleaning helpers using pandas."""

import pandas as pd
from loguru import logger


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize numeric columns of the dataframe between 0 and 1.

    Args:
        df (pd.DataFrame): Input dataframe.

    Returns:
        pd.DataFrame: Normalized dataframe.

    """
    logger.info("Normalizing dataframe")

    numeric_df = df.select_dtypes(include=["number"])
    normalized = numeric_df.apply(
        lambda col: (col - col.min()) / (col.max() - col.min()),
    )

    # Return with original non-numeric columns preserved
    for col in df.columns:
        if col not in normalized.columns:
            normalized[col] = df[col]

    return normalized
