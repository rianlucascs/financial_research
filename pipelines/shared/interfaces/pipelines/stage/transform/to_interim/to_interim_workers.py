"""
Worker:
    ...

Responsabilidades:
    Transformar RawData em InterimData: dado estruturalmente validado e tipado.
    Aplicar tipos corretos (Decimal, date, etc.), renomear colunas para o padrão interno.
    Tratar nulos técnicos (ausência de valor por limitação da fonte, não por regra de negócio).

Notas:
    ...
"""


from pipelines.shared.interfaces.stage_interface import StageTypes, RawData, InterimData
from pipelines.shared.context import PipelineContext
from pipelines.shared.checkpoint_writer_mixin import CheckpointWriterMixin

from abc import ABC, abstractmethod


class ToInterimWorkersInterface(CheckpointWriterMixin, ABC, StageTypes[RawData, InterimData]):
    """
    Class interface para os workers de to_interim de dados.
    
    Herança de CheckpointWriterMixin para permitir gravação de checkpoints.
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.
        
    Fluxo fixo (não sobrescrever):
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.

    Métodos que a subclasse deve implementar:
        ``_worker``: define a lógica do worker de to_interim.
    """
    
       
    process: str # subclasse deve declarar (ex: process = "transformer_workers_a")
    
    
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
        Método que implementa a lógica do worker de to_interim.
        """

        # worker_{name} = WorkerClass(pipeline=self.pipeline)
        # worker_{name}.main(ctx=ctx)
        
        ...
        
        
    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do worker de to_interim, responsável por configurar logging e chamar o método ``_worker``.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        self._worker(ctx=ctx)