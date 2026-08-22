

from pipelines.shared.context import PipelineContext

from abc import ABC
from pandas import read_parquet, DataFrame
from typing import Literal


class ReaderSnapshotParquetInterface(ABC):
    
    
    def __init__(
        self,
        pipeline: str,
        ctx: PipelineContext | None = None,
        subdir_stage: Literal["to_interim", "to_processed"] = "to_interim",
        subdir_format: str = "parquet",
    ) -> None:
        
        self.ctx = ctx or PipelineContext()
        self.pipeline = pipeline
        self.subdir_stage = subdir_stage
        self.subdir_format = subdir_format


    def _build_parquet_path(self) -> str:
        
        return self.ctx.build_transformed_path(
            self.ctx.current_snapshot_path(self.pipeline),
            subdir_stage=self.subdir_stage,
            subdir_format=self.subdir_format,
        )

    def read(self) -> DataFrame:
        return read_parquet(self._build_parquet_path(), engine="pyarrow")