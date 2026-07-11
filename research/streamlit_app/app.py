
from config.assets import get_assets
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

    assets = list(get_assets(indice="IBEP"))
    
    if mode == "Ativo individual":
        if not assets:
            st.warning("Nenhum ativo disponível para o índice IBEP.")
            return
        
        selected_asset = st.sidebar.selectbox(
            "Ativo", 
            assets,
            format_func=lambda asset: asset.label
            )
        
        render_single_asset_view(selected_asset)
        
    else:
        
        render_market_overview_view()
        
        
if __name__ == "__main__":
    
    main()