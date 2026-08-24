"""
Worker:
    to_processed_worker_a

Responsabilidades:
    Concatena os CSVs brutos anuais (2011 até o ano corrente) de cada tipo de formulário ITR (CVM).
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos InterimData foram gerados, o worker irá sobrescrever os arquivos Parquet processados existentes.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_workers import ToProcessedWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Step, Status
from pipelines.shared.utils.io_utils import remove_file

from datetime import date
from pandas import DataFrame, read_parquet
import pyarrow.parquet as pq
import pyarrow as pa
import gc


class ToProcessedWorkerA(ToProcessedWorkersInterface):
    
    
    process: str = "to_processed_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )

    
    def _add_derived_columns(self, df: DataFrame) -> DataFrame:
        
        df["ORIGEM_FORMULARIO"] = "ITR" 
        
        if ("DT_INI_EXERC" in df.columns) and ("DT_FIM_EXERC" in df.columns):
            df["INTERVALO_EXERC"] = (df["DT_FIM_EXERC"] - df["DT_INI_EXERC"]).dt.days
            
        return df
    
    
    def _worker(self, ctx: PipelineContext) -> None:
        
        current_year = date.today().year
        
        processed_parquet_path = ctx.prepare_transformed_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_stage="to_processed", 
            subdir_format="parquet"
        )
        
        interim_parquet_path = ctx.build_transformed_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_stage="to_interim", 
            subdir_format="parquet"
        )
        
        for demonstration_code in getattr(self.settings, "demonstration_codes", []):
            
            # Monta o caminho do arquivo Parquet processado final
            filename = f"itr_cia_aberta_{demonstration_code}_2011-{current_year}.parquet"
            parquet_file_path = processed_parquet_path / filename
            
            remove_file(parquet_file_path, logger=self.logger)
            
            writer = None
            
            try:
                
                for year in range(2011, current_year + 1):
                    
                    # Monta o caminho do arquivo Parquet intermediário
                    interim_file_path = interim_parquet_path / f"itr_cia_aberta_{demonstration_code}_{year}.parquet"
                    
                    df_interim = read_parquet(interim_file_path, engine="pyarrow")
                    
                    if df_interim.empty:
                        
                        del df_interim
                        gc.collect()
                        
                        self.logger.error(f"Arquivo Parquet intermediário vazio: {interim_file_path}. Pulando este arquivo.")
                        
                        continue
                    
                    df_interim = self._add_derived_columns(df_interim)
                    
                    table = pa.Table.from_pandas(
                        df_interim,
                        preserve_index=False,
                    )
                    
                    del df_interim
                    gc.collect()
                    
                    if writer is None:
                        writer = pq.ParquetWriter(
                            parquet_file_path,
                            table.schema,
                        )

                    writer.write_table(table)
                    
                    del table
                    gc.collect()
             
            finally:
                
                if writer is not None:
                    writer.close()
                
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.TO_PROCESSED,
                step=Step.CONCATENATE,
                filename=f"to_processed_worker_a.success.{demonstration_code}.json",
                status=Status.SUCCESSFUL,
                source=getattr(self.settings, "url", self.pipeline),
                extra={
                    "demonstration_code": demonstration_code,
                    "years": list(range(2011, current_year + 1)),
                    "processed_file_path": str(parquet_file_path),
                    }
            )
            