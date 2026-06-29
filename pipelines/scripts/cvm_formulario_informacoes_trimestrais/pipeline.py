

from pipelines.shared.context import PipelineContext
from .extract import ExtractCVMFormularioInformacoesTrimestrais
from .transform_1 import TransformCVMFormularioInformacoesTrimestraisStep1
from .transform_2 import TransformCVMFormularioInformacoesTrimestraisStep2
from .load import LoadCVMFormularioInformacoesTrimestrais


class PipelineCVMFormularioInformacoesTrimestrais:


    def __init__(self, env: str = "dev", run_id: str | None = None):

        self.ctx = PipelineContext(env=env, run_id=run_id)

        self.pipeline = "cvm_formulario_informacoes_trimestrais"


    def run(self):

        # Responsável pela extração dos formulários de informações trimestrais da CVM.
        extract = ExtractCVMFormularioInformacoesTrimestrais(pipeline=self.pipeline)
        extract.main(ctx=self.ctx) 

        # Responsável pela transformação dos formulários de informações trimestrais da CVM.  
        transform_1 = TransformCVMFormularioInformacoesTrimestraisStep1(pipeline=self.pipeline)
        transform_1.main(ctx=self.ctx)
        
        # Responsável pela transformação dos formulários de informações trimestrais da CVM.
        transform_2 = TransformCVMFormularioInformacoesTrimestraisStep2(pipeline=self.pipeline)
        transform_2.main(ctx=self.ctx)

        # Responsável pelo carregamento dos dados processados em banco SQLite.
        load = LoadCVMFormularioInformacoesTrimestrais(pipeline=self.pipeline)
        load.main(ctx=self.ctx)
        

def main(env: str = "dev", run_id: str | None = None):
    """
    Entrypoint padrão para execução (local e container).
    """
    
    p = PipelineCVMFormularioInformacoesTrimestrais(env=env, run_id=run_id)
    p.run()


if __name__ == "__main__":
    
    main()
