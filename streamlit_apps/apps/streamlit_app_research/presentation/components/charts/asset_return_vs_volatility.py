

import numpy as np
from pandas import DataFrame
import plotly.graph_objects as go
import streamlit as st


class ReturnVolatilityAnalysis:

    def __init__(
        self,
        price: DataFrame,
        window: int = 21,
    ) -> None:
        returns = (
            price["Adj Close"]
            .pct_change(fill_method=None)
            .dropna()
        )
        
        volatility = returns.rolling(window).std()
        mean_return = returns.rolling(window).mean()

        data = DataFrame(
            {
                "volatility": volatility,
                "mean_return": mean_return,
            }
        ).dropna()

        self.data = data

        self.mean_volatility = data["volatility"].mean()
        self.mean_return = data["mean_return"].mean()

        self.current_volatility = data["volatility"].iloc[-1]
        self.current_return = data["mean_return"].iloc[-1]

        self.r2 = self._calculate_r2()

        self.ellipse_x, self.ellipse_y = self._calculate_ellipse()


    def _calculate_r2(self) -> float:
        x = self.data["volatility"]
        y = self.data["mean_return"]

        coef = np.polyfit(x, y, 1)
        y_pred = np.polyval(coef, x)

        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)

        return 1 - ss_res / ss_tot


    def _calculate_ellipse(self):
        x = self.data["volatility"]
        y = self.data["mean_return"]

        covariance = np.cov(x, y)

        values, vectors = np.linalg.eigh(covariance)

        order = values.argsort()[::-1]

        values = values[order]
        vectors = vectors[:, order]

        angle = np.linspace(0, 2 * np.pi, 200)

        ellipse = (
            2
            * np.sqrt(values[:, None])
            * np.array([
                np.cos(angle),
                np.sin(angle),
            ])
        )

        rotated = vectors @ ellipse

        ellipse_x = self.mean_volatility + rotated[0]
        ellipse_y = self.mean_return + rotated[1]

        return ellipse_x, ellipse_y
    


def render_asset_return_vs_volatility_chart(
    analysis: ReturnVolatilityAnalysis,
) -> None:

    data = analysis.data

    fig = go.Figure()

    # Observações
    fig.add_trace(
        go.Scatter(
            x=data["volatility"],
            y=data["mean_return"],
            mode="markers",
            name="Observações",
            marker=dict(
                size=6,
                opacity=0.5,
            ),
        )
    )

    # Atual
    fig.add_trace(
        go.Scatter(
            x=[analysis.current_volatility],
            y=[analysis.current_return],
            mode="markers",
            name="Atual",
            marker=dict(
                size=12,
                color="orange",
                symbol="diamond",
                line=dict(
                    color="purple",
                    width=0.77,
                ),
            ),
        )
    )

    # Elipse
    fig.add_trace(
        go.Scatter(
            x=analysis.ellipse_x,
            y=analysis.ellipse_y,
            mode="lines",
            name="Dispersão",
            line=dict(
                color="red",
                width=1,
            ),
        )
    )

    # Regressão
    coef = np.polyfit(
        data["volatility"],
        data["mean_return"],
        1,
    )

    x_line = np.linspace(
        data["volatility"].min(),
        data["volatility"].max(),
        100,
    )

    y_line = coef[0] * x_line + coef[1]

    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name="Regressão",
            line=dict(
                color="purple",
                width=1,
                dash="dash",
            ),
        )
    )

    # Média de volatilidade
    fig.add_vline(
        x=analysis.mean_volatility,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    # Média de retorno
    fig.add_hline(
        y=analysis.mean_return,
        line_color="lightgray",
        line_width=1,
        line_dash="dot",
    )

    # R²
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"R² = {analysis.r2:.2f}",
        showarrow=False,
    )

    fig.update_layout(
        xaxis_title="Volatilidade",
        yaxis_title="Retorno Médio",
        xaxis=dict(
            tickformat=".1%",
        ),
        yaxis=dict(
            tickformat=".1%",
        ),
        hovermode="closest",
        showlegend=True,
        margin=dict(
            l=0,
            r=0,
            t=30,
            b=0,
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )