"""
Orquestrador:

Responsabilidades:
    Orquestrar a execução de múltiplos workers de comparação.
    
Notas:
    ...
"""

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.base_orchestrator import BaseOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_workers import ComparatorWorkersInterface

from abc import abstractmethod


class ComparatorOrchestratorInterface(BaseOrchestratorInterface):
    """
    Interface para orquestradores de comparação.
    """

    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[ComparatorWorkersInterface]:

        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]

        ...