
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_retorno_vs_volatilidade(df: pd.DataFrame, ticker: str) -> go.Figure:
    
    window = 21
    retorno = df["Adj Close"].pct_change(fill_method=None)

    x = retorno.rolling(window).std().dropna()
    y = retorno.rolling(window).mean().dropna()

    media_x = x.mean()
    media_y = y.mean()

    cov = np.cov(x, y)
    valores, vetores = np.linalg.eigh(cov)
    ordem = valores.argsort()[::-1]
    valores = valores[ordem]
    vetores = vetores[:, ordem]

    angulo = np.linspace(0, 2 * np.pi, 200)
    escala = 2

    elipse = escala * np.sqrt(valores[:, None]) * np.array([np.cos(angulo), np.sin(angulo)])
    elipse_rot = vetores @ elipse

    ellipse_x = media_x + elipse_rot[0]
    ellipse_y = media_y + elipse_rot[1]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            name="Observações",
            marker=dict(size=6, opacity=0.5),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[x.iloc[-1]],
            y=[y.iloc[-1]],
            mode="markers",
            name="Atual",
            marker=dict(
                size=15,
                color="purple",
                symbol="diamond",
                line=dict(color="white", width=0.5),
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ellipse_x,
            y=ellipse_y,
            mode="lines",
            name="Elipse de confiança",
            line=dict(color="red"),
        )
    )
    
    coef = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = coef[0] * x_line + coef[1]

    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name="Regressão Linear",
            line=dict(color="darkorange", width=1)
        )
    )

    y_pred = np.polyval(coef, x)

    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)

    r2 = 1 - ss_res / ss_tot

    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"R² = {r2:.2f}",
        showarrow=False,
        bgcolor="darkorange",
    )

    fig.add_hline(y=y.mean(), line_dash="dot", line_color="gray")
    fig.add_vline(x=x.mean(), line_dash="dot", line_color="gray")

    fig.update_layout(
        template="plotly_white",
        title=f"Retorno vs Volatilidade - {ticker}",
        xaxis_title="Volatilidade",
        yaxis_title="Retorno",
        height=600,
    )
    return fig


def build_heatmap(tabela: pd.DataFrame, ticker: str) -> go.Figure:
    fig = px.imshow(
        tabela,
        text_auto=".5f",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        aspect="auto",
    )

    fig.update_layout(
        title=dict(
            text=f"Retorno Ano e Mês - {ticker}",
            x=0.5,
            xanchor="center",
            font=dict(size=18),
        ),
        coloraxis_colorbar=dict(
            title="Retorno Médio",
            len=0.8,
        ),
        xaxis=dict(
            title="",
            tickangle=0,
        ),
        yaxis=dict(title=""),
        height=560,
        template="plotly_white",
    )

    fig.add_annotation(
        text="<i>Intervalo do retorno: 1d | Período: 10y | Fonte: Yahoo Finance</i>",
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.12,
        showarrow=False,
        font=dict(size=11, color="gray"),
        xanchor="center",
    )

    return fig


def build_reg_lin_serie(df, residuo):

    fig = go.Figure()

    fig.add_scatter(
        x=df.index,
        y=residuo,
        name="Resíduo (%)"
    )

    fig.add_hline(
        y=0,
        line_color="red",
        line_width=1.5,
        line_dash="dash"
    )

    return fig


def build_reg_lin_residuo_histograma(residuo, ticker):

    atual = residuo.iloc[-1]

    # Estatísticas
    media = residuo.mean()
    mediana = residuo.median()
    desvio = residuo.std()

    p5 = residuo.quantile(0.05)
    p25 = residuo.quantile(0.25)
    p75 = residuo.quantile(0.75)
    p95 = residuo.quantile(0.95)

    zscore = (atual - media) / desvio

    # Histograma
    fig = px.histogram(
        x=residuo,
        nbins=50,
        title=f"{ticker} - Distribuição da distância para a tendência (%)",
        labels={
            "x": "Distância para a tendência (%)",
            "count": "Frequência"
        }
    )

    # Média
    fig.add_vline(
        x=media,
        line_color="blue",
        line_width=2,
    )

    # Mediana
    fig.add_vline(
        x=mediana,
        line_color="green",
        line_dash="dash",
        line_width=2,
    )

    # ±1 desvio padrão
    fig.add_vline(
        x=media + desvio,
        line_color="gray",
        line_dash="dot",
        annotation_text="+1σ",
    )

    fig.add_vline(
        x=media - desvio,
        line_color="gray",
        line_dash="dot",
        annotation_text="-1σ",
    )

    # Percentis
    fig.add_vline(
        x=p5,
        line_color="orange",
        line_dash="dash",
        annotation_text="P5"
    )

    fig.add_vline(
        x=p95,
        line_color="orange",
        line_dash="dash",
        annotation_text="P95"
    )

    # Linha do zero
    fig.add_vline(
        x=0,
        line_color="black",
        line_width=1,
        line_dash="dash"
    )

    # Valor atual
    fig.add_vline(
        x=atual,
        line_color="red",
        line_width=1,
        annotation_text=f"Atual ({atual:.2f}%)",
        annotation_position="top"
    )

    # Caixa de estatísticas
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.99,
        y=0.99,
        xanchor="right",
        yanchor="top",
        showarrow=False,
        align="left",
        bgcolor="white",
        bordercolor="black",
        text=(
            f"<b>Média:</b> {media:.2f}%<br>"
            f"<b>Mediana:</b> {mediana:.2f}%<br>"
            f"<b>Desvio:</b> {desvio:.2f}%<br>"
            f"<b>Z-Score:</b> {zscore:.2f}<br>"
            f"<b>P5:</b> {p5:.2f}%<br>"
            f"<b>P25:</b> {p25:.2f}%<br>"
            f"<b>P75:</b> {p75:.2f}%<br>"
            f"<b>P95:</b> {p95:.2f}%"
        )
    )

    fig.update_layout(
        width=1100,
        height=600,
        bargap=0.05
    )

    return fig


def build_balanco_patrimonial_map_bar(df):
    
    plot_df = (
        df[["Código", "value"]]
        .dropna()
        .sort_values("value")
    )

    fig = px.bar(
        plot_df,
        x="value",
        y="Código",
        orientation="h",
        color="value",
        color_continuous_scale="RdYlGn",
        labels={"value": "Variação (%)", "Código": "Empresa"},
        title="Variação do Patrimônio por Empresa"
    )

    fig.add_vline(x=0, line_width=1, line_color="black")
    fig.update_layout(height=1000, width=800, yaxis={"categoryorder": "total ascending"})
    fig.update_yaxes(tickmode="array", tickvals=plot_df["Código"], ticktext=plot_df["Código"])
    
    return fig


def build_drawdown_map_bar(df, value_column="drawdown"):

    plot_df = (
        df[["Código", value_column]]
        .dropna()
        .sort_values(value_column)
    )

    media = plot_df[value_column].mean()

    plot_df["cor"] = plot_df["Código"].apply(
        lambda x: "Benchmark" if x == "^BVSP" else "Empresa"
    )

    fig = px.bar(
        plot_df,
        x="Código",
        y=value_column,
        labels={
            value_column: "Drawdown (%)",
            "Código": "Empresa"
        },
        title="Drawdown Máximo por Empresa"
    )

    # Linha em zero
    fig.add_hline(
        y=0,
        line_color="black"
    )

    # Linha da média
    fig.add_hline(
        y=media,
        line_color="blue",
        line_dash="dash",
        annotation_text=f"Média: {media:.2f}%",
        annotation_position="top right"
    )

    fig.update_layout(
        height=500,
        width=1200,
        xaxis_tickangle=-90
    )
    
    cores = [
        "purple" if codigo == "^BVSP" else "firebrick"
        for codigo in plot_df["Código"]
    ]
        
    fig.update_traces(marker_color=cores)

    return fig