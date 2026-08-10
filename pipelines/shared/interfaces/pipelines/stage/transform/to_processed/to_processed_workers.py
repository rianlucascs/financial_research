"""
Worker:
    ...

Responsabilidades:
    Concatenar dados, aplicar filtros, renomear colunas, aplicar tipos corretos (Decimal, date, etc.), 
    tratar nulos técnicos (ausência de valor por limitação da fonte, não por regra de negócio), e gerar ProcessedData.
    
Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage_interface import StageTypes, InterimData, ProcessedData
from pipelines.shared.checkpoint_writer_mixin import CheckpointWriterMixin

from abc import ABC, abstractmethod


class ToProcessedWorkersInterface(CheckpointWriterMixin, ABC, StageTypes[InterimData, ProcessedData]):
    """
    Class interface para os workers de to_processed de dados.
    
    Herança de CheckpointWriterMixin para permitir gravação de checkpoints.
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.
        
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama o método ``_worker``.

    Métodos que a subclasse deve implementar:
        ``_worker``: define a lógica do worker de to_processed.
    """
    
       
    process: str # subclasse deve declarar (ex: process = "to_processed_workers_a")
    
    
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
        Método que implementa a lógica do worker de to_processed.
        """

        # worker_{name} = WorkerClass(pipeline=self.pipeline)
        # worker_{name}.main(ctx=ctx)
        
        ...
        
        
    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do worker de to_processed, responsável por configurar logging e chamar o método ``_worker``.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        self._worker(ctx=ctx)