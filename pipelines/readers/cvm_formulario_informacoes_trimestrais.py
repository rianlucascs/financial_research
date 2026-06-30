

from pipelines.shared.context import PipelineContext

from datetime import date
from os.path import exists
from pandas import read_csv


class ReaderCVMFormularioDemonstracoesFinanceirasPadronizadas:
    """Classe para leitura do Formulário de Demonstrações Financeiras Padronizadas (DFP) da CVM."""


    def __init__(self):
        
        ctx = PipelineContext()
        
        # Definindo o pipeline e o processo de dados
        self.pipeline = "cvm_formulario_informacoes_trimestrais"
        self.process_data = "transform_2"
        
        # Definindo os parâmetros padrão
        self.tipo_demonstracao = "itr"
        self.tipo_empresa = "cia_aberta"
        
        # Definindo o caminho para os dados processados
        self.path = ctx.repo_root / "financial_research" / "data" / "pipelines" / self.pipeline / "processed" / self.process_data
    
     
    def read(self, ticker: str = "VALE3", tipo_arquivo: str = "BPA_con"):
        """Lê o arquivo CSV do Formulário de Demonstrações Financeiras Padronizadas (DFP) da CVM para um determinado ticker e tipo de arquivo."""
        
        if "." in ticker:
            raise ValueError("O ticker não deve conter pontos (ex.: 'VALE3' e não 'VALE3.SA').")
        
        # Definindo o nome do arquivo e o caminho completo
        file_name = f"{ticker}_{self.tipo_demonstracao}_{self.tipo_empresa}_{tipo_arquivo}_2011-{date.today().year}.csv"
        path_file = self.path / ticker / file_name
        
        if not path_file.exists():
            raise FileNotFoundError(f"O arquivo {file_name} não foi encontrado no caminho {path_file}.")
        
        # Lendo o arquivo CSV
        df = read_csv(path_file)

        return df
    
    
    