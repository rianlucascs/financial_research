"""
Worker:
    comparator_workers_a
    
Responsabilidades:
    ...
    
Notas:
    
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_workers import ComparatorWorkersInterface
from pipelines.scripts.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.pipeline_settings import current_snapshot_path
from pipelines.shared.utils.io_utils import clear_directory
from pipelines.shared.checkpoint_values import Stage, Step, Status

from datetime import date, timedelta
from pathlib import Path
from pandas import read_parquet
from pandas import DataFrame
import gc


class ComparatorWorkerA(ComparatorWorkersInterface):
    
    
    process: str = "comparator_workers_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
        
    
    def _compare_directory_files(self, ctx: PipelineContext, previous_snapshot: str, current_snapshot: str) -> tuple[set[str], set[str], set[str]]:
        
        previous_files = {
            path.name
            for path in self._build_transform_path(ctx, previous_snapshot).glob("*.parquet")
        }

        current_files = {
            path.name
            for path in self._build_transform_path(ctx, current_snapshot).glob("*.parquet")
        }

        common_files = previous_files & current_files
        only_in_previous = previous_files - current_files
        only_in_current = current_files - previous_files
        
        return common_files, only_in_previous, only_in_current
        
    
    def _build_transform_path(self, ctx: PipelineContext, date_snapshot) -> Path:
        
        to_processed_parquet_path = ctx.build_transformed_path(
            current_snapshot_path(self.pipeline, date_snapshot),
            subdir_stage="to_processed", 
            subdir_format="parquet"
            )
        
        return to_processed_parquet_path
    

    def _read_snapshot_parquet(self, ctx: PipelineContext, date_snapshot: str, file_name: str) -> DataFrame:
        
        return read_parquet(
            self._build_transform_path(ctx, date_snapshot) / file_name,
            engine="pyarrow"
            )
    
    
    def _find_added_rows(self, previous_df: DataFrame, current_df: DataFrame) -> DataFrame:
        """Linhas que estão no DataFrame novo, mas não no antigo."""
        
        return current_df[~current_df.apply(tuple, 1).isin(previous_df.apply(tuple, 1))]
    
    
    def _find_removed_rows(self, previous_df: DataFrame, current_df: DataFrame) -> DataFrame:
        """Linhas que estão no DataFrame antigo, mas não no novo."""
        
        return previous_df[~previous_df.apply(tuple, 1).isin(current_df.apply(tuple, 1))]
    
    
    def _find_changed_rows(self, previous_df: DataFrame, current_df: DataFrame) -> DataFrame:
        """Linhas que estão em ambos os DataFrames, mas com valores diferentes."""
        
        _key_cols: list[str] = ["CD_CVM", "DT_REFER", "VERSAO", "GRUPO_DFP", "ORDEM_EXERC", "DT_FIM_EXERC", "CD_CONTA"]
        _val_cols = [c for c in current_df.columns if c not in _key_cols]

        current_indexed = current_df.set_index(_key_cols)
        previous_indexed = previous_df.set_index(_key_cols)

        common_idx = current_indexed.index.intersection(previous_indexed.index)
        if common_idx.empty:
            return current_df.iloc[:0]

        _new = current_indexed.loc[common_idx, _val_cols]
        _old = previous_indexed.loc[common_idx, _val_cols]
        _mask = ~(_new.eq(_old) | (_new.isna() & _old.isna())).all(axis=1)

        return current_indexed.loc[_mask[_mask].index].reset_index()
        
        
    def _worker(self, ctx: PipelineContext) -> None:

        previous_snapshot = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        current_snapshot = date.today().strftime("%Y-%m-%d")
        
        prepare_snapshot_drift_path = ctx.prepare_snapshot_drift_path(self.pipeline, subdir=current_snapshot)
        
        clear_directory(prepare_snapshot_drift_path, logger=self.logger, remove_root=False)
        
        common_files, only_in_previous, only_in_current = self._compare_directory_files(ctx, previous_snapshot, current_snapshot)
        
        if only_in_previous:
            
            self.logger.warning(f"Arquivos presentes `apenas` no snapshot anterior ({previous_snapshot}): {only_in_previous}")
        
        if only_in_current:
            
            self.logger.warning(f"Arquivos presentes `apenas` no snapshot atual ({current_snapshot}): {only_in_current}")
            
        
        for filename in common_files:
            
            try:
                
                previous_df = self._read_snapshot_parquet(ctx, previous_snapshot, filename)
                current_df = self._read_snapshot_parquet(ctx, current_snapshot, filename)
                
                added = self._find_added_rows(previous_df, current_df)
                removed = self._find_removed_rows(previous_df, current_df)
                changed = self._find_changed_rows(previous_df, current_df)
                
                if not (added.empty and removed.empty and changed.empty):
                    
                    filename_folder_path = prepare_snapshot_drift_path / filename.removesuffix(".parquet")
                    filename_folder_path.mkdir(parents=True, exist_ok=True) 
                
                _filename = filename.removesuffix(".parquet")
                
                if not added.empty:
                    added.to_parquet(filename_folder_path / f"{_filename}_added.parquet", engine="pyarrow", index=False)
                
                if not removed.empty:
                    removed.to_parquet(filename_folder_path / f"{_filename}_removed.parquet", engine="pyarrow", index=False)
                
                if not changed.empty:
                    changed.to_parquet(filename_folder_path / f"{_filename}_changed.parquet", engine="pyarrow", index=False)
                    
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.COMPARE,
                    step=Step.TRANSFORM,
                    filename=f"comparator_workers_a.success.{_filename}.json",
                    status=Status.SUCCESSFUL,
                    source="cvm_formulario_demonstracoes_financeiras_padronizadas",
                    extra={
                        "previous_snapshot": previous_snapshot,
                        "current_snapshot": current_snapshot,
                        "filename": filename,
                        "common_files": list(common_files),
                        "only_in_previous": list(only_in_previous),
                        "only_in_current": list(only_in_current),
                        "len_added_rows": len(added),
                        "len_removed_rows": len(removed),
                        "len_changed_rows": len(changed),
                    }
                )
                
                del previous_df, current_df, added, removed, changed
                gc.collect()
        
            except Exception as e:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.COMPARE,
                    step=Step.TRANSFORM,
                    filename=f"comparator_workers_a.failure.{_filename}.json",
                    status=Status.FAILED,
                    source="cvm_formulario_demonstracoes_financeiras_padronizadas",
                    extra={
                        "previous_snapshot": previous_snapshot,
                        "current_snapshot": current_snapshot,
                        "common_files": list(common_files),
                        "only_in_previous": list(only_in_previous),
                        "only_in_current": list(only_in_current),
                        "error_message": str(e),
                    }
                )
                
                self.logger.error(f"Erro ao comparar arquivos do snapshot: {e}")
                
        
if __name__ == "__main__":
    worker = ComparatorWorkerA(pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas")
    worker.main(ctx=PipelineContext())