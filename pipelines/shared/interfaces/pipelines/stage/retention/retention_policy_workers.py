"""
Worker:
    ...
    
Responsabilidades:
    - Retenção de snapshots antigos, de acordo com a política definida na subclasse.
    - Retenção de logs de execução, de acordo com a política definida na subclasse.
    
Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.checkpoint_writer_mixin import CheckpointWriterMixin
from pipelines.shared.interfaces.pipelines.stage_interface import RawData, StageTypes

from abc import ABC, abstractmethod
from pathlib import Path


class RetentionPolicyWorkersInterface(CheckpointWriterMixin, ABC, StageTypes[RawData, None]):
    """
    Esta é a interface para as políticas de retenção de snapshots.
    
    > Retenção de snapshots é a política que define por quanto tempo e/ou quantos snapshots antigos serão mantidos.

    Herança de CheckpointWriterMixin para permitir gravação de checkpoints.
        ``_write_checkpoint``: método auxiliar para gravar checkpoints.
        
    Fluxo fixo (não sobrescrever):
        ``main``: ponto de entrada, sempre configura logging e chama o método ``_worker``.
        
    Métodos que a subclasse deve implementar:
        ``_worker``: define a lógica do worker de extração.
        
    Métodos auxiliares que a subclasse pode sobrescrever:
        ``_list_snapshots``: lista todos os snapshots disponíveis no caminho de origem.
        ``_select_snapshots_to_remove``: seleciona os snapshots que devem ser removidos com base na política de retenção.
    """
    
    
    process: str # subclasse deve declarar (ex: process = "retention_policy_workers_a")
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        self.pipeline = pipeline
        self.logger = None
    
    
    def _list_snapshots(self, source_path: Path) -> list[Path]:
        """
        Lista todos os snapshots disponíveis no caminho de origem.

        Args:
            source_path (Path): Caminho para o diretório que contém os snapshots.

        Returns:
            list[Path]: Lista de caminhos para os snapshots.
        """
        ...
        
        
    def _select_snapshots_to_remove(self, snapshots: list[Path]) -> list[Path]:
        """
        Seleciona os snapshots que devem ser removidos com base na política de retenção.

        Args:
            snapshots (list[Path]): Lista de snapshots disponíveis.

        Returns:
            list[Path]: Lista de snapshots que devem ser removidos.
        """
        
        # if len(snapshots) <= self.keep:
        #     return []
        
        # return snapshots[:-self.keep]
        
        ...
    
    
    @abstractmethod
    def _worker(self, ctx: PipelineContext) -> None:
        """
        Método que implementa a lógica do worker de retenção.
        """
        
        # snapshots = self._list_snapshots(ctx.source_path)
        # to_remove = self._select_snapshots_to_remove(snapshots)
        # for folder in to_remove:
        #     shutil.rmtree(folder)
        #     self.logger.info(f"Removido snapshot antigo: {folder}")
        
        ...


    def main(self, ctx: PipelineContext) -> None:
        """
        Método principal do worker de retenção, responsável por configurar logging e chamar o método ``_worker``.
        """
        
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        self._worker(ctx=ctx)
  
        