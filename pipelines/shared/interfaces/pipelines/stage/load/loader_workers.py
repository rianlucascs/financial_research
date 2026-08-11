"""
Worker:
    ...
    
Responsabilidades:
    Lógica de carregamento de dados em um destino final, como um banco de dados ou um sistema de armazenamento.
    
Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.checkpoint_writer_mixin import CheckpointWriterMixin

from abc import ABC, abstractmethod


class LoaderWorkersInterface(CheckpointWriterMixin, ABC):
    """
    Class interface para os workers de carregamento de dados.
    
    Herança de CheckpointWriterMixin para permitir gravação de checkpoints.
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.
    
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama o método ``_worker``.

    Métodos que a subclasse deve implementar:
        ``_worker``: define a lógica do worker de carregamento.
    """

    process: str  # subclasse deve declarar (ex: process = "loader_workers_a")


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
        Método que implementa a lógica do worker de carregamento.
        """
        ...


    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do worker de carregamento, responsável por configurar logging e chamar o método ``_worker``.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        self._worker(ctx=ctx)