# Copyright (c) 2025 Janez Bučar
# All rights reserved.

import pandas as pd
import datetime

from typing import List
from .tickers import get_tickers


def get_ticker_data(symbol: str, start: str = None, end: str = None, model: str = "ALL"):
    """
    Fetch historical trading data for a single LJSE ticker.
    """

    df = get_tickers()

    row = df[df["symbol"] == symbol]
    if row.empty:
        raise ValueError(f"Ticker '{symbol}' not found on LJSE")

    isin = row["isin"].iloc[0]

    # resolve start date
    if start is None:
        raw = "2018-1-1"  # LJSE restrictions
        try:
            start = pd.to_datetime(raw).strftime("%Y-%m-%d")
        except:
            start = "2018-1-1"

    # resolve end date
    if end is None:
        end = datetime.date.today().strftime("%Y-%m-%d")

    # correct ALL endpoint (NO trading_model_id)
    if model.upper() == "ALL":
        url_hist = (
            f"https://rest.ljse.si/web/Bvt9fe2peQ7pwpyYqODM/"
            f"security-history/XLJU/{isin}/{start}/{end}/csv?language=SI"
        )
    else:
        # CT / AUCT / BLOCK endpoint (WITH trading_model_id)
        url_hist = (
            f"https://rest.ljse.si/web/Bvt9fe2peQ7pwpyYqODM/"
            f"security-history/XLJU/{isin}/{start}/{end}/"
            f"csv?trading_model_id={model}&language=SI"
        )

    # load CSV
    df_hist = pd.read_csv(url_hist, sep=";")

    if "date" not in df_hist.columns:
        return pd.DataFrame()

    # index to datetime
    df_hist["date"] = pd.to_datetime(df_hist["date"])
    df_hist = df_hist.set_index("date")

    # numeric columns to fix
    numeric_cols = [
        'open_price', 'high_price', 'low_price', 'last_price',
        'vwap_price', 'change_prev_close_percentage',
        'num_trades', 'volume', 'turnover'

    ]

    # clean numeric format (comma → dot) and convert to float
    for col in numeric_cols:
        if col in df_hist.columns:
            df_hist[col] = (
                df_hist[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
            )
            df_hist[col] = pd.to_numeric(df_hist[col], errors="coerce")

    return df_hist

def get_tickers_column_data(
    tickers: List[str],
    col: str = "last_price",
    start: str = None,
    end: str = None
) -> pd.DataFrame:
    """
    Fetch a single price/metric column for multiple LJSE tickers and
    return a single aligned DataFrame.

    Parameters
    ----------
    tickers : list of str
        List of LJSE symbols, e.g. ["KRKG", "TLSG", "PETG"].

    col : str
        Column to extract from each ticker's dataset (e.g. "last_price").

    start : str or None
        Start date 'YYYY-MM-DD'. If None → take min date of all tickers.

    end : str or None
        End date. If None → take max date of all tickers.

    Returns
    -------
    pandas.DataFrame
        Wide DF with tickers as columns and aligned date index.
        Missing dates are forward-filled.
    """

    frames = []

    # fetch each ticker DF
    for symbol in tickers:
        df = get_ticker_data(symbol, start=start, end=end, model="CT")

        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist for ticker {symbol}")

        # rename selected column to ticker symbol
        ser = df[col].rename(symbol)
        frames.append(ser)

    # combine into one DF by index
    df_all = pd.concat(frames, axis=1)

    # handle start/end logic if user supplied None
    if start is None:
        start = df_all.dropna(how='all').index.min()
    else:
        start = pd.to_datetime(start)

    if end is None:
        end = df_all.dropna(how='all').index.max()
    else:
        end = pd.to_datetime(end)

    # final slicing
    df_all = df_all.loc[start:end]

    return df_all