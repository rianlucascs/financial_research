"""
Worker:
    to_interim_worker_a

Responsabilidades:
    Transformar RawData em InterimData: dado estruturalmente validado e tipado.
    Aplicar tipos corretos (Decimal, date, etc.), renomear colunas para o padrão interno.
    Tratar nulos técnicos (ausência de valor por limitação da fonte, não por regra de negócio).
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos RawData foram gerados, o worker irá sobrescrever os arquivos InterimData existentes.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface
from pipelines.shared.interfaces.stage_interface import RawData, InterimData
from pipelines.shared.checkpoint_values import Stage, Step, Status
from pipelines.shared.utils.io_utils import clear_directory

from pipelines.scripts.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.pipeline_settings import current_snapshot_path

from os import listdir
from pandas import read_csv, DataFrame, to_datetime, to_numeric
from pandas.errors import ParserError
import gc


class ToInterimWorkerA(ToInterimWorkersInterface):
    
    
    process: str = "to_interim_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)

    
    def _cast_column_vl_conta(self, df: RawData) -> tuple[InterimData, dict[str, str]]:
        
        cast_failed: dict[str, str] = {}
        
        if "VL_CONTA" in df.columns:
            
            values = to_numeric(
                df["VL_CONTA"],
                errors="coerce",
            )
            
            df["VL_CONTA"] = values
            
            try:
                
                df["VL_CONTA"] = df["VL_CONTA"].astype("float64")
                
            except (ValueError, TypeError) as exc:
                
                cast_failed["VL_CONTA"] = "float64"
                
                self.logger.warning(f"Não foi possível converter 'VL_CONTA' para 'float64': {exc}")
        
        return df, cast_failed
    
    
    def _cast_columns(self, df: RawData) -> InterimData:

        column_types = {
            "CNPJ_CIA": "string",
            "VERSAO": "Int64",
            "DENOM_CIA": "string",
            "CD_CVM": "string",
            "GRUPO_DFP": "string",
            "MOEDA": "string",
            "ESCALA_MOEDA": "string",
            "ORDEM_EXERC": "string",
            "CD_CONTA": "string",
            "DS_CONTA": "string",
            "ST_CONTA_FIXA": "string",
        }
        
        cast_failed: dict[str, str] = {}
        
        for col, dtype in column_types.items():
            
            if col not in df.columns:
                continue
            
            try:
                
                df[col] = df[col].astype(dtype)
                
            except (ValueError, TypeError) as exc:
                
                cast_failed[col] = str(dtype)
                
                self.logger.warning(f"Não foi possível converter '{col}' para '{dtype}': {exc}")

        return df, cast_failed
    
    
    def _parse_dates(self, df: RawData) -> tuple[InterimData, dict[str, int]]:

        date_columns = [
            "DT_REFER",
            "DT_INI_EXERC",
            "DT_FIM_EXERC",
        ]

        parse_invalid_dates: dict[str, int] = {}
        
        for col in date_columns:
            
            if col in df.columns:
            
                df[col] = to_datetime(df[col], errors="coerce")
                
                invalid_dates = df[col].isna().sum()
                
                if invalid_dates > 0:
                
                    parse_invalid_dates[col] = invalid_dates
                    
                    self.logger.warning(f"Foram encontradas {invalid_dates} datas inválidas em {col}.")
                    
        return df, parse_invalid_dates


    def _read_raw_csv(self, raw_file_path) -> DataFrame:

        try:
            
            return read_csv(raw_file_path, sep=";", encoding="iso-8859-1", dtype=str)
        
        except ParserError as exc:
            
            self.logger.warning(f"Falha no parser em '{raw_file_path}' ({exc}). Aplicando fallback com engine='python'.")

            try:
                
                return read_csv(
                    raw_file_path,
                    sep=";",
                    encoding="iso-8859-1",
                    dtype=str,
                    engine="python",
                )

            except Exception as exc:
                
                self.logger.error(f"Falha ao ler '{raw_file_path}' com fallback: {exc}")
                
                raise 


    def _worker(self, ctx: PipelineContext) -> None:
        
        raw_csv_path = ctx.build_raw_path(current_snapshot_path(self.pipeline), subdir_format="csv")
        interim_parquet_path = ctx.prepare_transformed_path(current_snapshot_path(self.pipeline), subdir_stage="to_interim", subdir_format="parquet")
        
        clear_directory(interim_parquet_path, logger=self.logger, remove_root=False)
        
        for filename in listdir(raw_csv_path):
            
            if filename.endswith(".csv"):
                
                raw_file_path = raw_csv_path / filename
                interim_file_path = interim_parquet_path / filename.replace('.csv', '.parquet')

                df = self._read_raw_csv(raw_file_path)
                
                df, dict_cast_columns_failed = self._cast_columns(df)
                df, dict_parse_invalid_dates = self._parse_dates(df)
                df, dict_cast_failed_vl_conta = self._cast_column_vl_conta(df)

                df.to_parquet(interim_file_path, index=False, engine="pyarrow")

                _filename = filename.removesuffix('.csv')
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.TO_INTERIM,
                    step=Step.PARSE,
                    filename=f"to_interim_worker_a.success.{_filename}.json",
                    status=Status.SUCCESSFUL,
                    source="cvm_formulario_demonstracoes_financeiras_padronizadas",
                    extra={
                        "parse_invalid_dates": dict_parse_invalid_dates,
                        "cast_failed_columns": dict_cast_columns_failed,
                        "cast_failed_vl_conta": dict_cast_failed_vl_conta,
                        }
                    )
                
                del df
                gc.collect()
                
                
if __name__ == "__main__":
    
    worker = ToInterimWorkerA(pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas")
    worker.main(ctx=PipelineContext())
