

from pipelines.shared.context import PipelineContext

from pandas import DataFrame
from typing import Literal
from pathlib import Path
from datetime import date
from pandas import read_sql
import sqlite3
from abc import ABC


class ReaderSQLiteCVMInterface(ABC):
    """
    Classe interface para leitura de arquivos SQLite do CVM.
    
    As classes filhas devem implementar o método ``read``.
    """
    

    
    def __init__(
        self,
        pipeline: str = Literal["cvm_formulario_demonstracoes_financeiras_padronizadas", "cvm_formulario_informacoes_trimestrais"],
        prefix: str = Literal["dfp", "itr"]
    ) -> None:
        
        self.pipeline = pipeline
        self.prefix = prefix
        
        self.ctx = PipelineContext()
    
    
    def _build_db_path(self, filename: str) -> Path:
        
        file_path = self.ctx.data_dir / self.ctx.current_snapshot_path(self.pipeline) / "load" / f"{filename}.db"
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist.")
        
        return file_path
    
    
    def read(
        self, 
        demonstration_code: Literal[ 
                                    'BPA_con', 'BPA_ind', 
                                    'BPP_con', 'BPP_ind', 
                                    'DFC_MD_con', 'DFC_MD_ind', 
                                    'DFC_MI_con', 'DFC_MI_ind', 
                                    'DMPL_con', 'DMPL_ind', 
                                    'DRA_con', 'DRA_ind', 
                                    'DRE_con', 'DRE_ind', 
                                    'DVA_con', 'DVA_ind'
                                    ]
        ) -> DataFrame:
        
        table_name = f"{self.prefix}_cia_aberta_{demonstration_code}_2011-{date.today().year}"
        db_path = self._build_db_path(table_name)
        
        with sqlite3.connect(db_path) as connection:
            return read_sql(
                f"SELECT * FROM \"{table_name}\"",
                connection,
            )
