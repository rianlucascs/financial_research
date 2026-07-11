

from pandas import DataFrame, MultiIndex
import streamlit as st
from yfinance import download

from config.assets import AssetOption


def _normalize_download(df: DataFrame) -> DataFrame:
    if df.empty:
        return df

    if isinstance(df.columns, MultiIndex):
        df = df.droplevel(1, axis=1)

    return df.sort_index()


@st.cache_data(ttl=60 * 30)
def load_price_data(ticker: str, interval: str = "1d") -> DataFrame:
    
    raw = download(
        ticker,
        period="10y",
        interval=interval,
        progress=False,
        auto_adjust=False,
    )
    
    return _normalize_download(raw)


@st.cache_data(ttl=60 * 30)
def load_all_price_data(assets: tuple[AssetOption, ...]) -> dict[str, DataFrame]:
    
    prices_by_ticker: dict[str, DataFrame] = {}
    
    for asset in assets:
        
        df = load_price_data(asset.ticker)
        
        if not df.empty:
            
            prices_by_ticker[asset.ticker] = df
            
    return prices_by_ticker
