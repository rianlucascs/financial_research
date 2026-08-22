

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.base_orchestrator import BaseOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_workers import ToProcessedWorkersInterface

from abc import abstractmethod


class ToProcessedOrchestratorInterface(BaseOrchestratorInterface):
    """
    Interface para orquestradores de to_processed.
    """
    
    
    process: str = "to_processed_orchestrator"
    

    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[ToProcessedWorkersInterface]:

        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]

        ...
            
        
    