"""
Worker:
    retention_policy_workers_a.

Responsabilidades:
    - Identificar snapshots expirados.
    - Remover snapshots fora da política de retenção.

Regra de exclusão:
    - Mantém os snapshots dos últimos 3 dias (hoje, ontem e anteontem).
    - Remove todos os snapshots mais antigos.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_workers import RetentionPolicyWorkersInterface
from pipelines.shared.utils.io_utils import clear_directory
from pipelines.shared.checkpoint_values import Stage, Step, Status

from datetime import date, timedelta
from pathlib import Path


class RetentionPolicyWorkerA(RetentionPolicyWorkersInterface):
    
    
    process: str = "retention_policy_workers_a"
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
    
    
    def _list_snapshots(self, ctx: PipelineContext) -> list[tuple[Path, str]]:
        """Lista todos os snapshots disponíveis no caminho de origem."""

        snapshots_root = ctx.data_dir / self.pipeline
        if not snapshots_root.exists():
            return []

        return [
            (path, path.name)
            for path in snapshots_root.iterdir()
            if path.is_dir()
        ]
        
        
    def _select_snapshots_to_remove(self, snapshots: list[tuple[Path, str]]) -> list[Path]:
        """Seleciona os snapshots que devem ser removidos com base na política de retenção."""
        
        # Define a política de retenção: manter os últimos 3 dias de snapshots
        manter = {
            date.today() - timedelta(days=i)
            for i in range(3)
        }
        
        # Datas que podem ser apagadas
        return [
            snapshot
            for snapshot in snapshots
            if date.fromisoformat(snapshot[1]) not in manter
        ]

    
    def  _remove_snapshots(self, snapshots_to_remove: list[tuple[Path, str]]) -> list[Path]:
        
        removed_snapshots = []
        
        for snapshot, _ in snapshots_to_remove:

            if snapshot.exists():
                
                clear_directory(snapshot, logger=self.logger, remove_root=True)
                removed_snapshots.append(snapshot)
                
            else:
                
                self.logger.warning(f"Snapshot não encontrado: {snapshot}")

        return removed_snapshots
    
    def _worker(self, ctx: PipelineContext) -> None:
        """
        Método que implementa a lógica do worker de retenção.
        """
        
        snapshots = self._list_snapshots(ctx)
        snapshots_to_remove = self._select_snapshots_to_remove(snapshots)
        removed_snapshots = self._remove_snapshots(snapshots_to_remove)
        
        self._write_checkpoint(
            ctx=ctx,
            stage=Stage.RETENTION,
            step=Step.CLEANUP,
            filename="retention_policy_workers_a.success.json",
            status=Status.SUCCESSFUL,
            source="cvm_formulario_demonstracoes_financeiras_padronizadas",
            extra={
                "removed_snapshots": [str(snapshot) for snapshot in removed_snapshots],
                "remaining_snapshots": [str(snapshot[0]) for snapshot in snapshots if snapshot not in snapshots_to_remove],
            }
        )
        


if __name__ == "__main__":
    
    worker = RetentionPolicyWorkerA(pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas")
    worker.main(ctx=PipelineContext())
  
        