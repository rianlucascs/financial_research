

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_orchestrator import ToInterimOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface

from pipelines.scripts.pipelines.cvm_formulario_informacoes_trimestrais.stage.transform.to_interim.to_interim_worker_A import ToInterimWorkerA


class ToInterimOrchestrator(ToInterimOrchestratorInterface):
    
    
    process: str = "to_interim_orchestrator"
    

    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)


    def _build_workers(self, ctx: PipelineContext) -> list[ToInterimWorkersInterface]:
        
        return [
            ToInterimWorkerA(pipeline=self.pipeline),
        ]
