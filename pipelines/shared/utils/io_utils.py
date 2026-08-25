


from pathlib import Path
from pandas import DataFrame, read_csv
from pandas.errors import ParserError
from csv import QUOTE_NONE


def remove_file(zip_path: Path, logger) -> None:
    
    try:
        
        if zip_path.exists():
            
            zip_path.unlink(missing_ok=True)
        
        # else:
            
        #     logger.info(f"O arquivo ZIP {zip_path} não existe. Nenhuma ação necessária.")
        
    except Exception as e:
        
        logger.warning(f"Falha ao excluir o arquivo ZIP {zip_path}: {e}")


def clear_directory(path: Path, logger, remove_root: bool = True) -> None:
    """Remove o conteúdo de um diretório e, opcionalmente, o próprio diretório.

    Args:
        path: Diretório a ser limpo.
        logger: Logger para registrar avisos e erros.
        remove_root: Se True (padrão), remove também `path` ao final.
            Se False, apenas esvazia `path`, mantendo-o no lugar.
    """

    if not path.exists():
        return

    if not path.is_dir():
        return

    for item in path.iterdir():
        try:
            
            if item.is_file():
                
                item.unlink()
                
            elif item.is_dir():
                # Subdiretórios são sempre removidos por completo,
                # independente do valor de remove_root no nível raiz.
                
                clear_directory(item, logger, remove_root=True)
                
        except OSError as e:
            
            logger.error(f"Falha ao remover '{item}': {e}")

    if remove_root:
        
        try:
            path.rmdir()
            
        except OSError as e:
            
            logger.error(f"Falha ao remover o diretório '{path}': {e}")
            

def read_csv_with_fallback(file_path, logger, sep=";", encoding="iso-8859-1") -> DataFrame:
    """Tenta ler um arquivo CSV com pandas. Se falhar, tenta novamente com engine='python'.
    Se ainda assim falhar (linhas com delimitadores não escapados no conteúdo), ignora as linhas malformadas.
    """

    try:
        
        return read_csv(file_path, sep=sep, encoding=encoding, dtype=str)
    
    except ParserError as exc:
        
        logger.warning(f"Falha no parser em '{file_path}' ({exc}). Aplicando fallback com engine='python'.")

        try:
            
            return read_csv(
                file_path,
                sep=sep,
                encoding=encoding,
                dtype=str,
                engine="python",
                quoting=QUOTE_NONE,
            )

        except ParserError as exc:
            
            logger.warning(f"Falha no fallback em '{file_path}' ({exc}). Ignorando linhas malformadas.")

            bad_lines: list[list[str]] = []

            def _on_bad_line(bad_line: list[str]) -> None:
                bad_lines.append(bad_line)
                return None

            try:

                df = read_csv(
                    file_path,
                    sep=sep,
                    encoding=encoding,
                    dtype=str,
                    engine="python",
                    quoting=QUOTE_NONE,
                    on_bad_lines=_on_bad_line,
                )

                if bad_lines:

                    logger.warning(f"'{file_path}': {len(bad_lines)} linha(s) malformada(s) ignorada(s).")

                return df

            except Exception as exc:

                logger.error(f"Falha ao ler '{file_path}' ignorando linhas malformadas: {exc}")

                raise

        except Exception as exc:
            
            logger.error(f"Falha ao ler '{file_path}' com fallback: {exc}")
            
            raise