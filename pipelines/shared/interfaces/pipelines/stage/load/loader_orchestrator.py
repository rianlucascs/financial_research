

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.base_orchestrator import BaseOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.load.loader_workers import LoaderWorkersInterface

from abc import abstractmethod


class LoaderOrchestratorInterface(BaseOrchestratorInterface):
    """
    Interface para orquestradores de carga.
    """

    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[LoaderWorkersInterface]:

        # return [
        #     WorkerA(pipeline=self.pipeline),
        #     WorkerB(pipeline=self.pipeline),
        # ]

        ...