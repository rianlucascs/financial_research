

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_workers import ToProcessedWorkersInterface

from abc import ABC, abstractmethod


class ToProcessedOrchestratorInterface(ABC):
    """
    Interface para orquestradores de to_processed, responsável por orquestrar os workers de to_processed.
    
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama os workers na ordem.

    Métodos que a subclasse deve implementar:
        ``build_workers``: define quais workers essa orquestração usa.
    """
    
    
    process: str # subclasse deve declarar (ex: process = "to_processed_orchestrator")
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
    
    
    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[ToProcessedWorkersInterface]:
        """
        Método responsável por construir os workers de to_processed.
        """
        
        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]
        
        ...
    
    
    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do orquestrador, responsável por orquestrar os workers de to_processed.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        for worker in self._build_workers(ctx=ctx):
            worker.main(ctx=ctx)
            
        
    