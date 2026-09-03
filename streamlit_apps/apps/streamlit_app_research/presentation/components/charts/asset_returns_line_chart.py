

import streamlit as st
import plotly.graph_objects as go
from pandas import DataFrame


def render_asset_returns_line_chart(daily_returns: DataFrame) -> None:
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=daily_returns["Date"],
            y=daily_returns["daily_returns"],
            mode="lines",
            name="Daily Return",
        )
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Return",
        hovermode="x unified",
        margin=dict(l=0, r=0, t=20, b=0),
    )

    st.plotly_chart(
        fig,
        width='stretch',
    )