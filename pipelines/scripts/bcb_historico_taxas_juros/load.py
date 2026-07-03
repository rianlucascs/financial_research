from pipelines.shared.checkpoint_values import (
    FAILURE_FILE_DETECTION,
    FAILURE_IO_ERROR,
    STATUS_FAILED,
    STATUS_NO_FILE_DETECTED,
    STATUS_SUCCESSFUL,
)

from .settings import (
    CHECKPOINT_STAGE_LOAD,
    CHECKPOINT_STEP_LOAD,
)

from pipelines.shared.checkpoint_contract import build_checkpoint_payload

from pandas import read_csv, to_datetime
import sqlite3
import gc


class LoadBCBHistoricoTaxasJuros:
    """Carrega o CSV bruto do BCB em um banco SQLite, em uma tabela única."""


    def __init__(self, pipeline: str):

        self.pipeline = pipeline
        self.process = "load"
        self.logger = None


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


    def _gravar_checkpoint_load(self, item_name, status, failure_point, ctx, extra=None):

        extra_payload = {"item_name": item_name}
        if extra:
            extra_payload.update(extra)

        try:
            payload = build_checkpoint_payload(
                pipeline=self.pipeline,
                stage=CHECKPOINT_STAGE_LOAD,
                step=CHECKPOINT_STEP_LOAD,
                status=status,
                run_id=ctx.run_id,
                environment=ctx.env,
                failure_point=failure_point,
                source="BCB",
                extra=extra_payload,
            )
            ctx.write_checkpoint(
                self.pipeline,
                CHECKPOINT_STAGE_LOAD,
                CHECKPOINT_STEP_LOAD,
                item_name,
                payload,
            )

        except Exception:
            self.logger.exception(f"Falha ao gravar checkpoint de load para '{item_name}'")


    def load(self, ctx):
        """Lê o CSV bruto do BCB e carrega os dados normalizados em SQLite."""

        path_raw = ctx.path_raw(self.pipeline)
        path_load = ctx.path_load(self.pipeline)
        path_load.mkdir(parents=True, exist_ok=True)

        csv_path = path_raw / "bcb_historico_taxas_juros.csv"
        db_path = path_load / "bcb.db"
        table_name = "bcb_historico_taxas_juros"

        self.logger.info(f"Iniciando load do pipeline '{self.pipeline}' para o banco '{db_path}'.")

        if not csv_path.exists():
            self.logger.error(f"CSV bruto não encontrado em '{csv_path}'.")

            self._gravar_checkpoint_load(
                item_name=table_name,
                status=STATUS_NO_FILE_DETECTED,
                failure_point=FAILURE_FILE_DETECTION,
                ctx=ctx,
                extra={"csv_path": str(csv_path), "db_path": str(db_path)},
            )

            raise FileNotFoundError(f"CSV bruto não encontrado: {csv_path}")

        try:
            df = read_csv(csv_path)

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

        except Exception:
            self.logger.exception(f"Erro ao ler ou tratar o CSV '{csv_path}'.")

            self._gravar_checkpoint_load(
                item_name=table_name,
                status=STATUS_FAILED,
                failure_point=FAILURE_IO_ERROR,
                ctx=ctx,
                extra={"csv_path": str(csv_path), "db_path": str(db_path)},
            )

            raise

        with sqlite3.connect(db_path) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)

        rows = len(df)

        self.logger.info(f"Tabela '{table_name}' carregada com sucesso ({rows} linhas).")

        self._gravar_checkpoint_load(
            item_name=table_name,
            status=STATUS_SUCCESSFUL,
            failure_point=None,
            ctx=ctx,
            extra={"csv_path": str(csv_path), "db_path": str(db_path), "rows": rows},
        )

        del df

        gc.collect()

        self.logger.info(f"Load do pipeline '{self.pipeline}' concluído. Banco: '{db_path}'.")


    def main(self, ctx) -> None:

        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger

        if ctx.env == "dev":
            pass

        if ctx.env == "prod":
            pass

        # Responsável pelo carregamento do CSV bruto em banco SQLite.
        self.load(ctx)