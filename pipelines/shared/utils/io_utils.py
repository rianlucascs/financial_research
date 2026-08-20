


from pathlib import Path
from pandas import DataFrame, read_csv
from pandas.errors import ParserError


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
    """Tenta ler um arquivo CSV com pandas. Se falhar, tenta novamente com engine='python'."""

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
            )

        except Exception as exc:
            
            logger.error(f"Falha ao ler '{file_path}' com fallback: {exc}")
            
            raise