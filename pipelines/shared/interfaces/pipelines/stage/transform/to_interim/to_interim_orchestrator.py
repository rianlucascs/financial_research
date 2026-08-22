

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.base_orchestrator import BaseOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface

from abc import abstractmethod


class ToInterimOrchestratorInterface(BaseOrchestratorInterface):
    """
    Interface para orquestradores de to_interim.
    """
    
    
    process: str = "to_interim_orchestrator"
    

    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[ToInterimWorkersInterface]:

        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]

        ...
    