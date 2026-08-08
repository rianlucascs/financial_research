

from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface
from pipelines.shared.context import PipelineContext
from pipelines.shared.checkpoint_values import Stage, Step, Status, FailurePoint, Severity


class ExtractorWorkerA(ExtractorWorkersInterface):
    
    
    process = "extractor_worker_a"
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)


    def _worker(self, ctx: PipelineContext) -> None:
        """
        Método responsável por executar a lógica do worker de extração.
        """

        self._write_checkpoint(
            ctx=ctx,
            stage=Stage.EXTRACT,
            step=Step.DOWNLOAD,
            filename="extractor_worker_a.running.json",
            status=Status.RUNNING,
            source="template",
        )

        try:
            
            raw_dir = ctx.prepare_raw_path(pipeline=self.pipeline, subdir_format="zip")
            output_file = raw_dir / "source_a.txt"
            output_file.write_text("TODO: substituir por extração real da fonte A\n", encoding="utf-8")

            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.EXTRACT,
                step=Step.DOWNLOAD,
                filename="extractor_worker_a.success.json",
                status=Status.SUCCESSFUL,
                source="template",
                extra={"file": str(output_file)},
            )
            
        except Exception:
            
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.EXTRACT,
                step=Step.DOWNLOAD,
                filename="extractor_worker_a.failed.json",
                status=Status.FAILED,
                failure_point=FailurePoint.EXCEPTION,
                severity=Severity.ERROR,
                source="template",
            )
            
            raise