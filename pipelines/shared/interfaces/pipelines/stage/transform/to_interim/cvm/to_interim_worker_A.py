"""
Worker:
    to_interim_worker_a

Responsabilidades:
    Transformar RawData em InterimData: dado estruturalmente validado e tipado.
    Aplicar tipos corretos (Decimal, date, etc.), renomear colunas para o padrão interno.
    Tratar nulos técnicos (ausência de valor por limitação da fonte, não por regra de negócio).
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos RawData foram gerados, o worker irá 
    sobrescrever os arquivos InterimData existentes.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface
from pipelines.shared.interfaces.pipelines.stage_interface import RawData, InterimData
from pipelines.shared.checkpoint_values import Stage, Step, Status
from pipelines.shared.utils.io_utils import clear_directory, read_csv_with_fallback

from os import listdir
from pandas import to_datetime, to_numeric
import gc
from abc import ABC, abstractmethod


class ToInterimWorkerInterfaceA(ToInterimWorkersInterface, ABC):
    """
    Herança de ToInterimWorkersInterface:
        ``_columns_to_cast``: método abstrato que deve ser implementado pela subclasse para definir as colunas e tipos de dados a serem convertidos.
        ``_columns_to_parse_dates``: método que pode ser sobrescrito pela subclasse para definir as colunas que devem ser convertidas para datetime.
        ``_columns_to_cast_to_numeric``: método que pode ser sobrescrito pela subclasse para definir as colunas que devem ser convertidas para numérico.
        ``_cast_columns``: método que realiza a conversão das colunas para os tipos especificados em _columns_to_cast.
        ``_parse_dates``: método que realiza a conversão das colunas para datetime, se especificado em _columns_to_parse_dates.
        ``_cast_columns_numeric``: método que realiza a conversão das colunas para numérico, se especificado em _columns_to_cast_to_numeric.
    
    Métodos que a subclasse deve implementar:
        ``_columns_to_cast``: Retorna um dicionário com os nomes das colunas e os tipos de dados para os quais elas devem ser convertidas.
        ``_worker``: define a lógica do worker de to_interim.
    
    Métodos que a subclasse pode sobrescrever:
        ``_columns_to_parse_dates``: Retorna uma lista com os nomes das colunas que devem ser convertidas para o tipo de dado datetime.
        ``_columns_to_cast_to_numeric``: Retorna uma lista com os nomes das colunas que devem ser convertidas para o tipo de dado numérico.
    """
     
    
    process: str = "to_interim_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )

    
    @abstractmethod
    def _columns_to_cast(self) -> dict[str, str]:
        ...
    

    def _worker(self, ctx: PipelineContext) -> None:
        
        raw_csv_path = ctx.build_raw_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_format="csv"
        )
        
        interim_parquet_path = ctx.prepare_transformed_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_stage="to_interim", 
            subdir_format="parquet"
        )
        
        clear_directory(interim_parquet_path, logger=self.logger, remove_root=False)
        
        for filename in listdir(raw_csv_path):
            
            # Aplica em todos os arquivos CSV encontrados no diretório RawData, convertendo-os para Parquet e aplicando os tipos corretos.
            
            if filename.endswith(".csv"):
                
                raw_file_path = raw_csv_path / filename
                interim_file_path = interim_parquet_path / filename.replace('.csv', '.parquet')

                df = read_csv_with_fallback(
                    file_path=raw_file_path,
                    logger=self.logger,
                    sep=";",
                    encoding="iso-8859-1",
                    )
                
                df, dict_cast_columns_failed = self._cast_columns(df)
                df, dict_parse_invalid_dates = self._parse_dates(df)
                df, dict_cast_failed_vl_conta = self._cast_columns_numeric(df)

                df.to_parquet(interim_file_path, index=False, engine="pyarrow")

                del df
                gc.collect()
                
                _filename = filename.removesuffix('.csv')
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.TO_INTERIM,
                    step=Step.PARSE,
                    filename=f"to_interim_worker_a.success.{_filename}.json",
                    status=Status.SUCCESSFUL,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={ 
                        "parse_invalid_dates": dict_parse_invalid_dates,
                        "cast_failed_columns": dict_cast_columns_failed,
                        "cast_failed_vl_conta": dict_cast_failed_vl_conta,
                        }
                    )

