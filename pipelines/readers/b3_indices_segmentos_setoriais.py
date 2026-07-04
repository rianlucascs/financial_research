

from pipelines.shared.context import PipelineContext

from datetime import datetime
from pathlib import Path
import sqlite3
from pandas import DataFrame, read_csv, read_sql_query, to_datetime


class ReaderCSVB3IndicesSegmentosSetoriais:
	"""Leitor dos arquivos brutos de carteiras diárias dos índices da B3."""


	def __init__(self):

		ctx = PipelineContext()

		self.pipeline = "b3_indices_segmentos_setoriais"

		self.path = ctx.repo_root / "financial_research" / "data" / "pipelines" / self.pipeline / "raw"


	def _raw_path(self, indice: str) -> Path:

		return self.path / indice.upper()


	def _latest_file(self, indice: str) -> Path:

		path = self._raw_path(indice)
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


	def read(self, indice: str = "IDIV", file_name: str | None = None) -> DataFrame:
		"""Lê a carteira bruta mais recente de um índice da B3."""

		indice = indice.upper()
		path_file = self._raw_path(indice) / file_name if file_name else self._latest_file(indice)

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


class ReaderSQLB3IndicesSegmentosSetoriais:
	"""Leitor dos dados carregados em SQLite para os índices da B3."""


	def __init__(self):

		ctx = PipelineContext()

		self.pipeline = "b3_indices_segmentos_setoriais"
		repo_root = ctx.repo_root / "financial_research"
		if not repo_root.exists():
			repo_root = ctx.repo_root

		self.path = repo_root / "data" / "pipelines" / self.pipeline / "load" / "b3_indices_segmentos_setoriais.db"
		self.table_name = "b3_indices_segmentos_setoriais"


	def read(self, indice: str = "IDIV") -> DataFrame:
		"""Lê do SQLite a carteira carregada para um índice da B3."""

		if not self.path.exists():
			raise FileNotFoundError(f"O banco SQLite não foi encontrado no caminho {self.path}.")

		query = f'SELECT * FROM "{self.table_name}" WHERE Indice = ? ORDER BY "Data Referencia", "Código"'

		with sqlite3.connect(self.path) as conn:
			df = read_sql_query(query, conn, params=[indice.upper()])

		if df.empty:
			raise ValueError(f"Nenhum dado encontrado no SQLite para o índice '{indice}'.")

		if "Data Referencia" in df.columns:
			df["Data Referencia"] = to_datetime(df["Data Referencia"], errors="coerce")

		return df
