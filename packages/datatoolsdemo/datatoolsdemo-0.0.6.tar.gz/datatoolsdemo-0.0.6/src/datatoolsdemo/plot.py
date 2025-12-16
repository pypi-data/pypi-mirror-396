"""Simple plotting utilities using matplotlib."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_column(df: pd.DataFrame, column: str) -> None:
    """
    Plot a single column from a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    column : str
        Column name to plot.

    Returns
    -------
    None
    """
    if column not in df:
        raise ValueError(f"Column '{column}' does not exist")

    plt.figure(figsize=(8, 4))
    plt.plot(df[column])
    plt.title(f"Plot of column '{column}'")
    plt.xlabel("Index")
    plt.ylabel(column)
    plt.tight_layout()
    plt.show()
