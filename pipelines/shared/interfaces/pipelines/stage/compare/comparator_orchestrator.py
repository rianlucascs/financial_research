"""
Orquestrador:

Responsabilidades:
    Orquestrar a execução de múltiplos workers de comparação.
    
Notas:
    ...
"""

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_workers import ComparatorWorkersInterface

from abc import ABC, abstractmethod


class ComparatorOrchestratorInterface(ABC):
    
    
    process: str # subclasse deve declarar (ex: process = "comparator_orchestrator")


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
    
    
    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[ComparatorWorkersInterface]:
        """
        Método responsável por construir os workers de comparação.
        """
        
        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]
        
        ...
        
        
    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do orquestrador, responsável por orquestrar os workers de comparação.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        for worker in self._build_workers(ctx=ctx):
            worker.main(ctx=ctx)