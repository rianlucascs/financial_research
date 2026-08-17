"""
Worker:
    comparator_workers_a
    
Responsabilidades:
    - Comparar os arquivos Parquet do snapshot atual com o snapshot anterior.
    - Verificar se houve adição, remoção ou alteração de linhas nos arquivos Parquet.
    
Notas:
    
"""



# Alto consumo de memória RAM, pois carrega os arquivos Parquet na memória para comparação.
# Descontinuar o uso deste worker, pois a comparação de arquivos Parquet será feita no worker `comparator_workers_b`.
# ------------------------------------------------------------------------------------------------------------------------------------------------


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_workers import ComparatorWorkersInterface
from pipelines.shared.utils.io_utils import clear_directory
from pipelines.shared.checkpoint_values import Stage, Step, Status

from pipelines.scripts.pipelines.cvm_formulario_informacoes_trimestrais.stage.pipeline_settings import current_snapshot_path

from datetime import date, timedelta
from pathlib import Path
from pandas import read_parquet, DataFrame
import pandas as pd
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
    
    
    def _find_added_rows(self, curr_hashes: pd.Series, prev_hashes_set: set, current_indexed: DataFrame) -> DataFrame:
        """Linhas que estão no DataFrame novo, mas não no antigo."""
        return current_indexed[~curr_hashes.isin(prev_hashes_set).values].reset_index()
    
    
    def _find_removed_rows(self, prev_hashes: pd.Series, curr_hashes_set: set, previous_indexed: DataFrame) -> DataFrame:
        """Linhas que estão no DataFrame antigo, mas não no novo."""
        return previous_indexed[~prev_hashes.isin(curr_hashes_set).values].reset_index()
    
    
    def _find_changed_rows(self, previous_indexed: DataFrame, current_indexed: DataFrame) -> DataFrame:
        """Linhas que estão em ambos os DataFrames, mas com valores diferentes."""
        _val_cols = list(current_indexed.columns)
        common_idx = current_indexed.index.intersection(previous_indexed.index)
        if common_idx.empty:
            return current_indexed.iloc[:0].reset_index()

        _new = current_indexed.loc[common_idx, _val_cols]
        _old = previous_indexed.loc[common_idx, _val_cols]
        _mask = ~(_new.eq(_old) | (_new.isna() & _old.isna())).all(axis=1)
        del _new, _old
        gc.collect()

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
            
            _filename = filename.removesuffix(".parquet")

            len_added_rows, len_removed_rows, len_changed_rows = None, None, None
            
            try:
                
                _key_cols = ["CD_CVM", "DT_REFER", "VERSAO", "GRUPO_DFP", "ORDEM_EXERC", "DT_FIM_EXERC", "CD_CONTA"]

                previous_df = self._read_snapshot_parquet(ctx, previous_snapshot, filename)
                prev_hashes = pd.util.hash_pandas_object(previous_df, index=False)
                previous_indexed = previous_df.set_index(_key_cols)
                del previous_df
                gc.collect()

                current_df = self._read_snapshot_parquet(ctx, current_snapshot, filename)
                curr_hashes = pd.util.hash_pandas_object(current_df, index=False)
                current_indexed = current_df.set_index(_key_cols)
                del current_df
                gc.collect()

                filename_folder_path = prepare_snapshot_drift_path / filename.removesuffix(".parquet")
                filename_folder_path.mkdir(parents=True, exist_ok=True)

                prev_hashes_set = set(prev_hashes)
                curr_hashes_set = set(curr_hashes)

                added = self._find_added_rows(curr_hashes, prev_hashes_set, current_indexed)
                del prev_hashes_set
                gc.collect()
                if not added.empty:
                    added.to_parquet(filename_folder_path / f"{_filename}_added.parquet", engine="pyarrow", index=False)
                    len_added_rows = len(added)
                del added
                gc.collect()

                removed = self._find_removed_rows(prev_hashes, curr_hashes_set, previous_indexed)
                del curr_hashes_set, prev_hashes, curr_hashes
                gc.collect()
                if not removed.empty:
                    removed.to_parquet(filename_folder_path / f"{_filename}_removed.parquet", engine="pyarrow", index=False)
                    len_removed_rows = len(removed)
                del removed
                gc.collect()

                changed = self._find_changed_rows(previous_indexed, current_indexed)
                del previous_indexed
                gc.collect()
                if not changed.empty:
                    changed.to_parquet(filename_folder_path / f"{_filename}_changed.parquet", engine="pyarrow", index=False)
                    len_changed_rows = len(changed)
                del changed
                del current_indexed
                gc.collect()
                    
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.COMPARE,
                    step=Step.TRANSFORM,
                    filename=f"comparator_workers_a.success.{_filename}.json",
                    status=Status.SUCCESSFUL,
                    source="cvm_formulario_informacoes_trimestrais",
                    extra={
                        "previous_snapshot": previous_snapshot,
                        "current_snapshot": current_snapshot,
                        "filename": filename,
                        "common_files": list(common_files),
                        "only_in_previous": list(only_in_previous),
                        "only_in_current": list(only_in_current),
                        "len_added_rows": len_added_rows,
                        "len_removed_rows": len_removed_rows,
                        "len_changed_rows": len_changed_rows,
                    }
                )
        
            except Exception as e:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.COMPARE,
                    step=Step.TRANSFORM,
                    filename=f"comparator_workers_a.failure.{_filename}.json",
                    status=Status.FAILED,
                    source="cvm_formulario_informacoes_trimestrais",
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
    worker = ComparatorWorkerA(pipeline="cvm_formulario_informacoes_trimestrais")
    worker.main(ctx=PipelineContext())