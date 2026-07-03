
from pipelines.shared.context import PipelineContext

from .extract import ExtractTemplate
from .transform import TransformTemplate
from .load import LoadTemplate


class PipelineTemplate:
    """Pipeline de referência para criação de novos pipelines do projeto."""


    def __init__(self, env: str = "dev", run_id: str | None = None):

        self.ctx = PipelineContext(env=env, run_id=run_id)
        
        self.pipeline = "PIPELINE_NAME"


    def run(self) -> None:

        # Responsável pela extração de dados.
        extract = ExtractTemplate(pipeline=self.pipeline)
        extract.main(ctx=self.ctx)

        # Responsável pela transformação dos dados.
        transform = TransformTemplate(pipeline=self.pipeline)
        transform.main(ctx=self.ctx)

        # Responsável pela carga dos dados processados.
        load = LoadTemplate(pipeline=self.pipeline)
        load.main(ctx=self.ctx)


def main(env: str = "dev", run_id: str | None = None):
    """Entrypoint padrão para execução (local e container)."""

    p = PipelineTemplate(env=env, run_id=run_id)
    p.run()


if __name__ == "__main__":

    main()
