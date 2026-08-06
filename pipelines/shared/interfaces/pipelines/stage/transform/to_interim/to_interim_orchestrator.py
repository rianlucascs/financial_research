

from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface
from pipelines.shared.context import PipelineContext

from abc import ABC, abstractmethod


class ToInterimOrchestratorInterface(ABC):
    """
    Interface para orquestradores de to_interim, responsável por orquestrar os workers de to_interim.
    
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama os workers na ordem.

    Métodos que a subclasse deve implementar:
        ``build_workers``: define quais workers essa orquestração usa.
    """
    
    
    process: str # subclasse deve declarar (ex: process = "to_interim_orchestrator_a")
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
    
    
    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[ToInterimWorkersInterface]:
        """
        Método responsável por construir os workers de to_interim.
        """
        
        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]
        
        ...
    
    
    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do orquestrador, responsável por orquestrar os workers de to_interim.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        for worker in self._build_workers(ctx=ctx):
            worker.main(ctx=ctx)
            
        
    