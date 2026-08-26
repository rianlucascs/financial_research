

from pipelines.shared.interfaces.pipelines.stage.pipeline import PipelineInterface

from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.extract.extractor_orchestrator import ExtractorOrchestrator
from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.transform.to_interim.to_interim_orchestrator import ToInterimOrchestrator
# from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.transform.to_processed.to_processed_orchestrator import ToProcessedOrchestrator
# from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.load.loader_orchestrator import LoaderOrchestrator
from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.compare.comparator_orchestrator import ComparatorOrchestrator
from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.retention.retention_policy_orchestrator import RetentionPolicyOrchestrator


class PipelineTemplate(PipelineInterface):
    
    
	pipeline: str = "cvm_cias_abertas_informacao_cadastral"


	def build_extractor_orchestrator(self) -> ExtractorOrchestrator:
		return ExtractorOrchestrator(pipeline=self.pipeline)


	def build_to_interim_orchestrator(self) -> ToInterimOrchestrator:
		return ToInterimOrchestrator(pipeline=self.pipeline)


	def build_to_processed_orchestrator(self) -> None:
		return None


	def build_loader_orchestrator(self) -> None:
		return None


	def build_comparator_orchestrator(self) -> ComparatorOrchestrator:
		return ComparatorOrchestrator(pipeline=self.pipeline)

 
	def build_retention_policy_orchestrator(self) -> RetentionPolicyOrchestrator:
		return RetentionPolicyOrchestrator(pipeline=self.pipeline)


def main(env: str = "dev", run_id: str | None = None) -> None:
    
	PipelineTemplate(env=env, run_id=run_id).run()


if __name__ == "__main__":
    
	main()



