

from pipelines.readers.cvm_formulario_demonstracoes_financeiras_padronizadas import (
    ReaderCSVCVMFormularioDemonstracoesFinanceirasPadronizadas,
    ReaderSQLCVMFormularioDemonstracoesFinanceirasPadronizadas,
)
from pipelines.readers.cvm_formulario_informacoes_trimestrais import (
    ReaderCSVCVMFormularioInformacoesTrimestrais,
    ReaderSQLCVMFormularioInformacoesTrimestrais,
)

import pandas as pd


class ReaderCSVCVMBalancoPatrimonial:
    """Classe para leitura do Balanço Patrimonial da CVM, combinando dados de ITR e DFP."""
    
    def __init__(self):
        
        self.reader_itr = ReaderCSVCVMFormularioInformacoesTrimestrais()
        self.reader_dfp = ReaderCSVCVMFormularioDemonstracoesFinanceirasPadronizadas()

        
    def read(self, ticker: str = "VALE3", tipo_arquivo: str = "BPA_con", cd_conta: str = "3.1"):
        """Lê e combina os arquivos CSV do Balanço Patrimonial da CVM para um determinado ticker, tipo de arquivo e código de conta."""

        df_itr = self.reader_itr.read(ticker=ticker, tipo_arquivo=tipo_arquivo)
        df_dfp = self.reader_dfp.read(ticker=ticker, tipo_arquivo=tipo_arquivo)
    
        df_itr["origem_demonstracao"] = "itr"
        df_dfp["origem_demonstracao"] = "dfp"

        todas_colunas = sorted(set(df_itr.columns) | set(df_dfp.columns))
        df_itr = df_itr.reindex(columns=todas_colunas)
        df_dfp = df_dfp.reindex(columns=todas_colunas)


        # Concatena os dataframes, alinhando colunas e mantendo o indice original (ou resetando se ignore_index=True).
        df = pd.concat([df_itr, df_dfp], ignore_index=True)


        # Converte colunas de data para datetime, se existirem, e ordena pelo coluna_data
        for col in ["DT_REFER", "DT_FIM_EXERC", "DT_INI_EXERC"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])


        # Ordena o dataframe concatenado pela coluna de data (coluna_data) e reseta o indice.
        df = df.sort_values("DT_REFER").reset_index(drop=True)


        # Filtra o dataframe concatenado para manter apenas as linhas correspondentes ao cd_conta e ORDEM_EXERC = "ÚLTIMO", se essas colunas existirem.
        if cd_conta in df["CD_CONTA"].astype(str).unique() and "ORDEM_EXERC" in df.columns:
            df = df[(df["ORDEM_EXERC"] == "ÚLTIMO") & (df["CD_CONTA"] == str(cd_conta))].copy()
        else:
            print(df.tail(3))
            raise ValueError(f"CD_CONTA '{cd_conta}' não encontrado no dataframe ou coluna 'ORDEM_EXERC' ausente. Verifique os dados carregados para o ticker '{ticker}' e os parâmetros fornecidos.")


        # Calcula o intervalo em dias entre as datas relevantes para cada linha, dependendo do tipo de demonstracao.
        if "DRE" in tipo_arquivo.upper() or "DRA" in tipo_arquivo.upper():

            df = df[["DT_REFER","DT_INI_EXERC", "DT_FIM_EXERC", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA", "origem_demonstracao"]]
            df["INTERVALO"] = (df["DT_FIM_EXERC"] - df["DT_INI_EXERC"]).dt.days
        
        else:
            df = df[["DT_REFER", "DT_FIM_EXERC", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA", "origem_demonstracao"]]
            df["INTERVALO"] = (df["DT_FIM_EXERC"] - df["DT_REFER"]).dt.days    


        # Mantem todos os DFP e filtra apenas ITR com INTERVALO < 95
        df = df[(df["origem_demonstracao"] != "itr") | (df["INTERVALO"] < 95)]


        # Prepara a série temporal ajustando os valores de acordo com a origem da demonstração (ITR ou DFP).
        if "DRE" in tipo_arquivo.upper() or "DRA" in tipo_arquivo.upper():
            
            df["ANO"] = df["DT_REFER"].dt.year
            df["VL_CONTA_ITR_SOMA"] = (df[df["origem_demonstracao"] == "itr"]
                .sort_values("DT_REFER")
                .groupby("ANO")["VL_CONTA"]
                .cumsum()
            )
        
            # Ajusta valores DFP subtraindo o acumulado do ano correspondente (VL_CONTA_ITR_SOMA)
            lista = []
            for i, (vl_conta, origem_demonstracao) in enumerate(df[['VL_CONTA', 'origem_demonstracao']].values):
                if origem_demonstracao == 'dfp':
                    vl = vl_conta - df['VL_CONTA_ITR_SOMA'].iloc[i-1]
                else:
                    vl = vl_conta
                lista.append(vl)

            df["SERIE_TRIMESTRAL"] = lista
        
        else:
            df["SERIE_TRIMESTRAL"] = df["VL_CONTA"]

        
        # Cria nome da coluna combinando DENOM_CIA e DS_CONTA (ex: "PETROBRAS_SA_LUCRO_LIQUIDO")
        denom_cia = (
            df["DENOM_CIA"].dropna().astype(str).iloc[0].strip()
            if "DENOM_CIA" in df.columns and not df["DENOM_CIA"].dropna().empty
            else "SEM_EMPRESA"
        )
        ds_conta = (
            df["DS_CONTA"].dropna().astype(str).iloc[0].strip()
            if "DS_CONTA" in df.columns and not df["DS_CONTA"].dropna().empty
            else "SEM_CONTA"
        )
        columnname = f"{denom_cia}_{ds_conta}".replace(" ", "_")

        df = df[["DT_REFER", "SERIE_TRIMESTRAL"]].reset_index(drop=True)
        df.columns = ["Date", columnname]

        return df


class ReaderSQLCVMBalancoPatrimonial:
    """Classe para leitura do Balanço Patrimonial da CVM a partir dos bancos SQLite de ITR e DFP."""

    def __init__(self):

        self.reader_itr = ReaderSQLCVMFormularioInformacoesTrimestrais()
        self.reader_dfp = ReaderSQLCVMFormularioDemonstracoesFinanceirasPadronizadas()


    def read(self, ticker: str = "VALE3", tipo_arquivo: str = "BPA_con", cd_conta: str = "3.1"):
        """Lê e combina os dados SQL do Balanço Patrimonial da CVM para ticker, tipo e código de conta."""

        df_itr = self.reader_itr.read(ticker=ticker, tipo_arquivo=tipo_arquivo)
        df_dfp = self.reader_dfp.read(ticker=ticker, tipo_arquivo=tipo_arquivo)

        df_itr["origem_demonstracao"] = "itr"
        df_dfp["origem_demonstracao"] = "dfp"

        todas_colunas = sorted(set(df_itr.columns) | set(df_dfp.columns))
        df_itr = df_itr.reindex(columns=todas_colunas)
        df_dfp = df_dfp.reindex(columns=todas_colunas)

        df = pd.concat([df_itr, df_dfp], ignore_index=True)

        for col in ["DT_REFER", "DT_FIM_EXERC", "DT_INI_EXERC"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        df = df.sort_values("DT_REFER").reset_index(drop=True)

        if cd_conta in df["CD_CONTA"].astype(str).unique() and "ORDEM_EXERC" in df.columns:
            df = df[(df["ORDEM_EXERC"] == "ÚLTIMO") & (df["CD_CONTA"] == str(cd_conta))].copy()
        else:
            print(df.tail(3))
            raise ValueError(f"CD_CONTA '{cd_conta}' não encontrado no dataframe ou coluna 'ORDEM_EXERC' ausente. Verifique os dados carregados para o ticker '{ticker}' e os parâmetros fornecidos.")

        if "DRE" in tipo_arquivo.upper() or "DRA" in tipo_arquivo.upper():

            df = df[["DT_REFER", "DT_INI_EXERC", "DT_FIM_EXERC", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA", "origem_demonstracao"]]
            df["INTERVALO"] = (df["DT_FIM_EXERC"] - df["DT_INI_EXERC"]).dt.days

        else:
            df = df[["DT_REFER", "DT_FIM_EXERC", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA", "origem_demonstracao"]]
            df["INTERVALO"] = (df["DT_FIM_EXERC"] - df["DT_REFER"]).dt.days

        df = df[(df["origem_demonstracao"] != "itr") | (df["INTERVALO"] < 95)]

        if "DRE" in tipo_arquivo.upper() or "DRA" in tipo_arquivo.upper():

            df["ANO"] = df["DT_REFER"].dt.year
            df["VL_CONTA_ITR_SOMA"] = (df[df["origem_demonstracao"] == "itr"]
                .sort_values("DT_REFER")
                .groupby("ANO")["VL_CONTA"]
                .cumsum()
            )

            lista = []
            for i, (vl_conta, origem_demonstracao) in enumerate(df[["VL_CONTA", "origem_demonstracao"]].values):
                if origem_demonstracao == "dfp":
                    vl = vl_conta - df["VL_CONTA_ITR_SOMA"].iloc[i - 1]
                else:
                    vl = vl_conta
                lista.append(vl)

            df["SERIE_TRIMESTRAL"] = lista

        else:
            df["SERIE_TRIMESTRAL"] = df["VL_CONTA"]

        denom_cia = (
            df["DENOM_CIA"].dropna().astype(str).iloc[0].strip()
            if "DENOM_CIA" in df.columns and not df["DENOM_CIA"].dropna().empty
            else "SEM_EMPRESA"
        )
        ds_conta = (
            df["DS_CONTA"].dropna().astype(str).iloc[0].strip()
            if "DS_CONTA" in df.columns and not df["DS_CONTA"].dropna().empty
            else "SEM_CONTA"
        )
        columnname = f"{denom_cia}_{ds_conta}".replace(" ", "_")

        df = df[["DT_REFER", "SERIE_TRIMESTRAL"]].reset_index(drop=True)
        df.columns = ["Date", columnname]

        return df