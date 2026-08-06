

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_workers import RetentionPolicyWorkersInterface
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_orchestrator import RetentionPolicyOrchestratorInterface


class RetentionPolicyOrchestrator(RetentionPolicyOrchestratorInterface):

    
    process: str # subclasse deve declarar (ex: process = "retention_policy_orchestrator_a")


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