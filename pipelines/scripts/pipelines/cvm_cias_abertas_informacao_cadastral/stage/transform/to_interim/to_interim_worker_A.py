"""
Worker:
    to_interim_worker_a

Responsabilidades:
    ...
    
Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface
from pipelines.shared.interfaces.pipelines.stage_interface import RawData, InterimData
from pipelines.shared.utils.io_utils import read_csv_with_fallback, clear_directory
from pipelines.shared.checkpoint_values import Stage, Step, Status

from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.pipeline_settings import filename

from pandas import to_datetime
import gc


class ToInterimWorkerA(ToInterimWorkersInterface):
    
    
    process: str = "to_interim_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)
        
        
    def _cast_columns(self, df: RawData) -> InterimData:

        column_types = {
            
            'CNPJ_CIA': "string",
            'DENOM_SOCIAL': "string",
            'DENOM_COMERC': "string",
            'MOTIVO_CANCEL': "string",
            'SIT': "string",
            'CD_CVM': "string",
            'SETOR_ATIV': "string",
            'TP_MERC': "string",
            'CATEG_REG': "string",
            'SIT_EMISSOR': "string",
            'CONTROLE_ACIONARIO': "string",
            'TP_ENDER': "string",
            'LOGRADOURO': "string",
            'COMPL': "string",
            'BAIRRO': "string",
            'MUN': "string",
            'UF': "string",
            'PAIS': "string",
            'CEP': "string",
            'DDD_TEL': "string",
            'TEL': "string",
            'DDD_FAX': "string",
            'FAX': "string",
            'EMAIL': "string",
            'TP_RESP': "string",
            'RESP': "string",
            'LOGRADOURO_RESP': "string",
            'COMPL_RESP': "string",
            'BAIRRO_RESP': "string",
            'MUN_RESP': "string",
            'UF_RESP': "string",
            'PAIS_RESP': "string",
            'CEP_RESP': "string",
            'DDD_TEL_RESP': "string",
            'TEL_RESP': "string",
            'DDD_FAX_RESP': "string",
            'FAX_RESP': "string",
            'EMAIL_RESP': "string",
            'CNPJ_AUDITOR': "string",
            'AUDITOR': "string",
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
            "DT_REG",
            "DT_CONST",
            "DT_CANCEL",
            "DT_INI_SIT",
            "DT_INI_CATEG",
            "DT_INI_SIT_EMISSOR",
            "DT_INI_RESP",
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
    
    
    def _worker(self, ctx: PipelineContext) -> None:
        
        build_raw_path_csv = (
            ctx.prepare_raw_path(pipeline=self.pipeline, subdir_format="csv") 
            / filename
        )
        
        interim_parquet_path = (
            ctx.prepare_transformed_path(
                ctx.current_snapshot_path(self.pipeline), 
                subdir_stage="to_interim", 
                subdir_format="parquet") 
        )
        
        clear_directory(interim_parquet_path, logger=self.logger, remove_root=False)
        
        try:
        
            df = read_csv_with_fallback(build_raw_path_csv, self.logger)
        
        except Exception as e:
            
            self.logger.error(f"Falha ao ler o arquivo CSV '{build_raw_path_csv}': {e}")
            
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.TO_INTERIM,
                step=Step.PARSE,
                filename=f"to_interim_worker_a.failed.{filename}.json",
                status=Status.FAILED,
                source="cvm_cias_abertas_informacao_cadastral",
                extra={"error": str(e)},
            )
        
            return
        
        df, dict_cast_columns_failed = self._cast_columns(df)
        df, dict_parse_invalid_dates = self._parse_dates(df)
        
        interim_file_path = interim_parquet_path / filename.replace('.csv', '.parquet')
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
            source="cvm_cias_abertas_informacao_cadastral",
            extra={
                "parse_invalid_dates": dict_parse_invalid_dates,
                "cast_failed_columns": dict_cast_columns_failed,
                }
            )

if __name__ == "__main__":
    
    worker = ToInterimWorkerA(pipeline="cvm_cias_abertas_informacao_cadastral")
    worker.main(ctx=PipelineContext())
