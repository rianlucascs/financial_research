

from pipelines.shared.context import PipelineContext


class PipelineRepository:
    
    
    def __init__(
        self
    ) -> None:
        
        self.ctx = PipelineContext()


    def list_pipelines(self):
        return [
            path.name
            for path in (self.ctx.pipelines_dir / "scripts" / "pipelines").glob("*")
            if path.is_dir()
        ]
        