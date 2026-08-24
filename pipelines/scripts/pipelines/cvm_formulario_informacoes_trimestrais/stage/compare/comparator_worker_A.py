
 
from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_worker_A import ComparatorWorkerInterfaceA

from pathlib import Path


class ComparatorWorkerA(ComparatorWorkerInterfaceA):


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )
        
        
    def _build_previous_data_path(self, ctx: PipelineContext) -> Path:
        
        return ctx.build_transformed_path(
            ctx.current_snapshot_path(self.pipeline, self.previous_snapshot),
            subdir_stage="to_processed",
            subdir_format="parquet"
        )
    
    
    def _build_current_data_path(self, ctx: PipelineContext) -> Path:
        
        return ctx.build_transformed_path(
            ctx.current_snapshot_path(self.pipeline, self.current_snapshot),
            subdir_stage="to_processed",
            subdir_format="parquet"
        )
        
    
    def _key_cols(self) -> list[str]:
        return ["CD_CVM", "DT_REFER", "VERSAO", "GRUPO_DFP", "ORDEM_EXERC", "DT_FIM_EXERC", "CD_CONTA"]
