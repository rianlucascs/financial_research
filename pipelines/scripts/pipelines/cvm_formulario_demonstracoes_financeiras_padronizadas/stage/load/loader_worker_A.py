"""
Worker:
    loader_worker_a

Responsabilidades:
    Carregar InterimData em banco de dados SQLite, criando um arquivo .db para cada tabela. 
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos InterimData foram gerados, o worker irá sobrescrever os arquivos .db existentes.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.load.loader_workers import LoaderWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Step, Status

from pipelines.scripts.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.pipeline_settings import current_snapshot_path

import sqlite3
import pyarrow.parquet as pq
import gc


class LoaderWorkerA(LoaderWorkersInterface):
    
    
    process: str = "loader_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)


    def _worker(self, ctx: PipelineContext) -> None:
        
        processed_parquet_path = ctx.build_transformed_path(current_snapshot_path(self.pipeline), subdir_stage="to_processed", subdir_format="parquet")
        load_path = ctx.prepare_load_path(current_snapshot_path(self.pipeline))
        
        for parquet_path in processed_parquet_path.glob("*.parquet"):
            
            table_name = parquet_path.stem
            db_path = load_path / f"{table_name}.db"
            
            conn = sqlite3.connect(db_path)
            
            try:
                
                first_batch = True

                for batch in pq.ParquetFile(parquet_path).iter_batches(batch_size=50_000):
                    df_batch = batch.to_pandas()
                    df_batch.to_sql(
                        name=table_name,
                        con=conn,
                        if_exists="replace" if first_batch else "append",
                        index=False,
                    )
                    first_batch = False
                    del df_batch
                    gc.collect()
                
                conn.commit()
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.LOAD,
                    step=Step.DB_CREATE,
                    status=Status.SUCCESSFUL,
                    filename=f"loader_worker_a.success.{table_name}.json",
                    source="cvm_formulario_demonstracoes_financeiras_padronizadas",
                    extra={
                        "table_name": table_name,
                        "db_path": str(db_path),
                    },
                )
                
            finally:
            
                conn.close()

            
if __name__ == "__main__":        
    worker = LoaderWorkerA(pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas")
    worker.main(ctx=PipelineContext())
