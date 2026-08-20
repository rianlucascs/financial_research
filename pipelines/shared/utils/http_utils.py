

import requests
from pathlib import Path


def url_is_accessible(url: str, timeout: int = 10) -> bool:
    """Verifica se uma URL está acessível via HTTP."""
    
    try:
        
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
        )

        return response.ok

    except requests.RequestException:
        
        return False
    
    
def download_file(url: str, target_path: Path, logger=None, timeout: int = 30) -> bool:
    """Baixa um arquivo de uma URL para um caminho de destino."""
    
    if not url_is_accessible(url):
        
        logger.error(f"URL não encontrada (404 ou indisponível): {url}")
        
        return None
    

    logger = logger.getChild("http")

    filename = Path(url).name
    target_path = target_path / filename

    if target_path.exists():
        target_path.unlink()

    try:
        
        response = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
        response.raise_for_status()

        with target_path.open("wb") as file:
            
            for chunk in response.iter_content(chunk_size=8192):
                
                if chunk:
                    
                    file.write(chunk)


        logger.info(f"Arquivo baixado com sucesso: {target_path}")
            
        return target_path

    except Exception as e:
        
        logger.exception(f"Falha ao baixar o arquivo CSV: {e}")
            
        return None