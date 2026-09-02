

from streamlit_apps.apps.streamlit_app_research.application.services.asset_service import AssetService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_price_service import AssetPriceService
from streamlit_apps.apps.streamlit_app_research.presentation.components.asset_select_widget import render_asset_select_widget

from streamlit_apps.apps.streamlit_app_research.shared.dto.asset_dto import AssetTradingCodeDTO

import streamlit as st
from pandas import DataFrame


asset_service = AssetService()
asset_price_service = AssetPriceService()



st.title("Asset Explorer")


asset: AssetTradingCodeDTO = render_asset_select_widget(asset_service.list_trading_codes())

try:
    
    price: DataFrame = asset_price_service.get_asset_price(tickers=asset.trading_code)

    st.dataframe(price)
    
except Exception as e:
    
    st.error(e.args[0])