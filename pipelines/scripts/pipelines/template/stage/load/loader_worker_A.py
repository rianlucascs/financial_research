

from pipelines.shared.interfaces.pipelines.stage.load.loader_workers import LoaderWorkersInterface
from pipelines.shared.context import PipelineContext
from pipelines.shared.checkpoint_values import Stage, Step, Status, FailurePoint, Severity


class LoaderWorkerA(LoaderWorkersInterface):
    
    
    process = "loader_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)


    def _worker(self, ctx: PipelineContext) -> None:
        self._write_checkpoint(
            ctx=ctx,
            stage=Stage.LOAD,
            step=Step.UPLOAD,
            filename="loader_worker_a.running.json",
            status=Status.RUNNING,
            source="template",
        )

        try:
            
            processed_file = (
                ctx.build_transformed_path(
                    pipeline=self.pipeline,
                    subdir_stage="to_processed",
                    subdir_format="text",
                )
                / "processed.txt"
            )

            output_dir = ctx.prepare_load_path(pipeline=self.pipeline)
            output_file = output_dir / "load_manifest.txt"
            output_file.write_text(
                "TODO: substituir por carga real do destino\n"
                f"processed_exists={processed_file.exists()}\n",
                encoding="utf-8",
            )

            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.LOAD,
                step=Step.UPLOAD,
                filename="loader_worker_a.success.json",
                status=Status.SUCCESSFUL,
                source="template",
                extra={"file": str(output_file)},
            )
            
        except Exception:
            
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.LOAD,
                step=Step.UPLOAD,
                filename="loader_worker_a.failed.json",
                status=Status.FAILED,
                failure_point=FailurePoint.EXCEPTION,
                severity=Severity.ERROR,
                source="template",
            )
            
            raise
