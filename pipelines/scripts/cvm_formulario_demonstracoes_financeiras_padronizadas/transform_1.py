

from pipelines.shared.checkpoint_values import (
    FAILURE_PROCESSED_EXCEPTION,
    STATUS_FAILED,
    STATUS_SUCCESSFUL,
)

from .settings import (
    CHECKPOINT_STAGE_PROCESSED, 
    CHECKPOINT_STEP_PROCESSED_1, 
    DFPS
    )

from pipelines.shared.checkpoint_contract import build_checkpoint_payload

import gc
from datetime import date
from pandas import DataFrame, concat, read_csv


class TransformCVMFormularioDemonstracoesFinanceirasPadronizadasStep1:
    """Concatena os CSVs brutos anuais (2011 até o ano corrente) de cada tipo de demonstração DFP (CVM),
    salvando o resultado consolidado na camada interim e gravando checkpoint de sucesso ou falha."""
    
    
    def __init__(self, pipeline: str):
        
        self.pipeline = pipeline
        self.process = "transform_1"
        self.logger = None


    def _gravar_checkpoint_transform_1(self, step: str, item_name: str, status: str, failure_point: str, ctx, extra: dict = None) -> None:
        
        extra_payload = {"item_name": item_name}
        if extra:
            extra_payload.update(extra)

        try:
            payload = build_checkpoint_payload(
                pipeline=self.pipeline,
                stage=CHECKPOINT_STAGE_PROCESSED,
                step=step,
                status=status,
                run_id=ctx.run_id,
                environment=ctx.env,
                failure_point=failure_point,
                source="CVM",
                extra=extra_payload,
            )
            ctx.write_checkpoint(
                self.pipeline,
                CHECKPOINT_STAGE_PROCESSED,
                step,
                item_name,
                payload,
            )
        
        except Exception as e:
            
            self.logger.exception(f"Falha ao gravar checkpoint de download para '{item_name}'")
    
    
    def _transform_1(self, ctx) -> None:
        
        year_now = date.today().year
        
        self.logger.info(f"Iniciando transform_1 do pipeline '{self.pipeline}' para o período 2011-{year_now}.")

        for dfp_name in DFPS:
            try:
                
                df = DataFrame()

                # Define o nome do arquivo CSV consolidado para cada tipo de demonstração financeira (DFP).
                filename = f"dfp_cia_aberta_{dfp_name}_2011-{year_now}.csv"
                raw_path, interim_path = ctx.prepare_interim_path(self.pipeline)
                path_iterim_csv = interim_path / filename

                # garante que o arquivo interim seja sempre atualizado, mesmo que já exista um prévio.
                ctx.delete_file(path_iterim_csv) 
                    
                for for_year in range(2011, year_now + 1):
                        
                    try:
                        name_raw_csv = f"dfp_cia_aberta_{dfp_name}_{for_year}.csv"
                        path_raw_csv = raw_path / "csv" / name_raw_csv

                        df_raw_csv = read_csv(path_raw_csv, sep=";", decimal=",", encoding="iso-8859-1")

                    except Exception as e:
                            
                        if for_year == year_now:
                                
                            self.logger.error(f"Erro ao abrir o arquivo '{name_raw_csv}'.", exc_info=False)

                        else:
                                
                            self.logger.error(f"Erro ao abrir o arquivo '{name_raw_csv}': {e}", exc_info=True)

                        continue # Continua para o próximo ano, mesmo em caso de erro.
                        
                    # Concatenando os dados do arquivo CSV do ano atual com o DataFrame acumulado.
                    df = concat([df, df_raw_csv])
                    
                # Salva o DataFrame concatenado em um arquivo CSV no diretório interim.
                df.to_csv(path_iterim_csv, index=False, encoding="utf-8", mode="w")

                # Libera memória após a criação do arquivo CSV concatenado.
                del df
                del df_raw_csv
                    
                gc.collect()
                    
                self.logger.info(f"Arquivo '{filename}' criado e salvo com sucesso.")


                # Grava o checkpoint de sucesso para a etapa transform_1.
                self._gravar_checkpoint_transform_1(
                    CHECKPOINT_STEP_PROCESSED_1,
                    dfp_name,
                    STATUS_SUCCESSFUL,
                    None,
                    ctx,
                    extra={"dfp_name": dfp_name},
                )

                self.logger.info(f"Sucesso no transform_1 para {dfp_name}")

            except Exception as e:
                
                # Grava o checkpoint de falha para a etapa transform_1.
                self._gravar_checkpoint_transform_1(
                    CHECKPOINT_STEP_PROCESSED_1,
                    dfp_name,
                    STATUS_FAILED,
                    FAILURE_PROCESSED_EXCEPTION,
                    ctx,
                    extra={"dfp_name": dfp_name},
                )
                
                self.logger.error(f"Erro no transform_1 para '{dfp_name}': {e}", exc_info=True)
        
        
        self.logger.info(f"Transform_1 do pipeline '{self.pipeline}' concluído para o período 2011-{year_now}.")   
        
    def main(self, ctx) -> None:

        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        if ctx.env == "dev":
            pass
        
        if ctx.env == "prod":
            pass
        
        # Executa a etapa de transformação 1 do pipeline.
        self._transform_1(ctx)
        