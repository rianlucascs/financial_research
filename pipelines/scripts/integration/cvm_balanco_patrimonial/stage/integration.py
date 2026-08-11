

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.integration.stage.integration import IntegrationInterface

from pipelines.scripts.integration.cvm_balanco_patrimonial.stage.integration_settings import demonstration_codes
from pipelines.scripts.integration.cvm_balanco_patrimonial.stage.loader_workers import LoaderWorkers

from datetime import date


class Integration(IntegrationInterface):
    
    
    integration: str = "cvm_balanco_patrimonial"

 
    def __init__(
        self,
        env: str = "dev",
        run_id: str | None = None,
    ) -> None:

        self.ctx = PipelineContext(env=env, run_id=run_id)
    
    
    def run(self) -> None:
        
        current_year = date.today().year
        
        for demonstration_code in demonstration_codes:
        
            workers = [
                LoaderWorkers(
                    integration=self.integration, 
                    source_pipeline="cvm_formulario_informacoes_trimestrais",
                    filename=f"itr_cia_aberta_{demonstration_code}_2011-{current_year}.parquet",
                ),
                LoaderWorkers(
                    integration=self.integration, 
                    source_pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas",
                    filename=f"dfp_cia_aberta_{demonstration_code}_2011-{current_year}.parquet",
                )
            ]
        
            dataframes = [worker.main(self.ctx) for worker in workers]
        

def main(env: str = "dev", run_id: str | None = None):
    
    Integration(env=env, run_id=run_id).run()
    

if __name__ == "__main__":
    
    main()