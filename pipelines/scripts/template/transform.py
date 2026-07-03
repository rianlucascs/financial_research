
class TransformTemplate:
	"""Etapa de transformação do pipeline template."""


	def __init__(self, pipeline: str):

		self.pipeline = pipeline
		self.process = "transform"
		self.logger = None


	def _transform(self, ctx) -> None:
		"""Implementar aqui a lógica de transformação."""

		self.logger.info("Etapa transform do pipeline template executada (placeholder).")


	def main(self, ctx) -> None:

		ctx.configure_logging(pipeline=self.pipeline, process=self.process)
		self.logger = ctx.logger

		if ctx.env == "dev":
			pass

		if ctx.env == "prod":
			pass

		self._transform(ctx=ctx)
    
