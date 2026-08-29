

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ChromeDriverConfig:
    """
    Configurações para o driver do Chrome no Selenium.
    
    Args:
        ``download_path``: Caminho para o diretório de downloads do Chrome.
        ``headless``: Executa o Chrome em modo headless.
        ``window_size``: Tamanho da janela do Chrome.
        ``start_maximized``: Inicia o Chrome maximizado.
        ``incognito``: Ativa o modo de navegação anônima.
        ``disable_notifications``: Desativa notificações do navegador.
        ``allow_popups``: Permite pop-ups no navegador.
        ``disable_sandbox``: Desativa o sandbox do Chrome.
        ``disable_dev_shm_usage``: Desativa o uso de /dev/shm.
        ``allow_multiple_downloads``: Permite múltiplos downloads.
        ``enable_safe_browsing``: Ativa a navegação segura.
        ``user_agent``: Define o user agent do navegador.
        ``disable_gpu``: Desativa a GPU do Chrome.
    """
    
    download_path: str | Path | None = None
    headless: bool = True
    window_size: tuple[int, int] = (1920, 1080)
    start_maximized: bool = False
    incognito: bool = True
    disable_notifications: bool = True
    allow_popups: bool = False          
    disable_sandbox: bool = True
    disable_dev_shm_usage: bool = True
    allow_multiple_downloads: bool = True
    enable_safe_browsing: bool = True
    user_agent: str | None = None
    disable_gpu: bool = True