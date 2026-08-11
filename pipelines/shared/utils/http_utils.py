

import requests


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