

from config.single_assets import get_single_assets
from config.market_overview_assets import get_market_overview_assets
from screens.single_asset import render_single_asset_view
from screens.market_overview import render_market_overview_view

import streamlit as st


st.set_page_config(
    page_title="Financial Research",
    page_icon="📈",
    layout="wide",
)


def main() -> None:

    st.title("Financial Research Streamlit")
    st.write("Escolha entre análise de um único ativo ou visão consolidada de todos os ativos.")

    mode = st.sidebar.radio(
        "Modo de visualização",
        ["Ativo individual", "Visão geral de ativos"],
        index=0,
    )

    # Seleciona o indice de visão geral de ativos
    market_overview_assets = get_market_overview_assets()
    if not market_overview_assets:
        st.warning("Nenhum ativo disponível para o índice IBEP.")
        return
    selected_market_overview_asset = st.sidebar.selectbox(
        "Indice", 
        market_overview_assets,
        format_func=lambda asset: asset.label
        )
    
    # Seleciona o ativo individual
    single_assets = list(get_single_assets(indice=selected_market_overview_asset.ticker))
    if not single_assets:
        st.warning("Nenhum ativo disponível para o índice IBEP.")
        return 
    selected_single_asset = st.sidebar.selectbox(
        "Ativo", 
        single_assets,
        format_func=lambda asset: asset.label
        )
        
    if mode == "Ativo individual":
        
        render_single_asset_view(selected_single_asset)
        
    else:
        
        render_market_overview_view(selected_market_overview_asset)
        
        
if __name__ == "__main__":
    
    main()