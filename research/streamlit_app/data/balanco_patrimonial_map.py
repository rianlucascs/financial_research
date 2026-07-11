

from data.b3_indices_segmentos_setoriais import load_b3_indices_segmentos_setoriais
from data.cvm_balanco_patrimonial import load_cvm_balanco_patrimonial


DEFAULT_BALANCO_PATRIMONIAL_MAP = {
    "BPA_ind": {
        "1": "Ativo Total",
    },
    "DRE_ind": {
        "3.03": "Resultado Bruto",
        "3.01": "Receita de Venda de Bens e/ou Serviços",
    },
}


def build_balanco_patrimonial_map_dataframe(indice: str="IBEP", tipo_arquivo: str = "BPA_ind", cd_conta: str = "1"):
    
    df_b3 = load_b3_indices_segmentos_setoriais(indice)
    
    dict_data = {}
    
    tickers_erros = []
    
    for codigo, acao in zip(df_b3["Código"], df_b3["Ação"]):
        
        try:

            df_cvm_balanco_patrimonial = load_cvm_balanco_patrimonial(ticker=codigo, tipo_arquivo=tipo_arquivo, cd_conta=cd_conta)
        
        except Exception:
            
            try:
                
                df_cvm_balanco_patrimonial = load_cvm_balanco_patrimonial(ticker=acao, tipo_arquivo=tipo_arquivo, cd_conta=cd_conta)
                
            except Exception:
                        
                tickers_erros.append(codigo)
            
                continue
        
        name = df_cvm_balanco_patrimonial.columns[-1]
        value = df_cvm_balanco_patrimonial.iloc[:, 1].ffill().pct_change(1).iloc[-1] * 100
        
        dict_data[codigo] = {"name": name, "value": value}
    

    nome_map = {
        ticker: dados["name"]
        for ticker, dados in dict_data.items()
    }

    valor_map = {
        ticker: dados["value"]
        for ticker, dados in dict_data.items()
    }

    df_b3["nome"] = df_b3["Código"].map(nome_map)
    df_b3["value"] = df_b3["Código"].map(valor_map)
    
    
    return df_b3