

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from pandas import DataFrame
from scipy.stats import linregress


class PriceRegressionAnalysis:

    def __init__(
        self,
        price: DataFrame,
        moving_average: int | None = None,
    ) -> None:
        data = price[["Date", "Adj Close"]].dropna().copy()

        if moving_average:
            data["Adj Close"] = (
                data["Adj Close"]
                .rolling(moving_average)
                .mean()
            )
            data = data.dropna()

        x = np.arange(len(data))
        y = data["Adj Close"].to_numpy()

        regression = linregress(x, y)

        trend = regression.intercept + regression.slope * x

        distance_pct = ((y - trend) / trend) * 100

        self.data = data
        self.distance_pct = distance_pct
        self.mean = distance_pct.mean()
        self.std = distance_pct.std()
        self.current = distance_pct[-1]
        

def render_asset_price_regression_chart(
    analysis: PriceRegressionAnalysis,
) -> None:

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=analysis.data["Date"],
            y=analysis.distance_pct,
            mode="lines",
            name="Distância",
        )
    )

    fig.add_hline(
        y=0,
        line_color="purple",
        line_width=2,
    )

    fig.add_hline(
        y=analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dash",
    )

    fig.add_hline(
        y=-analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dash",
    )

    fig.add_hline(
        y=2 * analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    fig.add_hline(
        y=-2 * analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Distância da Tendência (%)",
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )

    st.plotly_chart(fig, width="stretch")
    

def render_asset_price_regression_distribution_chart(
    analysis: PriceRegressionAnalysis,
) -> None:

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=analysis.distance_pct,
            nbinsx=30,
        )
    )

    fig.add_vline(
        x=analysis.current,
        line_color="red",
        line_width=2,
        annotation_text="Atual",
        annotation_position="top",
    )

    fig.add_vline(
        x=analysis.mean,
        line_color="purple",
        line_width=2,
        annotation_text="Média",
        annotation_position="top",
    )

    fig.add_vline(
        x=analysis.mean + analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dash",
    )

    fig.add_vline(
        x=analysis.mean - analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dash",
    )

    fig.add_vline(
        x=analysis.mean + 2 * analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    fig.add_vline(
        x=analysis.mean - 2 * analysis.std,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    fig.update_layout(
        xaxis_title="Distância da Tendência (%)",
        yaxis_title="Frequência",
        xaxis=dict(ticksuffix="%"),
        bargap=0.05,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
    )

    st.plotly_chart(fig, width="stretch")