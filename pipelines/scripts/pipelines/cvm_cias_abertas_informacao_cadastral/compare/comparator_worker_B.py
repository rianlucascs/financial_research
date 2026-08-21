"""
Worker:
    comparator_workers_b
    
Responsabilidades:
    ...
    
Notas:
    
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_workers import ComparatorWorkersInterface
from pipelines.shared.utils.io_utils import clear_directory
from pipelines.shared.checkpoint_values import Stage, Step, Status

from pipelines.scripts.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.stage.pipeline_settings import current_snapshot_path

from datetime import date, timedelta
from pathlib import Path
import duckdb


class ComparatorWorkerB(ComparatorWorkersInterface):
    
    
    process: str = "comparator_workers_b"


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
    

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        escaped = identifier.replace('"', '""')
        return '"' + escaped + '"'


    @staticmethod
    def _quote_literal(value: Path) -> str:
        return str(value).replace("'", "''")


    def _copy_query_if_not_empty(
        self, con: duckdb.DuckDBPyConnection, query: str, output_path: Path
    ) -> int:
        output_literal = self._quote_literal(output_path)
        copy_sql = f"COPY ({query}) TO '{output_literal}' (FORMAT PARQUET)"
        try:
            con.execute(copy_sql)
        except Exception:
            if self.logger:
                self.logger.error(f"Falha ao executar query DuckDB:\n{copy_sql}")
            raise
        count = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{output_literal}')"
        ).fetchone()[0]
        if count == 0:
            output_path.unlink()
        return count


    def _find_snapshot_drift_duckdb(
        self,
        previous_path: Path,
        current_path: Path,
        output_dir: Path,
        output_stem: str,
        key_cols: list[str],
    ) -> tuple[int, int, int]:
        
        previous_file = self._quote_literal(previous_path)
        current_file = self._quote_literal(current_path)

        with duckdb.connect() as con:
            con.execute("SET memory_limit = '3GB'")

            current_relation = f"read_parquet('{current_file}')"
            previous_relation = f"read_parquet('{previous_file}')"

            columns = [row[0] for row in con.execute(f"DESCRIBE SELECT * FROM {current_relation}").fetchall()]

            missing_key_cols = [column for column in key_cols if column not in columns]
            if missing_key_cols:
                raise ValueError(
                    f"key_cols ausentes no parquet atual: {missing_key_cols}"
                )
            if not key_cols:
                raise ValueError("key_cols não pode ser vazio")

            key_join = " AND ".join(
                f"c.{self._quote_identifier(column)} IS NOT DISTINCT FROM p.{self._quote_identifier(column)}"
                for column in key_cols
            )

            added_query = (
                f"SELECT c.* FROM {current_relation} c "
                f"WHERE NOT EXISTS ("
                f"  SELECT 1 FROM {previous_relation} p WHERE {key_join}"
                f")"
            )
            removed_query = (
                f"SELECT p.* FROM {previous_relation} p "
                f"WHERE NOT EXISTS ("
                f"  SELECT 1 FROM {current_relation} c WHERE {key_join}"
                f")"
            )

            added_count = self._copy_query_if_not_empty(
                con, added_query, output_dir / f"{output_stem}_added.parquet"
            )
            removed_count = self._copy_query_if_not_empty(
                con, removed_query, output_dir / f"{output_stem}_removed.parquet"
            )

            value_cols = [column for column in columns if column not in key_cols]
            if not value_cols:
                # sem colunas de valor, não há como haver linhas "changed"
                changed_count = 0
            else:
                changed_condition = " OR ".join(
                    f"c.{self._quote_identifier(column)} IS DISTINCT FROM p.{self._quote_identifier(column)}"
                    for column in value_cols
                )
                changed_query = (
                    f"SELECT c.* FROM {current_relation} AS c "
                    f"JOIN {previous_relation} AS p ON {key_join} "
                    f"WHERE {changed_condition}"
                )
                changed_count = self._copy_query_if_not_empty(
                    con, changed_query, output_dir / f"{output_stem}_changed.parquet"
                )

        return added_count, removed_count, changed_count
        
        
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

                filename_folder_path = prepare_snapshot_drift_path / _filename
                filename_folder_path.mkdir(parents=True, exist_ok=True)
                key_cols = ["CD_CVM", "DT_REFER", "VERSAO", "GRUPO_DFP", "ORDEM_EXERC", "DT_FIM_EXERC", "CD_CONTA"]

                len_added_rows, len_removed_rows, len_changed_rows = self._find_snapshot_drift_duckdb(
                    previous_path=self._build_transform_path(ctx, previous_snapshot) / filename,
                    current_path=self._build_transform_path(ctx, current_snapshot) / filename,
                    output_dir=filename_folder_path,
                    output_stem=_filename,
                    key_cols=key_cols,
                )
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.COMPARE,
                    step=Step.TRANSFORM,
                    filename=f"comparator_workers_b.success.{_filename}.json",
                    status=Status.SUCCESSFUL,
                    source="cvm_formulario_demonstracoes_financeiras_padronizadas",
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
                    filename=f"comparator_workers_b.failure.{_filename}.json",
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
    worker = ComparatorWorkerB(pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas")
    worker.main(ctx=PipelineContext())