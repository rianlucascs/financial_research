

from pipelines.shared.context import PipelineContext
from pipelines.shared.utils.resource_monitor import resource_monitor

from abc import ABC, abstractmethod
from importlib import import_module


class BaseOrchestratorInterface(ABC):
    """
    Base compartilhada para todos os orquestradores de stage.

    Fluxo fixo (não sobrescrever):
        ``main``: configura logging e chama os workers na ordem.

    Métodos que a subclasse deve implementar:
        ``_build_workers``: retorna a lista de workers do stage.
    """

    process: str  # subclasse deve declarar (ex: process = "extractor_orchestrator")

    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:

        self.pipeline = pipeline
        self.logger = None
        
        self.settings = import_module(f"pipelines.scripts.pipelines.{pipeline}.stage.pipeline_settings")
        

    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list:

        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]

        ...

    def main(self, ctx: PipelineContext) -> None:

        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger

        self.logger.info(f"Iniciando o orquestrador: {self.process}")

        for worker in self._build_workers(ctx=ctx):

            with resource_monitor(self.logger, worker.process) as metrics:
                worker.main(ctx=ctx)

            self.logger.info(f"Worker {worker.process} finalizado com sucesso.")
