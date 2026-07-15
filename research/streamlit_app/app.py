

from config.strategies import get_strategy_options, get_strategy_options_by_ticker
from config.single_assets import get_single_assets
from config.market_overview_assets import get_market_overview_assets
from screens.single_asset import render_single_asset_view
from screens.market_overview import render_market_overview_view
from screens.strategy_asset import render_strategy_asset_view

import streamlit as st


st.set_page_config(
    page_title="Financial Research",
    page_icon="📈",
    layout="wide",
)


def select_box_with_warning(label: str, options: list, format_func) -> any:
    
    if not options:
        st.warning(f"Nenhum item disponível para {label}.")
        return None
    
    return st.sidebar.selectbox(label, options, format_func=format_func)


def main() -> None:

    st.title("Financial Research Streamlit")

    mode = st.sidebar.radio(
        "Modo de visualização",
        ["Ativo individual", "Visão geral de ativos", "Estratégia de investimento"],
        index=0,
    )

    # Seleciona o indice de visão geral de ativos
    selected_market_overview_asset = select_box_with_warning(
        "Indice", 
        options=get_market_overview_assets(), format_func=lambda asset: asset.label)
    if not selected_market_overview_asset:
        return
        
    if mode == "Ativo individual":
        
        # Seleciona o ativo individual
        selected_single_asset = select_box_with_warning(
            "Ativo", 
            options=get_single_assets(indice=selected_market_overview_asset.ticker), format_func=lambda asset: asset.label)
        if not selected_single_asset:
            return
        
        render_single_asset_view(selected_single_asset)
        
    elif mode == "Visão geral de ativos":
        render_market_overview_view(selected_market_overview_asset)
    
    elif mode == "Estratégia de investimento":
        
        # Seleciona o ativo individual
        selected_single_asset = select_box_with_warning(
            "Ativo", 
            options=get_single_assets(indice=selected_market_overview_asset.ticker), format_func=lambda asset: asset.label)
        if not selected_single_asset:
            return
        
        # Seleciona o ativo para estratégia
        selected_strategy_asset = select_box_with_warning(
            "Estratégia por ativo", 
            options=get_strategy_options_by_ticker(ticker=selected_single_asset.ticker), format_func=lambda asset: asset.name_file_strategy)
        
        if not selected_strategy_asset:
            return
        
        render_strategy_asset_view(selected_strategy_asset)
        
        
if __name__ == "__main__":
    
    main()