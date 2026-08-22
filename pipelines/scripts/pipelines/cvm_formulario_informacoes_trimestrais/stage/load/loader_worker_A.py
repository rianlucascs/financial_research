

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.load.loader_worker_A import LoaderWorkerInterfaceA

from pathlib import Path


class LoaderWorkerA(LoaderWorkerInterfaceA):


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)


    def _build_data_path(self, ctx: PipelineContext) -> Path:
        
        return ctx.build_transformed_path(
            ctx.current_snapshot_path(self.pipeline),
            subdir_stage="to_processed", 
            subdir_format="parquet"
            )