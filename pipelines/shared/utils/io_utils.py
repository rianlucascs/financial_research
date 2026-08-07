


from pathlib import Path


def remove_file(zip_path: Path, logger) -> None:
    
    try:
        
        if zip_path.exists():
            
            zip_path.unlink(missing_ok=True)
        
        else:
            
            logger.info(f"O arquivo ZIP {zip_path} não existe. Nenhuma ação necessária.")
        
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
        
        logger.info(f"O diretório '{path}' não existe. Nenhuma ação necessária.")
        
        return

    if not path.is_dir():
        
        logger.warning(f"'{path}' não é um diretório.")
        
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