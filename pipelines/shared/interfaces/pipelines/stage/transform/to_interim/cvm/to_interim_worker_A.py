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
    Métodos que a subclasse deve implementar:
        ``_columns_to_cast``: Retorna um dicionário com os nomes das colunas e os tipos de dados para os quais elas devem ser convertidas.
    
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
        """
        Retorna um dicionário com os nomes das colunas e os tipos de dados para os quais elas devem ser convertidas.
        """
        # return {
        #     "CNPJ_CIA": "string",
        #     "VERSAO": "Int64",
        #     "DENOM_CIA": "string",
        #     "CD_CVM": "string",
        #     "GRUPO_DFP": "string",
        #     "MOEDA": "string",
        #     "ESCALA_MOEDA": "string",
        #     "ORDEM_EXERC": "string",
        #     "CD_CONTA": "string",
        #     "DS_CONTA": "string",
        #     "ST_CONTA_FIXA": "string",
        # }
        ...
    
    
    def _columns_to_parse_dates(self) -> list[str] | None:
        """
        Retorna uma lista com os nomes das colunas que devem ser convertidas para o tipo de dado datetime.
        """
        # return [
        #     "DT_REFER",
        #     "DT_INI_EXERC",
        #     "DT_FIM_EXERC",
        # ]
        return None
    
    
    def _columns_to_cast_to_numeric(self) -> list[str] | None: 
        """
        Retorna uma lista com os nomes das colunas que devem ser convertidas para o tipo de dado numérico.
        """
        # return [
        #     "VL_CONTA",
        # ]
        return None
 
 
    def _cast_columns(self, df: RawData) -> tuple[InterimData, dict[str, str]]:
        """
        Converte as colunas do DataFrame para os tipos especificados em _columns_to_cast.
        Retorna o DataFrame convertido e um dicionário com as colunas que não puderam ser convertidas e os tipos para os 
        quais tentaram ser convertidas.
        """
        
        
        cast_failed: dict[str, str] = {}
        
        for col, dtype in self._columns_to_cast().items():
            
            if col not in df.columns:
                
                # cast_failed[col] = str(dtype)
                
                # self.logger.warning(f"A coluna '{col}' não foi encontrada no DataFrame.")
                
                continue
            
            try:
                
                df[col] = df[col].astype(dtype)
                
            except (ValueError, TypeError) as exc:
                
                cast_failed[col] = str(dtype)
                
                self.logger.warning(f"Não foi possível converter '{col}' para '{dtype}': {exc}")

        return df, cast_failed
          

    def _parse_dates(self, df: RawData) -> tuple[InterimData, dict[str, int]]:
        """
        Converte as colunas do DataFrame para o tipo datetime, se especificado em _columns_to_parse_dates.
        Retorna o DataFrame convertido e um dicionário com as colunas que não puderam ser convertidas e a quantidade 
        de valores inválidos encontrados.
        """
        

        columns_dates = self._columns_to_parse_dates()

        parse_invalid_dates: dict[str, int] = {}
        
        if columns_dates is None:
            return df, parse_invalid_dates
        
        for col in columns_dates:
            
            if col in df.columns:
            
                df[col] = to_datetime(df[col], errors="coerce")
                
                invalid_dates = df[col].isna().sum()
                
                if invalid_dates > 0:
                
                    parse_invalid_dates[col] = invalid_dates
                    
                    self.logger.warning(f"Foram encontradas {invalid_dates} datas inválidas em {col}.")
            
            # else:
                
            #     parse_invalid_dates[col] = 0
                
            #     self.logger.warning(f"A coluna '{col}' não foi encontrada no DataFrame.")
                
                    
        return df, parse_invalid_dates
    
    
    def _cast_columns_numeric(self, df: RawData) -> tuple[InterimData, dict[str, str]]:
        """
        Converte as colunas do DataFrame para o tipo numérico, se especificado em _columns_to_cast_to_numeric.
        Retorna o DataFrame convertido e um dicionário com as colunas que não puderam ser convertidas e os tipos para os 
        quais tentaram ser convertidas.
        """
        
        
        cast_failed: dict[str, str] = {}
        
        columns_to_cast_numeric = self._columns_to_cast_to_numeric()
        
        if columns_to_cast_numeric is None:
            return df, cast_failed
        
        for col in columns_to_cast_numeric:
            
            if col in df.columns:
                
                values = to_numeric(
                    df[col],
                    errors="coerce",
                )
                
                df[col] = values
                
                try:
                    
                    df[col] = df[col].astype("float64")
                    
                except (ValueError, TypeError) as exc:
                    
                    cast_failed[col] = "float64"
                    
                    self.logger.warning(f"Não foi possível converter '{col}' para 'float64': {exc}")

            # else:
                
            #     cast_failed[col] = "float64"
                
            #     self.logger.warning(f"A coluna '{col}' não foi encontrada no DataFrame.")
            
        return df, cast_failed


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

