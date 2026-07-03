class LoadTemplate:
	"""Etapa de carga do pipeline template."""


	def __init__(self, pipeline: str):

		self.pipeline = pipeline
		self.process = "load"
		self.logger = None


	def _load(self, ctx) -> None:
		"""Implementar aqui a lógica de carga."""

		self.logger.info("Etapa load do pipeline template executada (placeholder).")


	def main(self, ctx) -> None:

		ctx.configure_logging(pipeline=self.pipeline, process=self.process)
		self.logger = ctx.logger

		if ctx.env == "dev":
			pass

		if ctx.env == "prod":
			pass

		self._load(ctx=ctx)
