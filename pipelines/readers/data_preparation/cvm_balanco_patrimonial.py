

from pipelines.readers.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.reader_parquet_cvm import ReaderParquetCVM as ReaderParquetCVMDFP
from pipelines.readers.pipelines.cvm_formulario_informacoes_trimestrais.reader_parquet_cvm import ReaderParquetCVM as ReaderParquetCVMITR

from dataclasses import dataclass
from pandas import DataFrame, concat


@dataclass
class EquityIdentifier:
    
    denom_cia: str | None = None
    cnpj_cia: str | None = None
    cd_cvm: str | None = None


@dataclass
class AccountIdentifier:

    cd_conta: str | None = None
    ds_conta: str | None = None


class CVMDataValidator:


    @staticmethod
    def validate_equity(search_equity: EquityIdentifier) -> None:
        if not any([search_equity.denom_cia, search_equity.cnpj_cia, search_equity.cd_cvm]):
            raise ValueError("Ao menos um dos parâmetros 'denom_cia', 'cnpj_cia' ou 'cd_cvm' deve ser fornecido.")


    @staticmethod
    def validate_account(search_account: AccountIdentifier | None) -> None:
        if search_account is None:
            raise ValueError("O parâmetro 'search_account' deve ser fornecido.")

        if not any([
            search_account.cd_conta is not None and str(search_account.cd_conta).strip(),
            search_account.ds_conta is not None and str(search_account.ds_conta).strip(),
        ]):
            raise ValueError("Ao menos um dos parâmetros 'cd_conta' ou 'ds_conta' deve ser fornecido.")

        if search_account.cd_conta is not None and not any(c.isdigit() for c in str(search_account.cd_conta)):
            raise ValueError("O parâmetro 'cd_conta' deve conter pelo menos um dígito numérico.")


    @staticmethod
    def validate_demonstration_code(demonstration_code: str) -> None:
        if not demonstration_code or not str(demonstration_code).strip():
            raise ValueError("O parâmetro 'demonstration_code' deve ser informado.")


    @classmethod
    def validate_read_inputs(cls, search_equity: EquityIdentifier, demonstration_code: str, search_account: AccountIdentifier | None) -> None:
        cls.validate_equity(search_equity)
        cls.validate_demonstration_code(demonstration_code)
        cls.validate_account(search_account)


class DemonstrationValueAggregator:


    @staticmethod
    def calc_dre_or_dra(df: DataFrame) -> DataFrame:

        df = df.copy()

        df["ANO"] = df["DT_REFER"].dt.year

        df["VL_CONTA_TRI"] = df["VL_CONTA"]

        itr = df[df["ORIGEM_FORMULARIO"] == "ITR"].copy()

        itr["VL_CONTA_ACUMULADO"] = (
            itr
            .sort_values("DT_REFER")
            .groupby("ANO")["VL_CONTA"]
            .cumsum()
        )

        ultimo_itr = (
            itr
            .sort_values("DT_REFER")
            .groupby("ANO")
            .tail(1)
            [["ANO", "VL_CONTA_ACUMULADO"]]
        )

        df = df.merge(
            ultimo_itr,
            on="ANO",
            how="left",
        )

        mask_dfp = df["ORIGEM_FORMULARIO"] == "DFP"

        df.loc[mask_dfp, "VL_CONTA_TRI"] = (
            df.loc[mask_dfp, "VL_CONTA"]
            - df.loc[mask_dfp, "VL_CONTA_ACUMULADO"]
        )

        return df.drop(columns=["VL_CONTA_ACUMULADO"])


    @classmethod
    def calculate_aggregated_values(cls, df: DataFrame, demonstration_code: str) -> DataFrame:

        if ("DRE" in demonstration_code) or ("DRA" in demonstration_code):
            return cls.calc_dre_or_dra(df)

        result = df.copy()
        result["VL_CONTA_TRI"] = result["VL_CONTA"]
        return result


class CVMDataFilter:


    @staticmethod
    def filter_equity_by_identifier(df: DataFrame, search_equity: EquityIdentifier) -> DataFrame:
        for attr, value in search_equity.__dict__.items():
            if value is not None:
                filtered = df[df[attr.upper()] == str(value)]
                if not filtered.empty:
                    return filtered
        raise ValueError(f"Nenhum registro encontrado para os parâmetros fornecidos em {search_equity}.")


    @staticmethod
    def filter_cd_conta_or_ds_conta(df: DataFrame, search_account: AccountIdentifier) -> DataFrame:
        filtered = df.copy()

        for attr, value in search_account.__dict__.items():
            if value is not None:
                filtered = filtered[filtered[attr.upper()] == str(value)]
                if not filtered.empty:
                    return filtered

        available_accounts = (
            df[["CD_CONTA", "DS_CONTA"]]
            .drop_duplicates()
            .sort_values(["CD_CONTA", "DS_CONTA"])
        )

        print("\nContas disponíveis:")
        print(available_accounts.to_string(index=False))

        raise ValueError(f"Nenhum registro encontrado para os parâmetros fornecidos em {search_account}.")


    @staticmethod
    def filter_by_ordem_exerc(df: DataFrame, ordem_exerc: str = "ÚLTIMO") -> DataFrame:
        if "ORDEM_EXERC" not in df.columns:
            raise ValueError("Coluna 'ORDEM_EXERC' não encontrada no DataFrame.")

        filtered = df[df["ORDEM_EXERC"] == ordem_exerc]

        if filtered.empty:
            raise ValueError(f"Nenhum registro com ORDEM_EXERC == '{ordem_exerc}'.")

        return filtered


    @staticmethod
    def filter_by_intervalo_exerc(df: DataFrame, demonstration_code: str, intervalo_exerc: int = 95) -> DataFrame:
        if "INTERVALO_EXERC" not in df.columns:
            if ("BPA" in demonstration_code) or ("BPP" in demonstration_code):
                return df
            raise ValueError("Coluna 'INTERVALO_EXERC' não encontrada no DataFrame.")

        filtered = df[(df["ORIGEM_FORMULARIO"] != "ITR") | (df["INTERVALO_EXERC"] < intervalo_exerc)]

        if filtered.empty:
            raise ValueError(f"Nenhum registro com INTERVALO_EXERC == '{intervalo_exerc}'.")

        return filtered


class CVMBalancoPatrimonial:
    

    def _reader_itr_parquet_cvm(self, demonstration_code: str) -> DataFrame:
        return ReaderParquetCVMITR().read(demonstration_code=demonstration_code).copy()
    

    def _reader_dfp_parquet_cvm(self, demonstration_code: str) -> DataFrame:
        return ReaderParquetCVMDFP().read(demonstration_code=demonstration_code).copy()
    
    
    def _concat_dataframes(self, demonstration_code: str) -> DataFrame:

        itr_data: DataFrame = self._reader_itr_parquet_cvm(demonstration_code)
        dfp_data: DataFrame = self._reader_dfp_parquet_cvm(demonstration_code)
        
        if any(df.empty for df in [itr_data, dfp_data]):
            raise ValueError(f"Não foi possível ler os dados para o código de demonstração '{demonstration_code}'.")
        
        combined = concat([itr_data, dfp_data], ignore_index=True)
        
        return combined
        
    
    def _filter_equity_by_identifier(self, df: DataFrame, search_equity: EquityIdentifier) -> DataFrame:
        return CVMDataFilter.filter_equity_by_identifier(df, search_equity)


    def _filter_cd_conta_or_ds_conta(self, df: DataFrame, search_account: AccountIdentifier) -> DataFrame:
        return CVMDataFilter.filter_cd_conta_or_ds_conta(df, search_account)


    def _filter_by_ordem_exerc(self, df: DataFrame, ordem_exerc: str = "ÚLTIMO") -> DataFrame:
        return CVMDataFilter.filter_by_ordem_exerc(df, ordem_exerc)


    def _filter_by_intervalo_exerc(self, df: DataFrame, demonstration_code: str, intervalo_exerc: int = 95) -> DataFrame:
        return CVMDataFilter.filter_by_intervalo_exerc(df, demonstration_code, intervalo_exerc)


    def _calc_DRE_or_DRA(self, df: DataFrame) -> DataFrame:
        return DemonstrationValueAggregator.calc_dre_or_dra(df)


    def _calculate_aggregated_values(self, df: DataFrame, demonstration_code: str) -> DataFrame:
        return DemonstrationValueAggregator.calculate_aggregated_values(df, demonstration_code)
    

    def read(self, search_equity: EquityIdentifier, demonstration_code: str, search_account: AccountIdentifier | None = None) -> DataFrame:

        CVMDataValidator.validate_read_inputs(search_equity, demonstration_code, search_account)

        df = self._concat_dataframes(demonstration_code).sort_values("DT_REFER").reset_index(drop=True)

        df = df.copy()

        df = self._filter_equity_by_identifier(df, search_equity)

        df = self._filter_cd_conta_or_ds_conta(df, search_account)
        df = self._filter_by_ordem_exerc(df, ordem_exerc="ÚLTIMO")

        df = self._filter_by_intervalo_exerc(df, demonstration_code, intervalo_exerc=95)

        df = self._calculate_aggregated_values(df, demonstration_code)

        df = df.sort_values(by=["DT_REFER"])

        return df
    
    
if __name__ == "__main__":
    
    cvm_balanco_patrimonial = CVMBalancoPatrimonial()
    demonstration_code = "DRE_con"

    df = cvm_balanco_patrimonial.read(
        search_equity=EquityIdentifier(denom_cia='VALE S.A.', cnpj_cia="33.592.510/0001-54", cd_cvm="4170"),
        demonstration_code=demonstration_code,
        search_account=AccountIdentifier(cd_conta="3.03", ds_conta="Receita Líquida de Vendas e/ou Serviços"),
    )
    
    print(df)
