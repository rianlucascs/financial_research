

from pipelines.shared.context import PipelineContext

from datetime import date
from pandas import DataFrame, read_csv, to_datetime


class ReaderBCBHistoricoTaxasJuros:
    """Leitor do histórico de taxas de juros do BCB a partir do CSV bruto."""


    def __init__(self):

        ctx = PipelineContext()

        self.pipeline = "bcb_historico_taxas_juros"
        self.path = ctx.path_raw(self.pipeline)
        
        self.file_name = "bcb_historico_taxas_juros.csv"

        # Definindo o caminho para os dados processados
        self.path = ctx.repo_root / "financial_research" / "data" / "pipelines" / self.pipeline / "raw" / self.file_name


    def _to_float(self, series):
        """Converte colunas numéricas no padrão brasileiro para float."""

        return (
            series.astype(str)
            .str.strip()
            .replace({"": None, "n/a": None, "nan": None})
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )


    def read(self, start_date: str | date | None = None, end_date: str | date | None = None) -> DataFrame:
        """Lê o histórico do BCB e retorna um DataFrame tratado.

        Args:
            start_date: Filtra linhas com Data da Reunião maior ou igual a essa data.
            end_date: Filtra linhas com Data da Reunião menor ou igual a essa data.
        """

        if not self.path.exists():
            raise FileNotFoundError(
                f"O arquivo {self.file_name} não foi encontrado no caminho {self.path}."
            )

        df = read_csv(self.path)

        df["Data da Reunião"] = to_datetime(df["Data da Reunião"], format="%d/%m/%Y", errors="coerce")
        df["Data da Divulgação"] = to_datetime(df["Data da Divulgação"], format="%d/%m/%Y", errors="coerce")

        periodo = df["Período de Vigência"].fillna("").str.split(" - ", n=1, expand=True)
        df["Início da Vigência"] = to_datetime(periodo[0], format="%d/%m/%Y", errors="coerce")
        df["Fim da Vigência"] = to_datetime(periodo[1], format="%d/%m/%Y", errors="coerce")

        for column in [
            "Taxa Selic Meta (%)",
            "Taxa Selic Over (%)",
            "Taxa Selic Meta Anterior (%)",
            "Taxa Selic Over Anterior (%)",
        ]:
            df[column] = self._to_float(df[column])

        if start_date is not None:
            start_date = to_datetime(start_date, errors="coerce")
            df = df[df["Data da Reunião"] >= start_date]

        if end_date is not None:
            end_date = to_datetime(end_date, errors="coerce")
            df = df[df["Data da Reunião"] <= end_date]

        df = df.sort_values("Data da Reunião").reset_index(drop=True)

        return df
        
