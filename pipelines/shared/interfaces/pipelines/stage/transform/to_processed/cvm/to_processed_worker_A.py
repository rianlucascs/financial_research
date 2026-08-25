"""
Worker:
    to_processed_worker_a

Responsabilidades:
    Concatena os CSVs brutos anuais (2011 até o ano corrente) em um único arquivo Parquet processado
    e adicionando colunas derivadas, se necessário.
    
Notas:
    Caso o pipelines seja executado no mesmo dia em que os arquivos InterimData foram gerados, 
    o worker irá sobrescrever os arquivos Parquet processados existentes.
    
    ``pipeline_settings`` deve conter:
        - ``file_prefix``: Prefixo do arquivo, por exemplo, "itr_cia_aberta" ou "dfp_cia_aberta".
        - ``file_identifiers``: Lista de identificadores de arquivo, por exemplo, ["BPA", "BPP", "DFC", "DRE", "ITR"].
        - ``start_year``: Ano de início para a concatenação, por exemplo, 2011 ou 2010.
        
    ---
    
    O pipeline ``cvm_formulario_de_referencia`` possui anos ausentes  ex: (2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021) 
    e não possui arquivos Parquet intermediários para esses anos.
    
    
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_workers import ToProcessedWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Step, Status
from pipelines.shared.utils.io_utils import clear_directory

from datetime import date
from pandas import DataFrame, read_parquet
import pyarrow.parquet as pq
import pyarrow as pa
import gc


class ToProcessedWorkerInterfaceA(ToProcessedWorkersInterface):
    """
    Métodos que a subclasse pode sobrescrever:
        ``_add_derived_columns``: Permite adicionar colunas derivadas ao DataFrame antes de concatená-lo e salvá-lo como Parquet.
    """
    
    
    process: str = "to_processed_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )

    
    def _add_derived_columns(self, df: DataFrame) -> DataFrame | None:
        """
        Adiciona colunas derivadas ao DataFrame.

        Retorna o DataFrame modificado ou None se nenhuma modificação for necessária.
        """
        
        # df["ORIGEM_FORMULARIO"] = "ITR" 
        
        # if ("DT_INI_EXERC" in df.columns) and ("DT_FIM_EXERC" in df.columns):
        #     df["INTERVALO_EXERC"] = (df["DT_FIM_EXERC"] - df["DT_INI_EXERC"]).dt.days
            
        # return df
        
        return None


    def _next_year_parquet_exists(self, interim_parquet_path: str, prefix: str, identifier: str, year: int) -> bool:
        """verifica se o arquivo Parquet intermediário para o próximo ano existe."""
        
        if (interim_parquet_path / f"{prefix}_{identifier}_{year + 1}.parquet".replace("__", "_")).exists():
            
            return True
        
        else:
            
            self.logger.info(f"Arquivo Parquet intermediário para o próximo ano não encontrado: {prefix}_{identifier}_{year + 1}.parquet."
                                f" Finalizando a concatenação para o identificador '{identifier}' e ano {year}.")
            
            return False
    
    
    def _worker(self, ctx: PipelineContext) -> None:
        
        current_year = date.today().year
        
        processed_parquet_path = ctx.prepare_transformed_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_stage="to_processed", 
            subdir_format="parquet"
        )
        
        interim_parquet_path = ctx.build_transformed_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_stage="to_interim", 
            subdir_format="parquet"
        )
        
        prefix = getattr(self.settings, "file_prefix", None) # itr_cia_aberta, dfp_cia_aberta
        if prefix is None:
            self.logger.error(f"Prefixo de arquivo não definido nas configurações do pipeline '{self.pipeline}'.")
            return
        
        file_identifiers = getattr(self.settings, "file_identifiers", None)
        if file_identifiers is None:
            self.logger.error(f"Lista de identificadores de arquivo não definida nas configurações do pipeline '{self.pipeline}'.")
            return
        
        start_year = getattr(self.settings, "start_year", None) # 2011, 2010
        if start_year is None or not isinstance(start_year, int) or start_year <= 0:
            self.logger.error(f"Ano de início inválido nas configurações do pipeline '{self.pipeline}': {start_year}. Deve ser um inteiro positivo.")
            return
        
        clear_directory(processed_parquet_path, logger=self.logger, remove_root=False)
        
        for identifier in file_identifiers:
            
            # Monta o caminho do arquivo Parquet processado final
            filename = f"{prefix}_{identifier}_{start_year}-{current_year}.parquet".replace("__", "_") 

            parquet_file_path = processed_parquet_path / filename
            
            writer = None
            years_written: list[int] = []
            
            try:
                
                for year in range(start_year, current_year + 1):
                    
                    # Monta o caminho do arquivo Parquet intermediário
                    
                    interim_file = f"{prefix}_{identifier}_{year}.parquet".replace("__", "_")
                    interim_file_path = interim_parquet_path / interim_file
                    
                    if not interim_file_path.exists():
                        
                        self.logger.warning(f"Arquivo Parquet intermediário não encontrado: {interim_file}, ano {year}. Pulando este arquivo.")
                    
                        continue
                    
                    df_interim = read_parquet(interim_file_path, engine="pyarrow")
                    
                    if df_interim.empty:
                        
                        del df_interim
                        gc.collect()
                        
                        self.logger.error(f"Arquivo Parquet intermediário vazio: {interim_file_path}. Pulando este arquivo.")
                        
                        continue
                    
                    df_derived = self._add_derived_columns(df_interim)
                    if df_derived is not None:
                        df_interim = df_derived
                    
                    table = pa.Table.from_pandas(
                        df_interim,
                        preserve_index=False,
                    )
                    
                    del df_interim
                    gc.collect()
                    
                    if writer is None:
                        writer = pq.ParquetWriter(
                            parquet_file_path,
                            table.schema,
                        )

                    writer.write_table(table)
                    
                    del table
                    gc.collect()
                    
                    years_written.append(year)

            except Exception as e:
                
                self.logger.error(f"Falha ao concatenar identificador '{identifier}': {e}")
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.TO_PROCESSED,
                    step=Step.CONCATENATE,
                    filename=f"to_processed_worker_a.failure.{identifier}.json",
                    status=Status.FAILED,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={
                        "demonstration_code": identifier, 
                        "error": str(e), 
                        "years_written": years_written
                    },
                )
                
                continue
        
            finally:
                
                if writer is not None:
                    writer.close()
                
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.TO_PROCESSED,
                step=Step.CONCATENATE,
                filename=f"to_processed_worker_a.success.{identifier}.json",
                status=Status.SUCCESSFUL,
                source=getattr(self.settings, "url", self.pipeline),
                extra={
                    "demonstration_code": identifier,
                    "years": years_written,
                    "processed_file_path": str(parquet_file_path),
                    }
            )
            