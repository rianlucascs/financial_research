

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_workers import RetentionPolicyWorkersInterface


from abc import ABC, abstractmethod


class RetentionPolicyOrchestratorInterface(ABC):
    """
    Interface para orquestradores de retenção, responsável por orquestrar os workers de retenção.
    
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama os workers na ordem.

    Métodos que a subclasse deve implementar:
        ``build_workers``: define quais workers essa orquestração usa.
    """
    
    
    process: str # subclasse deve declarar (ex: process = "retention_policy_orchestrator")


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None


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
        
        
    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do orquestrador, responsável por orquestrar os workers de retenção.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger

        for worker in self._build_workers(ctx=ctx):
            worker.main(ctx=ctx)