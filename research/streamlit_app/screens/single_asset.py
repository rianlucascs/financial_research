

from config.single_assets import SingleAssetOption
from data.series_prices import load_price_data
from components.metrics import describe_asset
from components.charts import (
    build_retorno_vs_volatilidade, 
    build_heatmap, 
    build_reg_lin_serie, 
    build_reg_lin_residuo_histograma
    )
from services.analytics import (
    build_tabela_retorno_mensal, 
    build_tabela_media_retorno_mensal, 
    build_reg_lin, 
    build_serie_retorno_mensal,  
    build_reg_ma
    )

import streamlit as st


def render_single_asset_view(selected_single_asset: SingleAssetOption) -> None:
    
    ticker = selected_single_asset.ticker
    
    st.sidebar.caption(f"Ticker selecionado: {ticker}")
    
    try:
        
        df = load_price_data(ticker)
        df_month = build_serie_retorno_mensal(df)
        
    except Exception as exc: 
        
        st.error(f"Não foi possível carregar dados para {ticker}: {exc}")
        
        return
    
    if df.empty:
        
        st.warning(f"Nenhum dado retornado para {ticker}.")

        return
    
    overview_tab, analysis_tab = st.tabs(["Visão geral", "Análises"])

    with overview_tab:
        
        st.subheader(f"Resumo do ativo: {selected_single_asset.label}")
        
        describe_asset(df)
        
        left, right = st.columns([1.1, 1])

        with left:
            
            st.markdown("### O que este painel reúne")
            st.write(
                "- Notebook 01.07: retorno x volatilidade com elipse de confiança.\n"
                "- Notebook 01.08: retorno acumulado por mês em matriz ano x mês.\n"
                "- Notebook 01.05: regressão linear com resíduos e histogramas.\n"
                "- O ticker é trocado pela sidebar e atualiza os dois gráficos."
            )

        with right:
            
            st.markdown("### Período")
            st.write("10 anos de dados diários via Yahoo Finance.")
            
            st.markdown("### Ticker")
            st.code(ticker)
            
    with analysis_tab:
        
        notebook_107_tab, notebook_108_tab, notebook_105_tab, notebook_110_tab = st.tabs(
            ["01.07 retorno_sd_x_retorno_mean", "01.08 retorno_agrupado_mes", "01.05 reg_lin", "01.10 reg_me"]
        )

        with notebook_107_tab:
            
            st.subheader("Retorno vs Volatilidade")
            st.caption("Versão Streamlit do notebook 01.07 com o ativo selecionado na sidebar.")
            
            fig_107 = build_retorno_vs_volatilidade(df, f"{ticker} - Intervalo Diário")
            fig_107_month = build_retorno_vs_volatilidade(df_month, f"{ticker} - Intervalo Mensal")
            
            st.plotly_chart(fig_107, width="stretch")
            st.plotly_chart(fig_107_month, width="stretch")
            
            st.subheader("DataFrame Diário")
            st.dataframe(df.tail(3).style.format("{:.5f}"), width="stretch")
            
            st.subheader("DataFrame Mensal")
            df_month["retorno"] = df_month["Adj Close"].pct_change(1)
            st.dataframe(df_month.tail(3).style.format("{:.5f}"), width="stretch")

        with notebook_108_tab:
            
            st.subheader("Retorno agrupado por mês")
            st.caption("Versão Streamlit do notebook 01.08 com o ativo selecionado na sidebar.")
            
            tabela = build_tabela_retorno_mensal(df)
            fig_108 = build_heatmap(tabela, ticker)
            media_tabela = build_tabela_media_retorno_mensal(tabela)
            
            st.plotly_chart(fig_108, width="stretch")
            st.dataframe(tabela.style.format("{:.5f}"), width="stretch")
            st.dataframe(media_tabela.style.format("{:.5f}"), width="stretch")
              
        with notebook_105_tab:
            
            st.subheader("Regressão linear")
            st.caption("Versão Streamlit do notebook 01.05 com o ativo selecionado na sidebar.")
            
            tendencia, residuo = build_reg_lin(df)
            
            fig_105 = build_reg_lin_serie(df, residuo)
            fig_105_hist = build_reg_lin_residuo_histograma(residuo, ticker, titulo=f"{ticker} - Distribuição da distância para a tendência (%)")
            
            st.plotly_chart(fig_105, width="stretch")
            st.plotly_chart(fig_105_hist, width="stretch")
        
        with notebook_110_tab:
            
            st.subheader("Média móvel")
            st.caption("Versão Streamlit do notebook 01.10 com o ativo selecionado na sidebar.")
            
            opcoes = {
                "Média Móvel (21p)": 21,
                "Média Móvel (200p)": 200,
            }
            
            window_select = st.selectbox(
                "Período da Média Móvel",
                options=list(opcoes.keys())
            )
            
            window = opcoes[window_select]
        
            tendencia_ma, residuo_ma = build_reg_ma(df, window)
            
            fig_110 = build_reg_lin_serie(df, residuo_ma)
            fig_110_hist = build_reg_lin_residuo_histograma(residuo_ma, ticker, titulo=f"{ticker} - Distribuição da distância para a tendência (%)")
            
            st.plotly_chart(fig_110, width="stretch")
            st.plotly_chart(fig_110_hist, width="stretch")