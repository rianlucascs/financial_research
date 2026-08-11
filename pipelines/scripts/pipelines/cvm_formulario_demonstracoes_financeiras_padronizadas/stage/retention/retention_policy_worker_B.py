"""
Worker:
    retention_policy_workers_b.

Responsabilidades:
    - Identificar logs expirados.
    - Remover logs fora da política de retenção.

Regra de exclusão:
    - Mantém os logs dos últimos 3 dias (hoje, ontem e anteontem).
    - Remove todos os logs mais antigos.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_workers import RetentionPolicyWorkersInterface
from pipelines.shared.utils.io_utils import clear_directory
from pipelines.shared.checkpoint_values import Stage, Step, Status

from datetime import date, timedelta
from pathlib import Path


class RetentionPolicyWorkerB(RetentionPolicyWorkersInterface):
    
    
    process: str = "retention_policy_workers_b"
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
    
    
    def _get_creation_time(self, path: Path) -> date:
        """Obtém a data de criação do diretório."""
        
        creation_time = path.stat().st_ctime
        return date.fromtimestamp(creation_time)
    
    
    def _list_logs(self, ctx: PipelineContext) -> list[tuple[Path, str, date]]:
        """Lista todos os logs disponíveis no caminho de origem."""

        logs_root = ctx.logs_dir / self.pipeline
        if not logs_root.exists():
            return []

        return [
            (path, path.name, self._get_creation_time(path))
            for path in logs_root.iterdir()
            if path.is_dir()
        ]


    def _select_logs_to_remove(self, logs: list[tuple[Path, str, date]]) -> list[Path]:
        """Seleciona os logs que devem ser removidos com base na política de retenção."""
        
        # Define a política de retenção: manter os últimos 3 dias de logs
        manter = {
            date.today() - timedelta(days=i)
            for i in range(3)
        }
        
        # Datas que podem ser apagadas
        return [
            log
            for log in logs
            if log[2] not in manter
        ]

    
    def  _remove_logs(self, logs_to_remove: list[tuple[Path, str, date]]) -> list[Path]:
        
        removed_logs = []
        
        for log_path, _, _ in logs_to_remove:

            if log_path.exists():
                
                clear_directory(log_path, logger=self.logger, remove_root=True)
                
                removed_logs.append(log_path)
                
            else:
                
                self.logger.warning(f"Log não encontrado: {log_path}")

        return removed_logs
    
    
    def _worker(self, ctx: PipelineContext) -> None:
        """
        Método que implementa a lógica do worker de retenção.
        """
        
        logs = self._list_logs(ctx)   
        logs_to_remove = self._select_logs_to_remove(logs)
        removed_logs = self._remove_logs(logs_to_remove)
        
        self._write_checkpoint(
            ctx=ctx,
            stage=Stage.RETENTION,
            step=Step.CLEANUP,
            filename="retention_policy_workers_b.success.json",
            status=Status.SUCCESSFUL,
            source="cvm_formulario_demonstracoes_financeiras_padronizadas",
            extra={
                "removed_logs": [str(log_path) for log_path in removed_logs],
                "remaining_logs": [str(log[0]) for log in logs if log not in logs_to_remove],
            }
        )
        

if __name__ == "__main__":
    worker = RetentionPolicyWorkerB(pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas")
    worker.main(ctx=PipelineContext())
  
        