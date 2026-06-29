

from pipelines.shared.context import PipelineContext
from .extract import ExtractCVMFormularioDemonstracoesFinanceirasPadronizadas
from .transform_1 import TransformCVMFormularioDemonstracoesFinanceirasPadronizadasStep1
from .transform_2 import TransformCVMFormularioDemonstracoesFinanceirasPadronizadasStep2
from .load import LoadCVMFormularioDemonstracoesFinanceirasPadronizadas


class PipelineCVMFormularioDemonstracoesFinanceirasPadronizadas:


    def __init__(self, env: str = "dev", run_id: str | None = None):

        self.ctx = PipelineContext(env=env, run_id=run_id)

        self.pipeline = "cvm_formulario_demonstracoes_financeiras_padronizadas"


    def run(self):

        # # Responsável pela extração dos formulários de demonstrações financeiras padronizadas da CVM.
        # extract = ExtractCVMFormularioDemonstracoesFinanceirasPadronizadas(pipeline=self.pipeline)
        # extract.main(ctx=self.ctx) 

        # # Responsável pela transformação dos formulários de demonstrações financeiras padronizadas da CVM.  
        # transform_1 = TransformCVMFormularioDemonstracoesFinanceirasPadronizadasStep1(pipeline=self.pipeline)
        # transform_1.main(ctx=self.ctx)
        
        # # Responsável pela transformação dos formulários de demonstrações financeiras padronizadas da CVM.
        # transform_2 = TransformCVMFormularioDemonstracoesFinanceirasPadronizadasStep2(pipeline=self.pipeline)
        # transform_2.main(ctx=self.ctx)

        # Responsável pelo carregamento dos dados processados em banco SQLite.
        load = LoadCVMFormularioDemonstracoesFinanceirasPadronizadas(pipeline=self.pipeline)
        load.main(ctx=self.ctx)


def main(env: str = "dev", run_id: str | None = None):
    """
    Entrypoint padrão para execução (local e container).
    """
    
    p = PipelineCVMFormularioDemonstracoesFinanceirasPadronizadas(env=env, run_id=run_id)
    p.run()


if __name__ == "__main__":
    
    main()
