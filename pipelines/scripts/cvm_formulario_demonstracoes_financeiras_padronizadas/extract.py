
from pipelines.shared.checkpoint_values import (
    STATUS_SUCCESSFUL,
    STATUS_FAILED,
    STATUS_NO_FILE_DETECTED,
    FAILURE_EXCEPTION,
    FAILURE_FILE_DETECTION,
)

from .settings import (
    CHECKPOINT_STAGE_EXTRACT,
    CHECKPOINT_STEP_DOWNLOAD_ZIP,
    CHECKPOINT_STAGE_EXTRACT_ZIP,
    DOWNLOAD_MAX_ATTEMPTS,
    URL,
    ARCHIVES_ZIP
)

from pipelines.shared.checkpoint_contract import build_checkpoint_payload

import json
import wget
from zipfile import ZipFile
import gc


class ExtractCVMFormularioDemonstracoesFinanceirasPadronizadas:
    """
    Classe responsável pela extração dos formulários de demonstrações financeiras padronizadas da CVM.
    """
    
    def __init__(self, pipeline):
        
        self.pipeline = pipeline
        self.process = "extract"
        self.driver = None
        self.logger = None
    
    
    def main(self, ctx):
        
        # Configura o logger e o ambiente
        ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = ctx.logger
        
        if ctx.env == "dev":
            pass
        
        if ctx.env == "prod":
            pass
        
        # Executa o download e extração dos arquivos zip
        download_zip_files = DownloadZipFiles(pipeline=self.pipeline)
        download_zip_files.main(ctx)
        
        # Executa a extração dos arquivos zip
        extract_zip_files = ExtractZipFiles(pipeline=self.pipeline)
        extract_zip_files.main(ctx)


class DownloadZipFiles(ExtractCVMFormularioDemonstracoesFinanceirasPadronizadas):
    """
    Classe responsável pelo download dos arquivos zip.
    """


    def _gravar_checkpoint_download(self, filename, status, failure_point, attempts, ctx):
        
        try:
            payload = build_checkpoint_payload(
                pipeline=self.pipeline,
                stage=CHECKPOINT_STAGE_EXTRACT,
                step=CHECKPOINT_STEP_DOWNLOAD_ZIP,
                status=status,
                run_id=ctx.run_id,
                environment=ctx.env,
                failure_point=failure_point,
                source="CVM",
                extra={
                    "filename": filename,
                    "attempts": attempts,
                },
            )
            ctx.write_checkpoint(
                self.pipeline,
                CHECKPOINT_STAGE_EXTRACT,
                CHECKPOINT_STEP_DOWNLOAD_ZIP,
                filename,
                payload,
            )
            return True
        
        except Exception as e:
            
            self.logger.exception(f"Falha ao gravar checkpoint de download para '{filename}': {e}")
            
            raise


    def _atualiza_ultimo_download_zip_file(self, filename, ctx):

        # sempre apagar o ultimo arquivo para garantir que estamos baixando a versão mais recente, 
        # já que a CVM pode atualizar o arquivo mantendo o mesmo nome
        
        ultimo = ARCHIVES_ZIP[-1]
        penultimo = ARCHIVES_ZIP[-2]
        position = 'ultimo' if filename == ultimo else 'penultimo' if filename == penultimo else 'desconhecido'

        if (ultimo != filename) and (penultimo != filename):
            return False

        try:
            raw_path_zip = ctx.path_raw(self.pipeline, "zip")
            zip_file_path = raw_path_zip / filename

            if zip_file_path.exists():
                zip_file_path.unlink()
                
                self.logger.info(f"Arquivo ZIP removido ({position}): {filename}")
                
                return True

            self.logger.info(f"Arquivo ZIP não encontrado para remoção ({position}): {filename}")
            
            return False

        except Exception as e:
            
            self.logger.error(f"Erro ao remover {position} arquivo ZIP '{filename}': {e}")
            
            return False
        
        
    def _deve_fazer_download_zip_file(self, filename, ctx):
        
        try:
            
            # Ler o checkpoint para verificar se o download já foi realizado com sucesso anteriormente
            checkpoint_file = ctx.checkpoint_file(
                self.pipeline,
                CHECKPOINT_STAGE_EXTRACT,
                CHECKPOINT_STEP_DOWNLOAD_ZIP,
                filename,
            )

            path_file = ctx.path_raw(self.pipeline, "zip") / filename

            # se ambos o checkpoint e o arquivo existirem, assumimos que o download foi bem-sucedido anteriormente e pulamos
            if not checkpoint_file.exists() or not path_file.exists():
                return True, "checkpoint_ou_arquivo_nao_existe"

            # Ambos arquivos exitem, vamos ler o checkpoint para entender o status do download

            with open(checkpoint_file, "r", encoding="utf-8") as fp:
                checkpoint = json.load(fp)

            status = checkpoint.get("status")
            failure_point = checkpoint.get("failure_point")

            if status == STATUS_SUCCESSFUL and failure_point is None and path_file.exists(): # Pulando download.                
                return False, "ja_existe_sucesso"

            if status == STATUS_FAILED: # Reprocessando download
                return True, "falha_anterior"
            
            if failure_point != None: # Reprocessando download
                return True, f"falha_no_ponto_{failure_point}"

            return True, "status_desconhecido"
        
        except Exception as e: # Reprocessando download
            return True, "erro_leitura_checkpoint"


    def _limpar_arquivo_anterior_download_zip_file(self, filename, ctx):
        """Remove arquivo ZIP anterior para refazer download limpo.

        Retorna: bool
            - True: arquivo removido ou não existia
            - False: erro ao tentar remover
        """
        
        try:
            
            # Ler o checkpoint para verificar se há um arquivo anterior a ser removido
            raw_path_zip = ctx.path_raw(self.pipeline, "zip")
            checkpoint_file = ctx.checkpoint_file(
                self.pipeline,
                CHECKPOINT_STAGE_EXTRACT,
                CHECKPOINT_STEP_DOWNLOAD_ZIP,
                filename,
            )

            arquivo_anterior = filename

            if checkpoint_file.exists():
                
                with open(checkpoint_file, "r", encoding="utf-8") as fp:
                    checkpoint = json.load(fp)
                    
                arquivo_anterior = checkpoint.get("filename") or filename

            arquivo_path = raw_path_zip / arquivo_anterior

            if arquivo_path.exists():
                arquivo_path.unlink()
                
                self.logger.info(f"Arquivo anterior removido: {arquivo_anterior}")
                
            else:
                
                self.logger.debug(f"Arquivo anterior não encontrado para remoção: {arquivo_anterior}")

            return True

        except Exception as e:
            
            self.logger.error(f"Erro ao limpar arquivo anterior '{filename}': {e}")
            
            return False

        
    def _download_zip_file(self, filename, raw_path_zip):
        
        url = f"{URL}{filename}"
        output_path = f"{raw_path_zip}/{filename}"
        
        try:
            result = wget.download(url, out=output_path, bar=False)
            return result
        
        except Exception as e:
            
            self.logger.error(f"Erro ao baixar o arquivo '{filename}': {e}")
            
            return None
        
        
    def main(self, ctx=None):

        self.logger = ctx.logger

        raw_path_zip = ctx.prepare_raw_path(self.pipeline, 'zip')
        
        # faça o download
        for filename in ARCHIVES_ZIP:

            self._atualiza_ultimo_download_zip_file(filename, ctx)

            deve_fazer, motivo = self._deve_fazer_download_zip_file(filename, ctx)
            
            self.logger.info(f"Verificação de download para '{filename}': {'Fazendo download' if deve_fazer else 'Pulando download'} (motivo: {motivo})")
            
            # se não deve fazer o download, continue para o próximo arquivo
            if not deve_fazer:
                continue

            self._limpar_arquivo_anterior_download_zip_file(filename, ctx)
            
            tentativas = 0
            max_tentativas = DOWNLOAD_MAX_ATTEMPTS

            while tentativas < max_tentativas:
                
                # tente baixar o arquivo ZIP
                result_download = self._download_zip_file(filename, raw_path_zip)

                # se o download falhar, incremente as tentativas e tente novamente
                if not result_download:
                    tentativas += 1
                    
                    self.logger.warning(f"Tentativa {tentativas} de {max_tentativas} para baixar '{filename}'")
                    
                    continue # tente novamente
                
                else:
                    break # se o download for bem-sucedido, saia do loop de tentativas
            
            # se o download falhou após o número máximo de tentativas, registre um erro e continue para o próximo arquivo
            if not result_download:
                
                self.logger.error(f"Falha ao baixar '{filename}' após {max_tentativas} tentativas. Pulando para o próximo arquivo.")
                
                self._gravar_checkpoint_download(
                    filename=filename,
                    status=STATUS_FAILED,
                    failure_point=FAILURE_EXCEPTION,
                    attempts=tentativas,
                    ctx=ctx,
                )
                
                continue

            else:
                
                # se o download for bem-sucedido, salve o checkpoint
                self._gravar_checkpoint_download(
                    filename=filename,
                    status=STATUS_SUCCESSFUL,
                    failure_point=None,
                    attempts=tentativas + 1,
                    ctx=ctx,
                )

            self.logger.info(f"Download do arquivo '{filename}' concluído com sucesso em {tentativas + 1} tentativas.")
            


class ExtractZipFiles(ExtractCVMFormularioDemonstracoesFinanceirasPadronizadas):
    """
    Classe responsável pela extração dos arquivos zip.
    """
    
    def main(self, ctx):
        pass
