

from pipelines.shared.utils.selenium_utils.config import ChromeDriverConfig

import functools
from random import choice
import logging
from dataclasses import replace
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


@functools.lru_cache(maxsize=1)
def _resolve_driver_path() -> str:
    return ChromeDriverManager().install()
 
  
USER_AGENT_ALIASES = {
    "agente_1": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    "agente_2": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    "agente_3": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
}


def _resolve_user_agent(user_agent: str | None) -> str:
    """
    Resolve a string final de User-Agent.

    - user_agent is None: escolhe aleatoriamente um dos USER_AGENT_ALIASES.
    - user_agent é uma chave conhecida (ex: "agente_1"): resolve o alias.
    - user_agent é qualquer outra string: usa como UA literal (passthrough).
    """
    
    if user_agent is None:
        return choice(list(USER_AGENT_ALIASES.values()))

    return USER_AGENT_ALIASES.get(user_agent, user_agent)


class ChromeDriverFactory:
    """Constrói opções e instâncias de Chrome WebDriver a partir de ChromeDriverConfig."""


    def __init__(
        self, 
        logger: logging.Logger
        ) -> None:
        
        self.logger = logger.getChild("chrome_driver_factory")


    def build_options(self, config: ChromeDriverConfig | None = None, **overrides) -> Options:
        
        config = config or ChromeDriverConfig()
        
        if overrides:
            
            config = replace(config, **overrides)

        options = Options()
        args = ["--disable-blink-features=AutomationControlled"]

        if config.headless:
            args.append("--headless=new")
            args.append(f"--window-size={config.window_size[0]},{config.window_size[1]}")
            
        elif config.start_maximized:
            args.append("--start-maximized")

        if config.incognito:
            args.append("--incognito")
            
        if config.disable_notifications:
            args.append("--disable-notifications")
            
        if config.allow_popups:
            args.append("--disable-popup-blocking")
            
        if config.disable_sandbox:
            args.append("--no-sandbox")
            
        if config.disable_dev_shm_usage:
            args.append("--disable-dev-shm-usage")
            
        if config.user_agent:
            agent = _resolve_user_agent(config.user_agent)
            args.append(f"--user-agent={agent}")
            
        if config.disable_gpu:
            args.append("--disable-gpu")

        for arg in args:
            options.add_argument(arg)

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        if config.download_path:
            
            path = Path(config.download_path).expanduser().resolve()
            
            options.add_experimental_option("prefs", {
                "download.default_directory": str(path),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "download.open_pdf_in_system_reader": False,
                "safebrowsing.enabled": config.enable_safe_browsing,
                "profile.default_content_settings.popups": 0,
                "profile.content_settings.exceptions.automatic_downloads.*.setting": (
                    1 if config.allow_multiple_downloads else 0
                ),
            })

        return options


    def create(self, config: ChromeDriverConfig | None = None, **overrides) -> WebDriver:
        
        
        try:
            options = self.build_options(config=config, **overrides)
            
        except Exception:
            
            self.logger.exception("Erro ao configurar opções do Chrome.")
            
            raise

        try:
            
            service = Service(_resolve_driver_path())
            driver = webdriver.Chrome(service=service, options=options)
            self.logger.info("Chrome WebDriver iniciado com sucesso.")
            
            return driver
        
        except Exception:
            
            self.logger.exception("Erro ao iniciar o Chrome WebDriver.")
            
            raise