

from pipelines.shared.context import PipelineContext

from pathlib import Path
import json

class ReaderCheckpoints:
    
    
    def __init__(
        self,
        pipeline
    ) -> None:
        
        self.pipeline = pipeline
        self.ctx = PipelineContext()
    
    
    def _list_checkpoints(self, folder: str | None = None) -> list[list[Path, str]]:
        
        base_path = self.ctx.checkpoints_dir / self.pipeline
        
        return [
            [path, path.name]
            for path in (base_path if folder is None else (base_path / folder)).glob("*")
        ]
        
        
    def read(self, checkpoint_path: Path) -> str:
        return json.dumps(
            json.loads(checkpoint_path.read_text()),
            indent=4,
            ensure_ascii=False,
        )