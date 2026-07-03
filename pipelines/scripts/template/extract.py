
class ExtractTemplate:
    """Etapa de extração do pipeline template."""


    def __init__(self, pipeline: str):

        self.pipeline = pipeline
        self.process = "extract"
        self.logger = None


    def _extract(self, ctx) -> None:
        """Implementar aqui a lógica de extração."""

        self.logger.info("Etapa extract do pipeline template executada (placeholder).")


    def main(self, ctx) -> None:

        # Configura logger e ambiente.
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger

        if ctx.env == "dev":
            pass

        if ctx.env == "prod":
            pass

        self._extract(ctx=ctx)