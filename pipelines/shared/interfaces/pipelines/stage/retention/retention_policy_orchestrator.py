

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.base_orchestrator import BaseOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_workers import RetentionPolicyWorkersInterface

from abc import abstractmethod


class RetentionPolicyOrchestratorInterface(BaseOrchestratorInterface):
    """
    Interface para orquestradores de retenção.
    """
    
    
    process: str = "retention_policy_orchestrator"
    

    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:

        super().__init__(
            pipeline=pipeline
        )
        
        
    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[RetentionPolicyWorkersInterface]:
        """
        Método responsável por construir os workers de retenção.
        """

        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]

        ...