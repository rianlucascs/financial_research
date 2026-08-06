

from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_orchestrator import ToInterimOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface
from pipelines.shared.context import PipelineContext

from pipelines.scripts.template.stage.transform.to_iterim.to_interim_worker_A import ToInterimWorkerA


class ToInterimOrchestrator(ToInterimOrchestratorInterface):
    
    
    process = "to_interim_orchestrator"
    

    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)

    def build_workers(self, ctx: PipelineContext) -> list[ToInterimWorkersInterface]:
        
        return [
            ToInterimWorkerA(pipeline=self.pipeline),
        ]
