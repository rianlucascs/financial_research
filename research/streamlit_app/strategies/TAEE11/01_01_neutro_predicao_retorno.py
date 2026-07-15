

from research.quant.ml.aprendizado_supervisionado.alvos.retornos.binario.bin_001_A import bin_001_A
from research.quant.ml.aprendizado_supervisionado.feature_engineering.operators import *
from research.quant.ml.aprendizado_supervisionado.series_reader import SeriesReader
from research.streamlit_app.components.charts import (
    build_reg_lin_serie,
    build_serie_retorno_acumulado_estrategia,
    build_reg_lin_residuo_histograma
    )

import streamlit as st
from joblib import load
from numpy import where
from numpy import nan


def calcular_resultado(df):

    mask = df["alvo_binario"].isna() | df["predicao"].isna()

    df["resultado_estrategia"] = where(
        mask,
        nan,
        where(
            df["alvo_binario"] == df["predicao"],
            abs(df["retorno_futuro"]),
            -abs(df["retorno_futuro"]),
        ),
    )
    
    df["resultado_estrategia_acumulado"] = df["resultado_estrategia"].cumsum()
    
    return df


@st.cache_data
def strategy(selected_strategy_asset):

    # base
    serie_base = SeriesReader(
        ticker="TAEE11.SA",
        start_date="2011-03-31",
        benchmark=True,
        usd=True
        ).get()

    # alvo
    serie_alvo = bin_001_A(
        serie_precos=serie_base,
        horizonte=1
    ).preparar()
    
    # modelo
    modelo = load(f"research/streamlit_app/strategies/{selected_strategy_asset.acao}/modelo_01_01_taee11.joblib")

    # features
    def __61__(df):
        q = pct(df["High"])
        w = pct(df["High ^BVSP"])
        n = (DEV_ema(q, 20) / R_ema(q, 20)) - (DEV_ema(w, 3) / R_ema(w, 3))
        b = R_sum(q, 8).diff() / (1 - R_sum(n, 18).diff() * R_max(n, 8))
        v = R_sum(q * 0.4, 15) + R_sum(b * 0.7, 9) + (1 / (1 - R_kurt(b, 18)))
        m = v
        return m


    def __71__(df):
        q = pct(df["High"])
        w = pct(df["High ^BVSP"])
        n = (DEV_ema(q, 20) / R_ema(q, 20)) - (DEV_ema(w, 3) / R_ema(w, 3))
        b = R_sum(q, 8).diff() / (1 - R_sum(n, 18).diff() * R_max(n, 8))
        v = R_sum(q * 0.4, 15) + R_sum(b * 0.7, 19) + (1 / (1 - R_kurt(b, 18)))
        m = v
        return m


    def __62__(df):
        q = pct(df["High"])
        w = pct(df["High ^BVSP"])
        n = (DEV_ema(q, 20) / R_ema(q, 20)) - (DEV_ema(w, 3) / R_ema(w, 3))
        b = R_sum(q, 8).diff() / (1 - R_sum(n, 18).diff() * R_max(n, 8))
        v = R_sum(q * 0.4, 15) + R_sum(b * 0.7, 10) + (1 / (1 - R_kurt(b, 18)))
        m = v
        return m


    def __82__(df):
        q = pct(df["High"] - df["Open"])
        w = pct(df["High"] - df["Close"])
        e = pct(df["Close"])
        n = R_sum(R_ema(q, 4) - R_ema(w, 4), 19).diff()
        b = (e * n) / (n - R_mean(0.4 * n, 11))
        m = b
        return m


    def __73__(df):
        q = pct(df["High"] - df["Open"])
        w = pct(df["High"] - df["Close"])
        e = pct(df["Close"])
        n = R_sum(R_ema(q, 4) - R_ema(w, 4), 19).diff()
        b = (e * n) / n
        m = b
        return m

    df = serie_alvo.copy()
    
    df["__61__"] = __61__(df)
    df["__71__"] = __71__(df)
    df["__62__"] = __62__(df)
    df["__82__"] = __82__(df)
    df["__73__"] = __73__(df)

    features = ["__61__", "__71__", "__62__", "__82__", "__73__"]
    predicao = modelo.predict(df[features])

    df["predicao"] = predicao
    
    df = calcular_resultado(df)
    
    df["resultado_estrategia_acumulado"] = df["resultado_estrategia"].cumsum()
    
    return df


def render_strategy( selected_strategy_asset):
    
    df_resultado = strategy(selected_strategy_asset)
    
    st.write("Resultado da estratégia:")
    fig_line = build_serie_retorno_acumulado_estrategia(df_resultado)
    st.plotly_chart(fig_line, width="stretch")
    
    st.write("Deploy:")
    df_deploy = df_resultado[["Date", "Adj Close", "alvo_binario", "predicao", "resultado_estrategia", "resultado_estrategia_acumulado"]].tail(21)
    
    st.dataframe(df_deploy, width="stretch")
    
    fig_t = build_reg_lin_residuo_histograma(residuo=df_resultado["resultado_estrategia"], titulo="Histograma do resultado da estratégia", x_label="Resultado da estratégia (%)")
    st.plotly_chart(fig_t, width="stretch")