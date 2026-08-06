"""
Worker:

Responsabilidades:
    ...
    
Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.stage_interface import RawData, StageTypes
from pipelines.shared.checkpoint_writer_mixin import CheckpointWriterMixin

from abc import ABC, abstractmethod


class ExtractorWorkersInterface(CheckpointWriterMixin, ABC, StageTypes[None, RawData]):
    """
    Class interface para os workers de extração de dados.

    Herança de CheckpointWriterMixin para permitir gravação de checkpoints.
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.
        
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama o método ``_worker``.

    Métodos que a subclasse deve implementar:
        ``_worker``: define a lógica do worker de extração.
    """
    
       
    process: str # subclasse deve declarar (ex: process = "extractor_workers_a")
    
    
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
        Método que implementa a lógica do worker de extração.
        """
        ...
        
        
    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do worker de extração, responsável por configurar logging e chamar o método ``_worker``.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        self._worker(ctx=ctx)