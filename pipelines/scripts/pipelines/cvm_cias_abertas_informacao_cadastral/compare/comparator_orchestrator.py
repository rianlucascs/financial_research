

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_orchestrator import ComparatorOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_workers import ComparatorWorkersInterface

from pipelines.scripts.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.compare.comparator_worker_A import ComparatorWorkerB


class ComparatorOrchestrator(ComparatorOrchestratorInterface):


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
    
    
    def _build_workers(self, ctx: PipelineContext) -> list[ComparatorWorkersInterface]:
        """
        Método responsável por construir os workers de comparação.
        """
        
        return [
            ComparatorWorkerB(pipeline=self.pipeline)
        ]
