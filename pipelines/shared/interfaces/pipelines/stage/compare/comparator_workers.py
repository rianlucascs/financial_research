"""
Worker:
    ...

Responsabilidades:
    Compara os arquivos de dados do snapshot atual com o snapshot anterior, identificando adições, remoções e alterações nos dados.
    
Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage_interface import ProcessedData, StageTypes, SnapshotDrift
from pipelines.shared.checkpoint_writer_mixin import CheckpointWriterMixin

from abc import ABC, abstractmethod


class ComparatorWorkersInterface(CheckpointWriterMixin, ABC, StageTypes[ProcessedData, SnapshotDrift]):
    """
    Esta é a interface para os comparadores de DataFrames.

    Herança de CheckpointWriterMixin para permitir gravação de checkpoints.
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.
        
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama o método ``_worker``.
        
    Métodos que a subclasse deve implementar:
        ``_worker``: define a lógica do worker de comparação.
    """
    
    
    process: str # subclasse deve declarar (ex: process = "comparator_workers_a")


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
        
    
    @abstractmethod
    def _worker(self, ctx: PipelineContext) -> None:
        """
        Compara dois DataFrames: ``previous`` e ``current``.
        """
        ...


    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do worker de comparação, responsável por configurar logging e chamar o método ``_worker``.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        self._worker(ctx=ctx)
