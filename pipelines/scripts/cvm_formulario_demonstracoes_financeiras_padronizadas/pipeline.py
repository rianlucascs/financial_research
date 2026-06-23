
from pipelines.shared.context import PipelineContext
from .extract import ExtractCVMFormularioDemonstracoesFinanceirasPadronizadas
from .transform import TransformCVMFormularioDemonstracoesFinanceirasPadronizadas


class PipelineCVMFormularioDemonstracoesFinanceirasPadronizadas:
    

    def __init__(self, env: str = "dev", run_id: str | None = None):

        self.ctx = PipelineContext(env=env, run_id=run_id)

        self.pipeline = "cvm_formulario_demonstracoes_financeiras_padronizadas"


    def run(self):

        extract = ExtractCVMFormularioDemonstracoesFinanceirasPadronizadas(pipeline=self.pipeline)
        extract.main(ctx=self.ctx) 

        transform = TransformCVMFormularioDemonstracoesFinanceirasPadronizadas(pipeline=self.pipeline)
        transform.main(ctx=self.ctx)
        

def main(env: str = "dev", run_id: str | None = None):
    """
    Entrypoint padrão para execução (local e container).
    """
    
    p = PipelineCVMFormularioDemonstracoesFinanceirasPadronizadas(env=env, run_id=run_id)
    p.run()


if __name__ == "__main__":
    
    main()
