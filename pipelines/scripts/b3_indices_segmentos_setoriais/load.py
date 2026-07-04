

from pipelines.shared.checkpoint_contract import build_checkpoint_payload
from pipelines.shared.checkpoint_values import (
	FAILURE_FILE_DETECTION,
	FAILURE_IO_ERROR,
	STATUS_FAILED,
	STATUS_NO_FILE_DETECTED,
	STATUS_SUCCESSFUL,
)

from .settings import (
	B3_INDICES,
	CHECKPOINT_STAGE_LOAD,
	CHECKPOINT_STEP_LOAD,
)

from datetime import datetime
from pandas import concat, read_csv, to_datetime
import gc
import sqlite3


class LoadB3IndicesSegmentosSetoriais:
	"""Carrega os CSVs brutos dos índices da B3 em um banco SQLite."""


	def __init__(self, pipeline: str):

		self.pipeline = pipeline
		self.process = "load"
		self.logger = None


	def _raw_base_path(self, ctx):

		repo_root = ctx.repo_root / "financial_research"
		if not repo_root.exists():
			repo_root = ctx.repo_root

		return repo_root / "data" / "pipelines" / self.pipeline / "raw"


	def _raw_path(self, ctx, indice: str):

		return self._raw_base_path(ctx) / indice.upper()


	def _latest_file(self, ctx, indice: str):

		path = self._raw_path(ctx, indice)
		if not path.exists():
			raise FileNotFoundError(f"Diretório raw não encontrado para o índice {indice}: {path}")

		files = sorted(
			[file for file in path.iterdir() if file.is_file() and file.suffix.lower() == ".csv"],
			key=lambda file: file.stat().st_mtime,
			reverse=True,
		)
		if not files:
			raise FileNotFoundError(f"Nenhum arquivo CSV encontrado para o índice {indice} em {path}")

		return files[0]


	def _to_float(self, series):

		return (
			series.astype(str)
			.str.strip()
			.str.rstrip(";")
			.replace({"": None, "nan": None, "None": None})
			.str.replace(".", "", regex=False)
			.str.replace(",", ".", regex=False)
			.astype(float)
		)


	def _to_int(self, series):

		return (
			series.astype(str)
			.str.strip()
			.str.rstrip(";")
			.str.replace(".", "", regex=False)
			.astype(int)
		)


	def _read_indice_csv(self, ctx, indice: str, file_name: str | None = None):
		"""Lê e normaliza o CSV bruto mais recente de um índice da B3."""

		indice = indice.upper()
		path_file = self._raw_path(ctx, indice) / file_name if file_name else self._latest_file(ctx, indice)

		if not path_file.exists():
			raise FileNotFoundError(f"O arquivo {path_file.name} não foi encontrado no caminho {path_file}.")

		header = read_csv(path_file, sep=";", encoding="latin-1", header=None, nrows=1).iloc[0, 0]
		data_referencia = None
		if isinstance(header, str):
			marker = "Carteira do Dia "
			if marker in header:
				data_str = header.split(marker, 1)[1].strip()
				data_referencia = datetime.strptime(data_str, "%d/%m/%y")

		df = read_csv(
			path_file,
			sep=";",
			encoding="latin-1",
			skiprows=1,
			dtype=str,
			usecols=range(5),
			index_col=False,
		)

		if "Código" not in df.columns:
			raise ValueError(f"Arquivo fora do formato esperado: {path_file}")

		df = df[df["Código"].notna()].copy()
		df["Código"] = df["Código"].astype(str).str.strip()
		df = df[df["Ação"].notna()].copy()
		df = df[df["Código"] != "Quantidade Teórica Total"].reset_index(drop=True)

		if "Qtde. Teórica" in df.columns:
			df["Qtde. Teórica"] = self._to_int(df["Qtde. Teórica"])

		if "Part. (%)" in df.columns:
			df["Part. (%)"] = self._to_float(df["Part. (%)"])

		df.insert(0, "Indice", indice)
		if data_referencia is not None:
			df.insert(1, "Data Referencia", to_datetime(data_referencia))

		return df


	def _gravar_checkpoint_load(self, item_name, status, failure_point, ctx, extra=None):

		extra_payload = {"item_name": item_name}
		if extra:
			extra_payload.update(extra)

		try:
			payload = build_checkpoint_payload(
				pipeline=self.pipeline,
				stage=CHECKPOINT_STAGE_LOAD,
				step=CHECKPOINT_STEP_LOAD,
				status=status,
				run_id=ctx.run_id,
				environment=ctx.env,
				failure_point=failure_point,
				source="B3",
				extra=extra_payload,
			)
			ctx.write_checkpoint(
				self.pipeline,
				CHECKPOINT_STAGE_LOAD,
				CHECKPOINT_STEP_LOAD,
				item_name,
				payload,
			)

		except Exception:
			self.logger.exception(f"Falha ao gravar checkpoint de load para '{item_name}'")


	def load(self, ctx):
		"""Lê os CSVs brutos dos índices e os carrega em uma tabela SQLite única."""

		path_load = ctx.path_load(self.pipeline)
		path_load.mkdir(parents=True, exist_ok=True)

		db_path = path_load / "b3_indices_segmentos_setoriais.db"
		table_name = "b3_indices_segmentos_setoriais"

		self.logger.info(f"Iniciando load do pipeline '{self.pipeline}' para o banco '{db_path}'.")

		frames = []

		for indice in B3_INDICES:
			try:
				csv_path = self._latest_file(ctx, indice)
				df = self._read_indice_csv(ctx, indice=indice, file_name=csv_path.name)
				frames.append(df)

				self.logger.info(f"Índice '{indice}' carregado em memória ({len(df)} linhas).")

				self._gravar_checkpoint_load(
					item_name=indice,
					status=STATUS_SUCCESSFUL,
					failure_point=None,
					ctx=ctx,
					extra={"csv_path": str(csv_path), "rows": len(df), "db_path": str(db_path)},
				)

			except FileNotFoundError:
				csv_path = self._raw_path(ctx, indice)

				self.logger.warning(f"Nenhum CSV encontrado para o índice '{indice}' em '{csv_path}'.")

				self._gravar_checkpoint_load(
					item_name=indice,
					status=STATUS_NO_FILE_DETECTED,
					failure_point=FAILURE_FILE_DETECTION,
					ctx=ctx,
					extra={"csv_path": str(csv_path), "db_path": str(db_path)},
				)

			except Exception:
				self.logger.exception(f"Erro ao carregar o índice '{indice}'.")

				self._gravar_checkpoint_load(
					item_name=indice,
					status=STATUS_FAILED,
					failure_point=FAILURE_IO_ERROR,
					ctx=ctx,
					extra={"db_path": str(db_path)},
				)

		if not frames:
			self.logger.error("Nenhum índice disponível para carga no SQLite.")

			self._gravar_checkpoint_load(
				item_name=table_name,
				status=STATUS_NO_FILE_DETECTED,
				failure_point=FAILURE_FILE_DETECTION,
				ctx=ctx,
				extra={"db_path": str(db_path)},
			)

			raise FileNotFoundError("Nenhum arquivo CSV disponível para carga do pipeline b3_indices_segmentos_setoriais.")

		df_all = concat(frames, ignore_index=True)

		with sqlite3.connect(db_path) as conn:
			df_all.to_sql(table_name, conn, if_exists="replace", index=False)

		rows = len(df_all)

		self.logger.info(f"Tabela '{table_name}' carregada com sucesso ({rows} linhas).")

		self._gravar_checkpoint_load(
			item_name=table_name,
			status=STATUS_SUCCESSFUL,
			failure_point=None,
			ctx=ctx,
			extra={"db_path": str(db_path), "rows": rows, "indices_processados": len(frames)},
		)

		del df_all
		del frames
		gc.collect()

		self.logger.info(f"Load do pipeline '{self.pipeline}' concluído. Banco: '{db_path}'.")


	def main(self, ctx) -> None:

		ctx.configure_logging(pipeline=self.pipeline, process=self.process)
		self.logger = ctx.logger

		if ctx.env == "dev":
			pass

		if ctx.env == "prod":
			pass

		self.load(ctx)
