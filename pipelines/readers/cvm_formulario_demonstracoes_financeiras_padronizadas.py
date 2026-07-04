

from pipelines.shared.context import PipelineContext

from datetime import date
import sqlite3
from pandas import read_csv, read_sql_query


class ReaderCSVCVMFormularioDemonstracoesFinanceirasPadronizadas:
    """Classe para leitura do Formulário de Demonstrações Financeiras Padronizadas (DFP) da CVM."""


    def __init__(self):
        
        ctx = PipelineContext()
        
        # Definindo o pipeline e o processo de dados
        self.pipeline = "cvm_formulario_demonstracoes_financeiras_padronizadas"
        self.process_data = "transform_2"
        
        # Definindo os parâmetros padrão
        self.tipo_demonstracao = "dfp"
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


class ReaderSQLCVMFormularioDemonstracoesFinanceirasPadronizadas:
    """Classe para leitura do DFP da CVM a partir do SQLite de load."""


    def __init__(self):

        ctx = PipelineContext()

        self.pipeline = "cvm_formulario_demonstracoes_financeiras_padronizadas"
        self.tipo_demonstracao = "dfp"
        self.tipo_empresa = "cia_aberta"

        repo_root = ctx.repo_root / "financial_research"
        if not repo_root.exists():
            repo_root = ctx.repo_root

        self.path = repo_root / "data" / "pipelines" / self.pipeline / "load" / "dfp.db"


    def read(self, ticker: str = "VALE3", tipo_arquivo: str = "BPA_con"):
        """Lê o DFP da CVM do SQLite para um ticker e tipo de arquivo."""

        if "." in ticker:
            raise ValueError("O ticker não deve conter pontos (ex.: 'VALE3' e não 'VALE3.SA').")

        if not self.path.exists():
            raise FileNotFoundError(f"O banco SQLite não foi encontrado no caminho {self.path}.")

        query = f'SELECT * FROM "{tipo_arquivo}" WHERE TICKER = ?'

        with sqlite3.connect(self.path) as conn:
            df = read_sql_query(query, conn, params=[ticker.upper()])

        if df.empty:
            raise ValueError(f"Nenhum dado encontrado no SQLite para ticker '{ticker}' e tipo '{tipo_arquivo}'.")

        return df
    
    
    