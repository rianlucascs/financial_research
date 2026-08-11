

from pipelines.shared.interfaces.pipelines.stage.pipeline import PipelineInterface

from pipelines.scripts.pipelines.template.stage.extract.extractor_orchestrator import ExtractorOrchestrator
from pipelines.scripts.pipelines.template.stage.transform.to_iterim.to_interim_orchestrator import ToInterimOrchestrator
from pipelines.scripts.pipelines.template.stage.transform.to_processed.to_processed_orchestrator import ToProcessedOrchestrator
from pipelines.scripts.pipelines.template.stage.load.loader_orchestrator import LoaderOrchestrator


class PipelineTemplate(PipelineInterface):
    
    
	pipeline = "template"


	def build_extractor_orchestrator(self) -> ExtractorOrchestrator:
		return ExtractorOrchestrator(pipeline=self.pipeline)


	def build_to_interim(self) -> ToInterimOrchestrator:
		return ToInterimOrchestrator(pipeline=self.pipeline)


	def build_to_processed(self) -> ToProcessedOrchestrator:
		return ToProcessedOrchestrator(pipeline=self.pipeline)


	def build_loader_orchestrator(self) -> LoaderOrchestrator:
		return LoaderOrchestrator(pipeline=self.pipeline)


def main(env: str = "dev", run_id: str | None = None) -> None:
    
	PipelineTemplate(env=env, run_id=run_id).run()


if __name__ == "__main__":
    
	main()



