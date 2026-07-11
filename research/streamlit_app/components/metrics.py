

import pandas as pd
import streamlit as st


def describe_asset(df: pd.DataFrame) -> None:
    
    adj_close = df["Adj Close"].dropna()
    retorno_diario = adj_close.pct_change(fill_method=None).dropna()

    latest_close = adj_close.iloc[-1]
    last_return = retorno_diario.iloc[-1]
    
    preco_atual = latest_close
    preco_maximo = adj_close.cummax().iloc[-1]
    drowdown_acumulado = (preco_atual - preco_maximo) / preco_maximo * 100

    cols = st.columns(4)
    cols[0].metric("Último fechamento", f"{latest_close:,.2f}")
    cols[1].metric("Último retorno", f"{last_return * 100:,.2f}%")
    cols[2].metric("Drawdown acumulado", f"{drowdown_acumulado:,.2f}%")

