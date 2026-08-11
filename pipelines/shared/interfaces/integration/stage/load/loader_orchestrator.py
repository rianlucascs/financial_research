"""
Orquestrador:
    ...

Responsabilidades:
    Orquestrar a execução de múltiplos workers de load.
    
Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.integration.stage.load.loader_workers import LoaderWorkersInterface

from abc import ABC, abstractmethod
from pandas import DataFrame


class LoaderOrchestratorInterface(ABC):
    """
    Interface para orquestradores de load.
    
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama os workers na ordem.

    Métodos que a subclasse deve implementar:
        ``_build_workers``: define quais workers essa orquestração usa. Editar apenas 'source_pipeline' e 'integration' (ex: LoaderWorkersInterface(integration=self.integration, source_pipeline="")).
    """
    
    
    process: str # subclasse deve declarar (ex: process = "loader_orchestrator")

    
    def __init__(
        self,
        *,
        integration: str,
    ) -> None:
        
        self.integration = integration
        self.logger = None
    
    
    @abstractmethod
    def _build_workers(self, ctx: PipelineContext) -> list[LoaderWorkersInterface]:
        """
        Método responsável por construir os workers de load.
        """
        
        # return [
        #     LoaderWorkersInterface(integration=self.integration, source_pipeline=""),
        #     LoaderWorkersInterface(integration=self.integration, source_pipeline=""),
        # ]
        
        ...
    
    
    def main(self, ctx: PipelineContext) -> dict[str, DataFrame]:
        """
        Método principal do orquestrador, responsável por orquestrar os workers de load.
        """
        
        ctx.configure_logging(pipeline=self.integration, process=self.process)
        self.logger = ctx.logger
        
        dataframes = {}
        
        for worker in self._build_workers(ctx=ctx):
            dataframes[worker.source_pipeline] = worker.main(ctx=ctx)
        
        return dataframes