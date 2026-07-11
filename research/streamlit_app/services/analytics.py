

from numpy import polyfit, polyval, arange
from pandas import DataFrame


def build_tabela_retorno_mensal(df: DataFrame) -> DataFrame:
    
    df["ret"] = df["Adj Close"].pct_change(fill_method=None)
    df["mes"] = df.index.month
    df["ano"] = df.index.year

    tabela = (
        df.groupby(["ano", "mes"])[["ret"]]
        .sum()
        .reset_index()
        .pivot(index="ano", columns="mes", values="ret")
    ) * 100

    return tabela


def build_tabela_media_retorno_mensal(tabela) -> DataFrame:
    media = DataFrame([tabela.mean(skipna=True)], index=["Média"])
    return media


def build_reg_lin(df: DataFrame) -> tuple:

    adj_close = df["Adj Close"].dropna()
    
    y = adj_close.to_numpy()
    x = arange(len(y))

    coef = polyfit(x, y, 1)      # regressão linear (grau 1)
    tendencia = polyval(coef, x)

    residuo = ((adj_close - tendencia) / tendencia) * 100
    
    return tendencia, residuo

