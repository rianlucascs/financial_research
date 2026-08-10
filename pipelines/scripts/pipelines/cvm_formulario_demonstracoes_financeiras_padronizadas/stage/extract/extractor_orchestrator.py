

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_orchestrator import ExtractorOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface

from pipelines.scripts.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.extract.extractor_worker_A import ExtractorWorkerA
from pipelines.scripts.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.extract.extractor_worker_B import ExtractorWorkerB


class ExtractorOrchestrator(ExtractorOrchestratorInterface):


    process: str = "extractor_orchestrator"
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)


    def _build_workers(self, ctx: PipelineContext) -> list[ExtractorWorkersInterface]:
        
        return [
            ExtractorWorkerA(pipeline=self.pipeline),
            ExtractorWorkerB(pipeline=self.pipeline),
        ]
