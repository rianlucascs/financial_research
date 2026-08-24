"""
Worker:
    loader_worker_a

Responsabilidades:
    Carregar InterimData em banco de dados SQLite, criando um arquivo .db para cada tabela. 
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos InterimData foram gerados, o worker irá sobrescrever os arquivos .db existentes.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.load.loader_worker_A import LoaderWorkerInterfaceA

from pathlib import Path


class LoaderWorkerA(LoaderWorkerInterfaceA):
    
    
    process: str = "loader_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )


    def _build_data_path(self, ctx: PipelineContext) -> Path:
        
        return ctx.build_transformed_path(
            ctx.current_snapshot_path(self.pipeline),
            subdir_stage="to_processed", 
            subdir_format="parquet"
            )
