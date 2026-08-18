

from pipelines.shared.context import PipelineContext

from abc import ABC
from pathlib import Path
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Literal
from pandas import read_parquet, DataFrame


@dataclass
class HistoricalDataLocation:
    
    pipeline: str
    snapshot_directory: str
    foldername: str
    filename: str
    snapshot: str | None = None


class HistoricalDataValidator:
    """
    Valida localizações e nomes de arquivos de dados históricos.
    """
    
    
    @staticmethod
    def validate_filename(historical_data_location: HistoricalDataLocation) -> None:
        
        if historical_data_location.snapshot_directory == "snapshot_drift" and not (
            "added" in historical_data_location.filename.lower() or
            "changed" in historical_data_location.filename.lower() or
            "removed" in historical_data_location.filename.lower()
        ):
            raise ValueError("O parâmetro 'snapshot_directory' deve conter 'added', 'changed' ou 'removed' quando for igual a 'snapshot_drift'.")

        if ".parquet" in historical_data_location.foldername:
            raise ValueError("O parâmetro 'foldername' não deve conter a extensão '.parquet'.")
    
    
    @classmethod
    def validate_read_inputs(cls, historical_data_location: HistoricalDataLocation) -> None:
        cls.validate_filename(historical_data_location)
        
  
class ReaderHistoricalDataInterface(ABC):
    """
    Classe abstrata para leitura do histórico de mudanças dos pipelines.
    """
    
    
    def __init__(
        self,
        pipeline: str,
        snapshot_directory: Literal["snapshot_drift"],
        foldername: str,
        filename: str,
        snapshot: str | None = None
    ) -> None:
        
        self.pipeline = pipeline
        self.snapshot_directory = snapshot_directory
        self.foldername = foldername
        self.filename = filename
        self.snapshot = snapshot
        
        self.ctx = PipelineContext()


    def _build_parquet_path(self, snapshot: str | None = None) -> Path:
        """
        Retorna o caminho do arquivo Parquet no snapshot informado ou nos últimos 4 dias.
        
        Args:
            ``snapshot`` (str | None): Diretório do snapshot específico. (YYYY-MM-DD). Se None, busca nos últimos 4 dias.
        """
        
        
        for days in [0, 1, 2, 3]:
             
            file_path = (
                self.ctx.build_snapshot_drift_path(
                    pipeline=self.pipeline,
                    subdir=(date.today() - timedelta(days=days)).strftime("%Y-%m-%d") if snapshot is None else snapshot,
                )
                / self.foldername
                / self.filename
            )
            
            print(f"\n\n{file_path}\n\n")
            
            if file_path.exists():
                
                return file_path

            if self.snapshot is not None:
                # Se um snapshot específico foi fornecido e não existe, não continue procurando.
                raise FileNotFoundError(f"Para o snapshot específico '{snapshot}', o arquivo não foi encontrado.")
        
        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado.")
         
    
    def read(self) -> DataFrame:
        
        HistoricalDataValidator.validate_read_inputs(
            HistoricalDataLocation(
                pipeline=self.pipeline,
                snapshot_directory=self.snapshot_directory,
                foldername=self.foldername,
                filename=self.filename,
                snapshot=self.snapshot
            )
        )
        print(self._build_parquet_path(self.snapshot))
        return read_parquet(
            self._build_parquet_path(self.snapshot),
            engine="pyarrow"
            )