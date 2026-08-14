

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.base_orchestrator import BaseOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_workers import RetentionPolicyWorkersInterface

from abc import abstractmethod


class RetentionPolicyOrchestratorInterface(BaseOrchestratorInterface):
    """
    Interface para orquestradores de retenção.
    """

    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[RetentionPolicyWorkersInterface]:

        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]

        ...