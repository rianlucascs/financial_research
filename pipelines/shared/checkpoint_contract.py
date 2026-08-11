

from pipelines.shared.checkpoint_values import (
    Stage,
    Step,
    Status,
    FailurePoint,
    ReasonCode,
    Severity,
)


from datetime import datetime, timezone
import socket


def build_checkpoint_payload(
    *,
    pipeline: str,
    stage: Stage | str,
    step: Step | str,
    status: Status | str,
    run_id: str | None,
    environment: str | None,
    failure_point: FailurePoint | str | None = None,
    reason: ReasonCode | str | None = None,
    severity: Severity | str | None = None,
    source: str | None = None,
    extra: dict | None = None,
) -> dict:
    """
    Monta payload base padronizado para checkpoints.

    Args:
        ``pipeline``: Nome do pipeline que está gerando o checkpoint (ex: 'cvm_dfp').
        ``stage``: Etapa macro do processamento (ex: 'extract', 'transform', 'load').
        ``step``: Sub-etapa específica dentro do stage (ex: 'download_zip', 'extract_zip').
        ``status``: Situação final da execução (ex: 'successful', 'failed', 'no_file_detected').
        ``run_id``: Identificador único da execução atual, usado para rastrear o run no log/checkpoint. Pode ser None se não houver um run_id disponível no contexto.
        ``environment``: Ambiente em que o pipeline está rodando (ex: 'dev', 'prod'). Pode ser None se não fornecido.
        ``failure_point``: Ponto específico de falha, quando status indica erro (ex: 'exception', 'file_detection'). None quando não houve falha.
        ``source``: Origem dos dados processados (ex: 'B3', 'CVM').
        ``extra``: Dados adicionais específicos do checkpoint (ex: nome de arquivo, tentativas, arquivos extraídos). Mesclado ao payload final via update().

    Returns:
        dict: Payload padronizado pronto para ser persistido pelo checkpoint,
        contendo os campos acima mais 'timestamp' (UTC, gerado automaticamente)
        e 'host' (nome da máquina, via socket.gethostname()).

    """
    
    payload = {
        "pipeline": pipeline,
        "stage": stage,
        "step": step,
        "status": status,
        "failure_point": failure_point,
        "reason": reason,
        "severity": severity,
        "run_id": run_id, 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "host": socket.gethostname(),
        "environment": environment,
    }
    
    if extra:
        
        payload.update(extra)
        
    return payload
