

from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface
from pipelines.shared.context import PipelineContext
from pipelines.shared.checkpoint_values import Stage, Step, Status, FailurePoint, Severity


class ToInterimWorkerA(ToInterimWorkersInterface):
    
    
    process = "to_interim_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)

    def _worker(self, ctx: PipelineContext) -> None:
        
        self._write_checkpoint(
            ctx=ctx,
            stage=Stage.TO_INTERIM,
            step=Step.TRANSFORM,
            filename="to_interim_worker_a.running.json",
            status=Status.RUNNING,
            source="template",
        )

        try:
            
            source_a = ctx.build_raw_path(pipeline=self.pipeline, subdir_format="text") / "source_a.txt"
            source_b = ctx.build_raw_path(pipeline=self.pipeline, subdir_format="text") / "source_b.txt"

            output_dir = ctx.prepare_transformed_path(
                pipeline=self.pipeline,
                subdir_stage="to_interim",
                subdir_format="text",
            )
            output_file = output_dir / "interim.txt"

            lines = [
                "TODO: substituir por transformação real para interim",
                f"source_a_exists={source_a.exists()}",
                f"source_b_exists={source_b.exists()}",
            ]
            output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.TO_INTERIM,
                step=Step.TRANSFORM,
                filename="to_interim_worker_a.success.json",
                status=Status.SUCCESSFUL,
                source="template",
                extra={"file": str(output_file)},
            )
            
        except Exception:
            
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.TO_INTERIM,
                step=Step.TRANSFORM,
                filename="to_interim_worker_a.failed.json",
                status=Status.FAILED,
                failure_point=FailurePoint.TRANSFORM_EXCEPTION,
                severity=Severity.ERROR,
                source="template",
            )
            
            raise
