

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
        file_identifiers: str | None = None,
    ) -> None:
        
        self.ctx = ctx or PipelineContext()
        self.pipeline = pipeline
        self.subdir_stage = subdir_stage
        self.subdir_format = subdir_format
        self.file_identifiers = file_identifiers if ".parquet" in file_identifiers else f"{file_identifiers}.parquet"


    def _build_parquet_path(self) -> str:
        
        return (
            self.ctx.build_transformed_path(
            self.ctx.current_snapshot_path(self.pipeline),
            subdir_stage=self.subdir_stage,
            subdir_format=self.subdir_format)
            / self.file_identifiers
            )


    def read(self) -> DataFrame:
        
        file_path = self._build_parquet_path()
        
        if not file_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {file_path}")
        
        return read_parquet(file_path, engine="pyarrow")