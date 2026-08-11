

from pipelines.shared.context import PipelineContext

from abc import ABC, abstractmethod


class IntegrationInterface(ABC):
    """
    Fluxo do integration:
        `Load` → `Align` → `Join/Merge` → `Join/Merge` → `Validate` → `Persist/Export` → `Retention`
    """
    
    
    integration: str  # subclasse deve declarar (ex: integration = "integration_a")


    def __init__(
        self,
        env: str = "dev",
        run_id: str | None = None,
    ) -> None:

        self.ctx = PipelineContext(env=env, run_id=run_id)

    
    def run(self) -> None:
        """
        Método principal da pipeline, responsável por orquestrar os orquestradores.
        """
        ...
        

# def main(env: str = "dev", run_id: str | None = None):
#     """Entrypoint padrão para execução (local e container)."""
    
#     IntegrationInterface(env=env, run_id=run_id).run()
    

# if __name__ == "__main__":
    
#     main()