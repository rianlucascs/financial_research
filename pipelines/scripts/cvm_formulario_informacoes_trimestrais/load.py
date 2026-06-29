
from pipelines.shared.checkpoint_values import (
    FAILURE_PROCESSED_EXCEPTION,
    STATUS_FAILED,
    STATUS_SUCCESSFUL,
)

from .settings import (
    DEMONSTRACOES,
    CHECKPOINT_STAGE_LOAD,
    CHECKPOINT_STEP_LOAD,
)

from pipelines.shared.checkpoint_contract import build_checkpoint_payload

from pandas import concat, read_csv
import sqlite3
import gc


class LoadCVMFormularioInformacoesTrimestrais:
    """Carrega os CSVs processados pelo transform_2 em um banco SQLite,
    criando uma tabela por tipo de demonstração financeira."""


    def __init__(self, pipeline: str):
        self.pipeline = pipeline
        self.process = "load"
        self.logger = None


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
                source="CVM",
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
        """Lê os CSVs de transform_2 e os carrega no SQLite, uma tabela por demonstração."""

        path_transform_2 = ctx.path_processed(self.pipeline, "transform_2")
        path_load = ctx.path_load(self.pipeline)
        path_load.mkdir(parents=True, exist_ok=True)

        db_path = path_load / "itr.db"

        self.logger.info(f"Iniciando load do pipeline '{self.pipeline}' para o banco '{db_path}'.")

        ticker_dirs = sorted([d for d in path_transform_2.iterdir() if d.is_dir()])

        self.logger.info(f"{len(ticker_dirs)} diretório(s) de ticker encontrado(s) em transform_2.")

        with sqlite3.connect(db_path) as conn:

            for demonstracao in DEMONSTRACOES:

                self.logger.info(f"Carregando demonstração '{demonstracao}'.")

                frames = []

                for ticker_dir in ticker_dirs:
                    ticker = ticker_dir.name

                    matching = list(ticker_dir.glob(f"{ticker}_itr_cia_aberta_{demonstracao}_*.csv"))

                    if not matching:
                        self.logger.debug(f"Nenhum arquivo para ticker '{ticker}' / demonstração '{demonstracao}'. Pulando.")
                        continue

                    csv_path = matching[0]

                    try:
                        df = read_csv(csv_path, sep=",", decimal=",", encoding="utf-8")
                        df.insert(0, "TICKER", ticker)
                        frames.append(df)

                    except Exception:
                        self.logger.exception(f"Erro ao ler '{csv_path}'.")
                        self._gravar_checkpoint_load(
                            item_name=f"{demonstracao}_{ticker}",
                            status=STATUS_FAILED,
                            failure_point=FAILURE_PROCESSED_EXCEPTION,
                            ctx=ctx,
                            extra={"demonstracao": demonstracao, "ticker": ticker, "csv_path": str(csv_path)},
                        )

                if not frames:
                    self.logger.warning(f"Nenhum dado encontrado para a demonstração '{demonstracao}'. Pulando.")
                    continue

                df_all = concat(frames, ignore_index=True)
                df_all.to_sql(demonstracao, conn, if_exists="replace", index=False)

                rows = len(df_all)
                self.logger.info(f"Demonstração '{demonstracao}' carregada com sucesso ({rows} linhas).")

                self._gravar_checkpoint_load(
                    item_name=demonstracao,
                    status=STATUS_SUCCESSFUL,
                    failure_point=None,
                    ctx=ctx,
                    extra={"demonstracao": demonstracao, "rows": rows},
                )

                del df_all
                del frames
                gc.collect()

        self.logger.info(f"Load do pipeline '{self.pipeline}' concluído. Banco: '{db_path}'.")


    def main(self, ctx) -> None:

        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger

        if ctx.env == "dev":
            pass
        
        if ctx.env == "prod":
            pass
        
        # Responsável pelo carregamento dos dados processados em banco SQLite.
        self.load(ctx)

