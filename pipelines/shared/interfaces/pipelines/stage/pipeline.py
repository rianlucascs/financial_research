"""
Pipeline base para orquestração de estágios.

Responsabilidades:
    Executar o fluxo principal na ordem: ``extract`` -> ``to_interim`` -> ``to_processed`` -> ``load`` -> ``compare`` -> ``retention``.
    Executar ``compare`` e ``retention`` somente quando implementados pela subclasse.
    Centralizar contexto de execução (env, run_id, paths e logging).

Notas:

    As subclasses devem definir o atributo pipeline e implementar os builders obrigatórios.
    Compare e retention são opcionais e retornam None por padrão.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_orchestrator import ExtractorOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_orchestrator import ToInterimOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_orchestrator import ToProcessedOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.load.loader_orchestrator import LoaderOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_orchestrator import ComparatorOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_orchestrator import RetentionPolicyOrchestratorInterface

from abc import ABC, abstractmethod


class PipelineInterface(ABC):
    """
    Interface para pipelines, responsável por orquestrar as etapas de extração, transformação e carga.
    
    Fluxo fixo (não sobrescrever):
        ``run``: ponto de entrada, sempre configura logging e chama os orquestradores na ordem.
    
    Métodos que a subclasse deve implementar:
        ``build_extractor_orchestrator``: define qual orquestrador de extração essa pipeline usa.
        ``build_to_interim_orchestrator``: define qual orquestrador de to_interim essa pipeline usa.
        ``build_loader_orchestrator``: define qual orquestrador de carga essa pipeline usa.
    
    Metodos opcionais que a subclasse pode implementar:
        ``build_to_processed_orchestrator``: define qual orquestrador de to_processed essa pipeline usa.
        ``build_comparator_orchestrator``: define qual orquestrador de comparação essa pipeline usa.
        ``build_retention_policy_orchestrator``: define qual orquestrador de política de retenção essa pipeline usa.
    
    Fluxo do pipeline: 
        `Extract` → `Transform.ToInterim` → `Transform.ToProcessed` → `Load` → `Compare` → `Retention`
    """
    
    
    pipeline: str # subclasse deve declarar (ex: pipeline = "pipeline_a")
    
    
    def __init__(
        self,
        env: str = "dev",
        run_id: str | None = None,
    ) -> None:

        self.ctx = PipelineContext(env=env, run_id=run_id)
    
    
    @abstractmethod
    def build_extractor_orchestrator(self) -> ExtractorOrchestratorInterface: ...
    
    
    @abstractmethod
    def build_to_interim_orchestrator(self) -> ToInterimOrchestratorInterface: ...
    
    
    def build_to_processed_orchestrator(self) -> ToProcessedOrchestratorInterface | None:
        return None
    
    
    @abstractmethod
    def build_loader_orchestrator(self) -> LoaderOrchestratorInterface: ...


    def build_comparator_orchestrator(self) -> ComparatorOrchestratorInterface | None:
        return None
    
    
    def build_retention_policy_orchestrator(self) -> RetentionPolicyOrchestratorInterface | None:
        return None
    
    
    def run(self) -> None:
        """
        Método principal da pipeline, responsável por orquestrar os orquestradores.
        """
        
        self.build_extractor_orchestrator().main(ctx=self.ctx)
        
        self.build_to_interim_orchestrator().main(ctx=self.ctx)
        
        to_processed = self.build_to_processed_orchestrator()
        if to_processed is not None:
            to_processed.main(ctx=self.ctx)
        
        self.build_loader_orchestrator().main(ctx=self.ctx)
        
        comparator = self.build_comparator_orchestrator()
        if comparator is not None:
            comparator.main(ctx=self.ctx)

        retention = self.build_retention_policy_orchestrator()
        if retention is not None:
            retention.main(ctx=self.ctx)
        
        
# def main(env: str = "dev", run_id: str | None = None):
#     """Entrypoint padrão para execução (local e container)."""
    
#     PipelineInterface(env=env, run_id=run_id).run()
    

# if __name__ == "__main__":
    
#     main()