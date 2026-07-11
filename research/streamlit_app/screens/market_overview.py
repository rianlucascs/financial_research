

from data.market_map import build_market_map_dataframe
from data.balanco_patrimonial_map import build_balanco_patrimonial_map_dataframe
from components.charts import build_balanco_patrimonial_map_bar, build_drawdown_map_bar

import streamlit as st


def render_market_overview_view() -> None:
    
    overview_tab, mapa_tab, balanco_patrimonial_tab, drawdown_atual_tab = st.tabs(
        [
            "Visão geral", 
            "Mapa de ativos", 
            "Balanço Patrimonial",
            "Drawdown Atual",
        ]
    )
    
    with overview_tab:
        
        st.markdown("### O que este painel reúne")
        st.write(
            "- Notebook 02.01: tabela consolidada com dados setoriais, CVM e métricas de mercado.\n"
            "- Notebook 01.03: balanço patrimonial consolidado com dados setoriais.\n"
            "- Notebook 01.04: drawdown atual consolidado com dados setoriais.\n"
        )
        
    
    with mapa_tab:
        
        df_mapa = build_market_map_dataframe(indice="IBEP")
        
        format_columns = {"Beta": "{:.3f}"}
        for column in df_mapa.columns:
            
            if column.startswith("Média Ret. Mês"):
                format_columns[column] = "{:.2f}%"

            if column.startswith("Retorno Agrupado por Mês"):
                format_columns[column] = "{:.2f}%"
                
        for column in ["Ativo Total", "Resultado Bruto", "Receita de Vendas"]:
            if column in df_mapa.columns:
                format_columns[column] = "{:.2%}"

        if "Resíduo Regressão Linear" in df_mapa.columns:
            format_columns["Resíduo Regressão Linear"] = "{:.2f}%"
        
        if "Drawdown Atual" in df_mapa.columns:
            format_columns["Drawdown Atual"] = "{:.2f}%"

        st.dataframe(df_mapa.style.format(format_columns), width="stretch")


    with balanco_patrimonial_tab:
        
        st.write("Balanço Patrimonial")
        
        opcoes = {
            "Ativo Total": ("BPA_ind", "1"),
            "Resultado Bruto": ("DRE_ind", "3.03"),
            "Receita de Venda de Bens e/ou Serviços": ("DRE_ind", "3.01"),
        }
        
        conta = st.selectbox(
            "Conta contábil",
            options=list(opcoes.keys())
        )
        
        tipo_arquivo, cd_conta = opcoes[conta]

        df_balanco = build_balanco_patrimonial_map_dataframe(indice="IBEP", tipo_arquivo=tipo_arquivo, cd_conta=cd_conta)
        
        fig_balanco = build_balanco_patrimonial_map_bar(df_balanco)
        st.plotly_chart(fig_balanco, use_container_width=True)
        
        st.write(
            f"**Média da variação do patrimônio das empresas do índice:** "
            f"{df_balanco['value'].mean():.2f}%"
        )
    
    
    with drawdown_atual_tab:
        
        st.write("Drawdown Atual")
        
        df_drawdown = build_market_map_dataframe(indice="IBEP")
        
        fig_drawdown = build_drawdown_map_bar(df_drawdown, value_column="Drawdown Atual")
        st.plotly_chart(fig_drawdown, use_container_width=True)
            
        st.write(
            f"**Média do Drawdown Atual das empresas do índice:** "
            f"{df_drawdown['Drawdown Atual'].mean():.2f}%"
        )
        
        st.write(
            f"**Percentual de empresas abaixo da média:** "
            f"{(df_drawdown['Drawdown Atual'] < df_drawdown['Drawdown Atual'].mean()).mean():.2%}"
        )
        
     
