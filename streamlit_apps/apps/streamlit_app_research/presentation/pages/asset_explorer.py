

from streamlit_apps.apps.streamlit_app_research.application.services.asset_service import AssetService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_price_service import AssetPriceService
from streamlit_apps.apps.streamlit_app_research.application.analytics.price_regression_analysis import PriceRegressionAnalysis
from streamlit_apps.apps.streamlit_app_research.application.analytics.return_volatility_analysis import ReturnVolatilityAnalysis

from streamlit_apps.apps.streamlit_app_research.presentation.components.moving_average_select_widget import render_moving_average_select_widget
from streamlit_apps.apps.streamlit_app_research.presentation.components.asset_select_widget import render_asset_select_widget
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_price_line_chart import render_asset_price_line_chart
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_returns_line_chart import render_asset_returns_line_chart
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_returns_distribution_bar_chart import render_asset_returns_distribution_bar_chart
from streamlit_apps.apps.streamlit_app_research.presentation.components.styled_tabs_widget import styled_tabs
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_price_regression_chart import (
    render_asset_price_regression_chart,
    render_asset_price_regression_distribution_chart,
)
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_return_vs_volatility import (
    render_asset_return_vs_volatility_chart,
)

from streamlit_apps.apps.streamlit_app_research.shared.dto.asset_dto import AssetTradingCodeDTO

import streamlit as st
from pandas import DataFrame


asset_service = AssetService()
asset_price_service = AssetPriceService()


st.title("Asset Explorer")

asset: AssetTradingCodeDTO = render_asset_select_widget(asset_service.list_trading_codes())

(
    preco, 
    retornos, 
    balanco
) = styled_tabs(
    [
        "Preço", 
        "Retornos", 
        "Balanço"
    ]
)


with preco:

    try:
        
        price: DataFrame = asset_price_service.get_asset_price(
            tickers=asset.trading_code,
            period="10y"
            )
        
        render_asset_price_line_chart(price)
        
        st.dataframe(price[["Date", "Adj Close", "Volume"]].tail(5))
        
    except Exception as e:
        
        st.error(e.args[0])
    
    (
        regressao_de_preco, 
        indicator2, 
        indicator3
    ) = styled_tabs(
        [
            "Regressão de Preço", 
            "Indicador 2", 
            "Indicador 3"
        ]
    )
    
    with regressao_de_preco:

        analysis = PriceRegressionAnalysis(
            price=price,
            moving_average=render_moving_average_select_widget(key="asset_explorer_price_regression"),
        )

        render_asset_price_regression_chart(analysis)
        render_asset_price_regression_distribution_chart(analysis)


with retornos:
    
    daily_returns: DataFrame = asset_price_service.get_asset_returns(
        tickers=asset.trading_code,
        period="10y"
    )
    
    render_asset_returns_line_chart(daily_returns)
    
    st.dataframe(daily_returns[["Date", "daily_returns"]].tail(5))
    
    (
        distribuicao, 
        retorno_vs_volatilidade, 
        indicador3
    ) = styled_tabs(
        [
            "Distribuição", 
            "Retorno vs Volatilidade", 
            "Indicador 3"
        ]
    )
    
    with distribuicao:
        
        render_asset_returns_distribution_bar_chart(
            daily_returns=daily_returns,
            moving_average=render_moving_average_select_widget(key="asset_explorer_returns_distribution"),
        )
    
    with retorno_vs_volatilidade:

        analysis = ReturnVolatilityAnalysis(
            price=price,
            window=render_moving_average_select_widget(
                options = [20, 10, 5, 50, 100, 200],
                key="asset_explorer_return_vs_volatility"
            ),
        )

        render_asset_return_vs_volatility_chart(analysis)
        

with balanco:
    
    st.info("Balanço section is under construction.")