

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.base_orchestrator import BaseOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface

from abc import abstractmethod


class ExtractorOrchestratorInterface(BaseOrchestratorInterface):
    """
    Interface para orquestradores de extração.
    """
    

    process: str = "extractor_orchestrator"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:

        super().__init__(
            pipeline=pipeline
        )
        
        
    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[ExtractorWorkersInterface]:

        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]

        ...
    