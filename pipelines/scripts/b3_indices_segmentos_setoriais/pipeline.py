

from pipelines.shared.context import PipelineContext


class PipelineB3IndicesSegmentosSetoriais:
    
    
    def __init__(self, env: str = "dev", run_id: str | None = None):

        self.ctx = PipelineContext(env=env, run_id=run_id)

        self.pipeline = "b3_indices_segmentos_setoriais"


    def run(self):
        pass
    

def main(env: str = "dev", run_id: str | None = None):
    """
    Entrypoint padrão para execução (local e container).
    """
    
    p = PipelineB3IndicesSegmentosSetoriais(env=env, run_id=run_id)
    p.run()
    

if __name__ == "__main__":
    
    main()
