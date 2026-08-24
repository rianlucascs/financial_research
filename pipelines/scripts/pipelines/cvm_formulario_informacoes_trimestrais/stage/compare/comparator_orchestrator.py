

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_orchestrator import ComparatorOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_workers import ComparatorWorkersInterface

from pipelines.scripts.pipelines.cvm_formulario_informacoes_trimestrais.stage.compare.comparator_worker_A import ComparatorWorkerA


class ComparatorOrchestrator(ComparatorOrchestratorInterface):


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )
    
    
    def _build_workers(self, ctx: PipelineContext) -> list[ComparatorWorkersInterface]:
        
        return [
            ComparatorWorkerA(pipeline=self.pipeline)
        ]
