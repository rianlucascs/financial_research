

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_orchestrator import ExtractorOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface

from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.extract.extractor_worker_A import ExtractorWorkerA


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
        ]
