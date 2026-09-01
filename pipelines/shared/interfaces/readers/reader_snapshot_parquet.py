

from pipelines.shared.context import PipelineContext

from abc import ABC
from pandas import read_parquet, DataFrame
from typing import Literal
from pathlib import Path


class ReaderSnapshotParquetInterface(ABC):

    def __init__(
        self,
        pipeline: str,
        ctx: PipelineContext | None = None,
        subdir_stage: Literal["to_interim", "to_processed"] = "to_interim",
        subdir_format: str = "parquet",
        file_identifiers: str | None = None,
        use_latest_snapshot: bool | None = None,
    ) -> None:

        self.ctx = ctx or PipelineContext()
        self.pipeline = pipeline
        self.subdir_stage = subdir_stage
        self.subdir_format = subdir_format
        self.use_latest_snapshot = use_latest_snapshot

        if file_identifiers is not None and not file_identifiers.endswith(".parquet"):
            file_identifiers = f"{file_identifiers}.parquet"
        self.file_identifiers = file_identifiers


    def _find_latest_snapshot(self) -> Path | None:
        snapshots_dir = self.ctx.data_dir / self.pipeline
        snapshots = [p for p in snapshots_dir.iterdir() if p.is_dir()]

        if not snapshots:
            return None

        return max(snapshots, key=lambda p: p.name)


    def _resolve_snapshot_dir(self) -> Path | None:
        
        if self.use_latest_snapshot:
            
            return self._find_latest_snapshot()
        
        return self.ctx.current_snapshot_path(self.pipeline)


    def _build_parquet_path(self) -> Path:
        
        snapshot_dir = self._resolve_snapshot_dir()

        if snapshot_dir is None:
            raise FileNotFoundError(
                f"No snapshot found for pipeline: {self.pipeline}"
            )

        return (
            self.ctx.build_transformed_path(
                snapshot_dir,
                subdir_stage=self.subdir_stage,
                subdir_format=self.subdir_format,
            )
            / self.file_identifiers
        )


    def read(self) -> DataFrame:
        
        file_path = self._build_parquet_path()
        
        print(file_path)

        if not file_path.exists():
            
            raise FileNotFoundError(
                f"Parquet file not found: {file_path}"
                f"Snapshot directory: {self._find_latest_snapshot()}"
            )

        return read_parquet(file_path, engine="pyarrow")
