"""
Worker:
    ...

Responsabilidades:
    Transformar RawData em InterimData: dado estruturalmente validado e tipado.
    Aplicar tipos corretos (Decimal, date, etc.), renomear colunas para o padrão interno.
    Tratar nulos técnicos (ausência de valor por limitação da fonte, não por regra de negócio).

Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage_interface import StageTypes, RawData, InterimData
from pipelines.shared.checkpoint_writer_mixin import CheckpointWriterMixin

from abc import ABC, abstractmethod
from importlib import import_module
from pandas import to_datetime, to_numeric


class ToInterimWorkersInterface(CheckpointWriterMixin, ABC, StageTypes[RawData, InterimData]):
    """
    Class interface para os workers de to_interim de dados.
    
    Herança de CheckpointWriterMixin para permitir gravação de checkpoints.
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.
        
    Fluxo fixo (não sobrescrever):
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.

    Métodos que podem ser sobrescritos pela subclasse:
        ``_columns_to_parse_dates``: método que pode ser sobrescrito para definir as colunas que devem ser convertidas para datetime.
        ``_columns_to_cast_to_numeric``: método que pode ser sobrescrito para definir as colunas que devem ser convertidas para numérico.
    
    Métodos auxiliares que realizam as conversões:
        ``_cast_columns``: método que realiza a conversão das colunas para os tipos especificados em _columns_to_cast.
        ``_parse_dates``: método que realiza a conversão das colunas para datetime, se especificado em _columns_to_parse_dates.
        ``_cast_columns_numeric``: método que realiza a conversão das colunas para numérico, se especificado em _columns_to_cast_to_numeric.
    
    Métodos que a subclasse deve implementar:
        ``_columns_to_cast``: método abstrato que deve ser implementado pela subclasse para definir as colunas e tipos de dados a serem convertidos.
        ``_worker``: define a lógica do worker de to_interim.
    """
    
       
    process: str # subclasse deve declarar (ex: process = "transformer_workers_a")
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
        
        self.settings = import_module(f"pipelines.scripts.pipelines.{pipeline}.stage.pipeline_settings")
    

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
    
    
    @abstractmethod
    def _worker(self, ctx: PipelineContext) -> None:
        """
        Método que implementa a lógica do worker de to_interim.
        """

        # worker_{name} = WorkerClass(pipeline=self.pipeline)
        # worker_{name}.main(ctx=ctx)
        
        ...
        
        
    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do worker de to_interim, responsável por configurar logging e chamar o método ``_worker``.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        self._worker(ctx=ctx)