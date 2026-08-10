

from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_workers import ToProcessedWorkersInterface
from pipelines.shared.context import PipelineContext
from pipelines.shared.checkpoint_values import Stage, Step, Status, FailurePoint, Severity


class ToProcessedWorkerA(ToProcessedWorkersInterface):
    
    
    process = "to_processed_worker_a"
    

    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        super().__init__(pipeline=pipeline)


    def _worker(self, ctx: PipelineContext) -> None:
        
        self._write_checkpoint(
            ctx=ctx,
            stage=Stage.TO_PROCESSED,
            step=Step.TRANSFORM,
            filename="to_processed_worker_a.running.json",
            status=Status.RUNNING,
            source="template",
        )

        try:
            interim_file = (
                ctx.build_transformed_path(
                    pipeline=self.pipeline,
                    subdir_stage="to_interim",
                    subdir_format="text",
                )
                / "interim.txt"
            )

            output_dir = ctx.prepare_transformed_path(
                pipeline=self.pipeline,
                subdir_stage="to_processed",
                subdir_format="text",
            )
            output_file = output_dir / "processed.txt"

            content = [
                "TODO: substituir por transformação de negócio para processed",
                f"interim_exists={interim_file.exists()}",
            ]
            output_file.write_text("\n".join(content) + "\n", encoding="utf-8")

            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.TO_PROCESSED,
                step=Step.TRANSFORM,
                filename="to_processed_worker_a.success.json",
                status=Status.SUCCESSFUL,
                source="template",
                extra={"file": str(output_file)},
            )
            
        except Exception:
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.TO_PROCESSED,
                step=Step.TRANSFORM,
                filename="to_processed_worker_a.failed.json",
                status=Status.FAILED,
                failure_point=FailurePoint.TRANSFORM_EXCEPTION,
                severity=Severity.ERROR,
                source="template",
            )
            raise
