

from research.streamlit_app.components.metrics import describe_asset
from research.streamlit_app.config.strategies import StrategyOption, get_strategy_options_by_ticker
from research.streamlit_app.data.series_prices import load_price_data
from research.streamlit_app.services.analytics import build_serie_retorno_mensal
from research.streamlit_app.services.analytics import build_serie_retorno_mensal

import streamlit as st

from importlib import import_module

def render_strategy_asset_view(selected_strategy_asset: StrategyOption) -> None:
    
    acao = selected_strategy_asset.acao
    
    
    st.sidebar.caption(f"Ação selecionada: {acao}")
    
    try:
    
        strategy_module  = import_module(f"research.streamlit_app.strategies.{selected_strategy_asset.acao}.{selected_strategy_asset.name_file_strategy}")
    
    except ModuleNotFoundError:
        
        st.error(f"Não foi possível importar a estratégia para {selected_strategy_asset.acao}")
        
        return
    
    try:
        
        df = load_price_data(selected_strategy_asset.ticker)
        
    except Exception as exc: 
        
        st.error(f"Não foi possível carregar dados para {selected_strategy_asset.ticker}: {exc}")
        
        return
    
    if df.empty:
        
        st.warning(f"Nenhum dado retornado para {selected_strategy_asset.ticker}.")

        return
    
    overview_tab, estrategia_selecionada_tab = st.tabs(["Visão geral", "Estratégia selecionada"])
    
    with overview_tab:
        
        left, right = st.columns([1.1, 1])
        
        with left:
            
            st.write(f"Todas as estratégias disponíveis para o ativo ({selected_strategy_asset.ticker})")
            estrategias_disponiveis = get_strategy_options_by_ticker(ticker=selected_strategy_asset.ticker)
            for estrategia in estrategias_disponiveis:
                st.write(f"- {estrategia.name_file_strategy}")
        
        with right:
            pass
        
        
    with estrategia_selecionada_tab:
        
        st.write(f"#### Estratégia selecionada: {selected_strategy_asset.name_file_strategy}")
        
        strategy_module.render_strategy(selected_strategy_asset)
    