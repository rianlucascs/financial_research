
from data.series_prices import load_price_data
from data.b3_indices_segmentos_setoriais import load_b3_indices_segmentos_setoriais
from data.cvm_balanco_patrimonial import load_cvm_balanco_patrimonial
from services.analytics import build_tabela_retorno_mensal

from numpy import nan, arange, polyfit, polyval
from pandas import DataFrame, set_option, concat, DateOffset
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta



def build_market_map_dataframe(indice: str = "IBEP"):
    
    df_b3 = load_b3_indices_segmentos_setoriais(indice=indice)
    
    nova_linha = DataFrame([{
        **{col: nan for col in df_b3.columns},
        "Código": "^BVSP",
        "Ação": "Ibovespa"
    }])
    
    df_b3 = concat([df_b3, nova_linha], ignore_index=True)
    
    benchmark = load_price_data("^BVSP")[["Adj Close"]].pct_change()
    
    for codigo, acao in zip(df_b3["Código"], df_b3["Ação"]):
        
        ticker = codigo + ".SA" if codigo != "^BVSP" else codigo
        
        serie_precos = load_price_data(ticker)
        
        dict_infos = {
            "ativo_total": {"tipo_arquivo": "BPA_ind", "cd_conta": "1"},
            "receita_de_vendas": {"tipo_arquivo": "DRE_ind", "cd_conta": "3.01"},
            "resultado_bruto": {"tipo_arquivo": "DRE_ind", "cd_conta": "3.03"},
        }
        
        for key, info in dict_infos.items():
            
            if codigo == "^BVSP":
                valor = nan
                df_b3.loc[df_b3["Código"] == codigo, key] = valor
                continue
            
            try:
                
                # Carregar o balanço patrimonial da CVM pelo código da ação
                valor = load_cvm_balanco_patrimonial(
                    ticker=codigo, 
                    tipo_arquivo=info["tipo_arquivo"], 
                    cd_conta=info["cd_conta"]
                ).astype(int).pct_change().iloc[:, 1].iloc[-1]
                
            except Exception:
                
                try:
                    # Se ocorrer um erro, tentar novamente com o nome da ação
                    valor = load_cvm_balanco_patrimonial(
                        ticker=acao, 
                        tipo_arquivo=info["tipo_arquivo"], 
                        cd_conta=info["cd_conta"]
                    ).astype(int).pct_change().iloc[:, 1].iloc[-1]
                
                except Exception:
                    
                    valor = nan
            
            df_b3.loc[df_b3["Código"] == codigo, key] = valor

        try:
            
            serie_precos = load_price_data(ticker)
                
        except Exception:
                
            drawdown_atual = nan
            residuo_reg_lin = nan

            continue
        
        # Drawdown
        preco_maximo = serie_precos['Adj Close'].max()
        preco_atual = serie_precos['Adj Close'].iloc[-1]
        drawdown_atual = (preco_atual - preco_maximo) / preco_maximo * 100
        df_b3.loc[df_b3["Código"] == codigo, "Drawdown Atual"] = drawdown_atual
        
        # Regressão linear
        y = serie_precos["Adj Close"].to_numpy()
        x = arange(len(y))

        coef = polyfit(x, y, 1)      
        tendencia = polyval(coef, x)

        residuo_reg_lin = ((serie_precos["Adj Close"] - tendencia) / tendencia) * 100
        residuo_reg_lin = residuo_reg_lin.iloc[-1]
        df_b3.loc[df_b3["Código"] == codigo, "Resíduo Regressão Linear"] = residuo_reg_lin
        
        # Beta
        beta = serie_precos["Adj Close"].pct_change().cov(benchmark["Adj Close"]) / benchmark["Adj Close"].var()
        df_b3.loc[df_b3["Código"] == codigo, "Beta"] = beta
        
        # Retorno agrupado por mês
        tabela = build_tabela_retorno_mensal(serie_precos)
        
        current_month = date.today().month
        next_month = (date.today() + relativedelta(months=1)).month
        
        df_b3.loc[df_b3["Código"] == codigo, f"Média Ret. Mês{current_month}"] = tabela[current_month].mean(skipna=True)
        df_b3.loc[df_b3["Código"] == codigo, f"Média Ret. Mês{next_month}"] = tabela[next_month].mean(skipna=True)
        
    
        df_b3 = df_b3.sort_values(by="Drawdown Atual", ascending=False)
    
    
    return df_b3
        