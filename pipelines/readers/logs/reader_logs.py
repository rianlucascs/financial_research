

from typing import Literal

from pipelines.shared.context import PipelineContext
from pathlib import Path
from dataclasses import dataclass


@dataclass
class LogIdentifier:
    
    log_id: str | None = None
    stage: str | None = None
    

class ReaderLogs:
    
    
    def __init__(
        self,
        *,
        pipeline: str
    ) -> None:
        
        self.pipeline = pipeline
        self.ctx = PipelineContext()
       
       
    def _list_log_folders(self, log_path: Path | None = None) -> list[Path]:
        """Lista os diretórios de log para o pipeline especificado.
        
        Args:
            log_path (Path | None): Caminho para o diretório de logs. Se None, será usado o diretório padrão de logs do pipeline."""
        
        if log_path is None:
            return list((self.ctx.logs_dir / self.pipeline).glob("*"))
        
        return list(log_path.glob("*"))


    def _get_latest_log_folder(self) -> Path:
        """Obtém o diretório de log mais recente para o pipeline especificado."""
        
        folders = self._list_log_folders()

        if not folders:
            
            raise FileNotFoundError(
                f"Nenhuma pasta de log encontrada em "
                f"{self.ctx.logs_dir / self.pipeline}"
            )

        return max(
            folders,
            key=lambda path: path.stat().st_ctime,
        )
        
        
    def _list_latest_log_files(self, log_path: Path | None = None) -> list[Path]:
        """Lista os arquivos de log no diretório de log mais recente para o pipeline especificado.
        
        Args:
            log_path (Path | None): Caminho para o diretório de logs. Se None, será usado o diretório padrão de logs do pipeline."""
        
        if log_path is None:
            log_path = self._get_latest_log_folder()
        
        return self._list_log_folders(log_path=log_path)
    
    
    def _read_log_file(self, 
                       log_file_name: Literal[
                           "extractor_orchestrator", "extractor_worker_a", "extractor_worker_b",
                           "to_interim_orchestrator", "to_interim_worker_a", "to_interim_worker_b",
                           "to_processed_orchestrator", "to_processed_worker_a", "to_processed_worker_b", 
                           "comparator_orchestrator", "comparator_worker_a", "comparator_worker_b",
                           "retention_policy_orchestrator", "retention_policy_worker_a", "retention_policy_worker_b"
                        ] | None = None
        ) -> str:
        
        
        for log_file in self._list_latest_log_files():
            
            if log_file_name in log_file.name:
                
                with open(log_file, "r") as f:
                    print(log_file)
                    return f.read()
        
        raise FileNotFoundError(f"Nenhum arquivo de log encontrado com o nome '{log_file_name}' no diretório de logs mais recente.")
        
    


if __name__ == "__main__":
    
    reader = ReaderLogs(pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas")
    last = reader._read_log_file(log_file_name="comparator_workers_a")
    print(last)