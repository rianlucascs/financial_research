

from pipelines.shared.checkpoint_contract import build_checkpoint_payload
from pipelines.shared.checkpoint_values import Stage, Step, Status, FailurePoint, ReasonCode, Severity
from pipelines.shared.context import PipelineContext

from logging import Logger
from typing import Any


class CheckpointWriterMixin:
    
    
    pipeline: str 
    logger: Logger | None = None


    def _write_checkpoint(
        self,
        *,
        ctx: PipelineContext,
        stage: Stage,
        step: Step,
        filename: str, # f"{step}_{worker}.{status}.json",
        status: Status,
        failure_point: FailurePoint | None = None,
        reason: ReasonCode | None = None,
        severity: Severity | None = None,
        source: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:

        try:

            payload = build_checkpoint_payload(
                pipeline=self.pipeline,
                stage=stage,
                step=step,
                status=status,
                run_id=ctx.run_id,
                environment=ctx.env,
                failure_point=failure_point,
                reason=reason,
                severity=severity,
                source=source,
                extra=extra or {},
            )

            ctx.write_checkpoint(
                pipeline=self.pipeline or self.integration,
                stage=stage,
                step=step,
                filename=filename,
                data=payload,
            )

        except Exception:

            if self.logger:
                self.logger.exception(f"Falha ao gravar checkpoint para '{filename}'")

            raise