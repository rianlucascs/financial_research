

from pipelines.shared.context import PipelineContext
from .extract import ExtractBCBHistoricoTaxasJurosSettings
from .load import LoadBCBHistoricoTaxasJuros


class PipelineBCBHistoricoTaxasJuros:
    
    
    def __init__(self, env: str = "dev", run_id: str | None = None):

        self.ctx = PipelineContext(env=env, run_id=run_id)

        self.pipeline = "bcb_historico_taxas_juros"
        
    
    def run(self):
        
        # Responsável pela extração dos dados do histórico de taxas de juros do Banco Central do Brasil
        extract = ExtractBCBHistoricoTaxasJurosSettings(pipeline=self.pipeline)
        extract.main(ctx=self.ctx)

        # Responsável por carregar o CSV bruto em banco SQLite.
        load = LoadBCBHistoricoTaxasJuros(pipeline=self.pipeline)
        load.main(ctx=self.ctx)
    
    
def main(env: str = "dev", run_id: str | None = None):
    """
    Entrypoint padrão para execução (local e container).
    """
    
    p = PipelineBCBHistoricoTaxasJuros(env=env, run_id=run_id)
    p.run()
    

if __name__ == "__main__":
    
    main()
