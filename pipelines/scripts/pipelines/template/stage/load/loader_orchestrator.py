

from pipelines.shared.interfaces.pipelines.stage.load.loader_orchestrator import LoaderOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.load.loader_workers import LoaderWorkersInterface
from pipelines.shared.context import PipelineContext

from pipelines.scripts.pipelines.template.stage.load.loader_worker_A import LoaderWorkerA


class LoaderOrchestrator(LoaderOrchestratorInterface):
    
    
    process = "loader_orchestrator"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)

    def build_workers(self, ctx: PipelineContext) -> list[LoaderWorkersInterface]:
        
        return [
            LoaderWorkerA(pipeline=self.pipeline),
        ]
