

from streamlit_apps.apps.streamlit_app_research.shared.dto.asset_dto import AssetTradingCodeDTO

import streamlit as st


def render_asset_select_widget(
    list_asset_search_labels: list[AssetTradingCodeDTO],
) -> str | None:

    if not list_asset_search_labels:
        st.warning("No assets available for selection.")
        return None

    selected_option = st.selectbox(
        f"Asset  —  {len(list_asset_search_labels)}",
        options=[asset for asset in list_asset_search_labels],
        format_func=lambda asset: f"{asset.trading_code}  —  {asset.company_name[0] if type(asset.company_name) is list else asset.company_name}",
        key="selected_asset",
    )

    return AssetTradingCodeDTO(
        trading_code=selected_option.trading_code,
        cvm_code=selected_option.cvm_code,
        company_name=selected_option.company_name,
    )
