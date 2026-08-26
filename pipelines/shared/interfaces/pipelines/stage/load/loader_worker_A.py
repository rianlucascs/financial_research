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

from abc import abstractmethod
import sqlite3
import pyarrow.parquet as pq
import gc
from pathlib import Path


class LoaderWorkerInterfaceA(LoaderWorkersInterface):
    """
    Classe responsável por implementar a lógica de carregamento de dados do worker 'loader_worker_a'.
    
    Está classe carrega os dados dos arquivos InterimData para bancos de dados SQLite, criando um arquivo .db para cada tabela.
    """
    
    
    process: str = "loader_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )


    @abstractmethod
    def _build_data_path(self, ctx: PipelineContext) -> Path:
        """
        Constrói o caminho para os arquivos Interim ou Processed.
        """
        
        ...
    
    
    def _worker(self, ctx: PipelineContext) -> None:
        
        data_path = self._build_data_path(ctx=ctx)
        load_path = ctx.prepare_load_path(ctx.current_snapshot_path(self.pipeline)) 
        
        for parquet_path in data_path.glob("*.parquet"):
            
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
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={
                        "table_name": table_name,
                        "db_path": str(db_path),
                    },
                )
            
            except Exception as exc:
                
                self.logger.error(f"Falha ao carregar '{parquet_path}' no banco de dados: {exc}")
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.LOAD,
                    step=Step.DB_CREATE,
                    status=Status.FAILED,
                    filename=f"loader_worker_a.failed.{table_name}.json",
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={
                        "table_name": table_name,
                        "db_path": str(db_path),
                        "error": str(exc),
                    },
                )
                
                raise
            
            finally:
            
                conn.close()
                