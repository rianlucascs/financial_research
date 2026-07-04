

from pipelines.shared.context import PipelineContext
from .extract import ExtractB3IndicesSegmentosSetoriais
from .load import LoadB3IndicesSegmentosSetoriais


class PipelineB3IndicesSegmentosSetoriais:
    
    
    def __init__(self, env: str = "dev", run_id: str | None = None):

        self.ctx = PipelineContext(env=env, run_id=run_id)

        self.pipeline = "b3_indices_segmentos_setoriais"


    def run(self):
        
        # Responsavel pela extração dos dados da B3 (Bolsa de Valores do Brasil) para os índices e segmentos setoriais.
        extract = ExtractB3IndicesSegmentosSetoriais(pipeline=self.pipeline)
        extract.main(ctx=self.ctx)

        # Responsável por carregar os CSVs brutos dos índices em banco SQLite.
        load = LoadB3IndicesSegmentosSetoriais(pipeline=self.pipeline)
        load.main(ctx=self.ctx)
    

def main(env: str = "dev", run_id: str | None = None):
    """
    Entrypoint padrão para execução (local e container).
    """
    
    p = PipelineB3IndicesSegmentosSetoriais(env=env, run_id=run_id)
    p.run()
    

if __name__ == "__main__":
    
    main()
