"""
Worker:
    ...

Responsabilidades:
    Logica de leitura de dados de uma fonte externa (ex: banco de dados, API, arquivo) e transformação em um DataFrame pandas.

Notas:  
    A saída dos dados está padronizada, então o orquestrador pode receber os dados de diferentes pipelines e tratar de forma uniforme.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.checkpoint_writer_mixin import CheckpointWriterMixin
from pipelines.shared.interfaces.integration.stage_interface import StageTypes, SourceDataset
from pipelines.shared.checkpoint_values import Stage, Step, Status, FailurePoint, Severity

from abc import ABC
from pandas import DataFrame, read_parquet


class LoaderWorkersInterface(CheckpointWriterMixin, ABC, StageTypes[None, SourceDataset]):
    """
    Classe interface para o estágio de load.
    
    Herança de CheckpointWriterMixin para permitir gravação de checkpoints.
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.

    Fluxo fixo (não sobrescrever):
        ``_load``: método que implementa a lógica do estágio de load.
        ``main``: ponto de entrada, sempre configura logging e chama o método ``_worker``.
    """
    
    
    process: str # subclasse deve declarar (ex: process = "loader_worker_a")
    

    def __init__(
        self,
        *,
        integration: str,
        source_pipeline: str,
        data_dir: str | None = None,
        filename: str
    ) -> None:
        """
        Args:
            integration: Nome da integração (ex: "integration_a").
            source_pipeline: Nome da pipeline de origem (ex: "pipeline_a").
            data_dir: Diretório onde os dados estão armazenados (ex: "to_interim", "to_processed"). Se None, assume "to_processed".
            filename: Nome do arquivo a ser lido (ex: "data.parquet").
        """
        
        self.integration = integration
        self.source_pipeline = source_pipeline
        self.source_stage = data_dir if data_dir is not None else "to_processed"
        self.filename = filename
        self.logger = None
        
        
    def _load(self, ctx: PipelineContext) -> DataFrame:
        """
        Método que implementa a lógica do estágio de load.
        
        Sempre pegamos o snapshot mais recente da pipeline de origem, e lemos o arquivo especificado.
        """
        
        return read_parquet(
            ctx.build_transformed_path(
                ctx.current_snapshot_path(self.source_pipeline),
                subdir_stage=self.source_stage,
                subdir_format="parquet",
                ) / self.filename,
            engine="pyarrow",
        )
    
       
    def main(self, ctx: PipelineContext) -> DataFrame:
        """
        Método principal do estágio de load. Configura o logger e chama o método _load.
        """
        
        ctx.configure_logging(pipeline=self.integration, process=self.process)
        self.logger = ctx.logger
        
        try:
            
            df = self._load(ctx=ctx)
            
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.LOAD,
                step=Step.READER,
                filename=f"loader_workers.success.{self.filename}.json",
                status=Status.SUCCESSFUL,
                source=[self.integration, self.source_pipeline],
                extra={
                    "rows": len(df),
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                }
            )
            
            return df
        
        except Exception as e:
            
            self.logger.error(f"Erro ao executar o worker de load de {self.integration} para {self.source_pipeline}: {e}")
            
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.LOAD,
                step=Step.READER,
                filename=f"loader_workers.failure.{self.filename}.json",
                status=Status.FAILED,
                source=[self.integration, self.source_pipeline],
                extra={
                    "error_message": str(e),
                }
            )
            
            raise

