

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_workers import RetentionPolicyWorkersInterface
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_orchestrator import RetentionPolicyOrchestratorInterface
from pipelines.scripts.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.retention.retention_policy_worker_A import RetentionPolicyWorkerA


class RetentionPolicyOrchestrator(RetentionPolicyOrchestratorInterface):

    
    process: str = "retention_policy_orchestrator"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None


    def _build_workers(self, ctx: PipelineContext) -> list[RetentionPolicyWorkersInterface]:
        """
        Método responsável por construir os workers de retenção.
        """

        return [
            RetentionPolicyWorkerA(pipeline=self.pipeline),
        ]
        