"""
Worker:
    to_processed_worker_a

Responsabilidades:
    Concatena os CSVs brutos anuais (2011 até o ano corrente) de cada tipo de demonstração DFP (CVM).
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos InterimData foram gerados, o worker irá sobrescrever os arquivos Parquet processados existentes.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_workers import ToProcessedWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Step, Status
from pipelines.shared.utils.io_utils import remove_file

from pipelines.scripts.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.pipeline_settings import current_snapshot_path, demonstration_codes

from datetime import date
from pandas import DataFrame, read_parquet, concat
import gc


class ToProcessedWorkerA(ToProcessedWorkersInterface):
    
    
    process: str = "to_processed_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)


    def _worker(self, ctx: PipelineContext) -> None:
        
        current_year = date.today().year
        
        for demonstration_code in demonstration_codes:
            
            # Monta o caminho do arquivo Parquet processado final
            filename = f"dfp_cia_aberta_{demonstration_code}_2011-{current_year}.parquet"
            processed_parquet_path = ctx.prepare_transformed_path(current_snapshot_path(self.pipeline), subdir_stage="to_processed", subdir_format="parquet")
            parquet_file_path = processed_parquet_path / filename
            
            remove_file(parquet_file_path, logger=self.logger)
            
            df = DataFrame()
            
            for year in range(2011, current_year + 1):
                
                # Monta o caminho do arquivo Parquet intermediário
                interim_parquet_path = ctx.build_transformed_path(current_snapshot_path(self.pipeline), subdir_stage="to_interim", subdir_format="parquet")
                interim_file_path = interim_parquet_path / f"dfp_cia_aberta_{demonstration_code}_{year}.parquet"
                
                df_interim = read_parquet(interim_file_path, engine="pyarrow")
                
                df = concat([df, df_interim])

            df.to_parquet(parquet_file_path, index=False, engine="pyarrow")
            
            del df
            del df_interim
            gc.collect()
            
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.TO_PROCESSED,
                step=Step.CONCATENATE,
                filename=f"to_processed_worker_a.success.{demonstration_code}.json",
                status=Status.SUCCESSFUL,
                source="cvm_formulario_demonstracoes_financeiras_padronizadas",
                extra={
                    "demonstration_code": demonstration_code,
                    "years": list(range(2011, current_year + 1)),
                    "processed_file_path": str(parquet_file_path),
                    }
            )
            

if __name__ == "__main__":
    worker = ToProcessedWorkerA(pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas")
    worker.main(ctx=PipelineContext())