

from dataclasses import dataclass, replace
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import functools
from time import sleep
from pathlib import Path
from selenium.common.exceptions import TimeoutException
from typing import List, Optional, Union, Literal, Any, Callable
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from random import randint

    
USER_AGENT_ALIASES = {
    "agente_1": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


@dataclass(frozen=True)
class ChromeDriverConfig:
    download_path: str | Path | None = None
    headless: bool = True
    window_size: tuple[int, int] = (1920, 1080) 
    start_maximized: bool = False
    incognito: bool = True
    disable_notifications: bool = True
    disable_popups: bool = True
    disable_sandbox: bool = True
    disable_dev_shm_usage: bool = True
    allow_multiple_downloads: bool = True
    enable_safe_browsing: bool = True
    user_agent: str | None = None
    disable_gpu: bool = True


class SeleniumUtils:
    """Utilitários para interação com o Selenium WebDriver."""
    
    
    def __init__(self, ctx):
        
        # Reutiliza o logger do processo atual, mas com namespace próprio do Selenium.
        self.logger = ctx.logger.getChild("selenium")
        

    def chrome_options(self, config: ChromeDriverConfig | None = None, **overrides) -> Options:
        """
        Configura opções do Chrome WebDriver.

        Args:
            config: Configuração base do Chrome.
            overrides: Sobrescreve campos da configuração (kwargs).
        
        Returns:
            Objeto Options configurado para ChromeDriver
        """
        
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
        if not config.disable_popups:
            args.append("--disable-popup-blocking")
        if config.disable_sandbox:
            args.append("--no-sandbox")
        if config.disable_dev_shm_usage:
            args.append("--disable-dev-shm-usage")
        if config.user_agent:
            agent = USER_AGENT_ALIASES.get(config.user_agent, config.user_agent)
            args.append(f"--user-agent={agent}")
        if config.disable_gpu:
            args.append("--disable-gpu")

        for arg in args:
            options.add_argument(arg)

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        if config.download_path:
            path = Path(config.download_path).expanduser().resolve()
            prefs = {
                "download.default_directory": str(path),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "download.open_pdf_in_system_reader": False,
                "safebrowsing.enabled": config.enable_safe_browsing,
                "profile.default_content_settings.popups": 0,
                "profile.content_settings.exceptions.automatic_downloads.*.setting": 1 if config.allow_multiple_downloads else 0,
            }

            options.add_experimental_option("prefs", prefs)

        return options

        
    def driver(self, config: ChromeDriverConfig | None = None, **overrides) -> WebDriver:
        """
        Cria e retorna uma instância de Chrome WebDriver.

        Os parâmetros de configuração do navegador seguem o mesmo contrato de
        ``chrome_options``.
        """
            
        try:
            options = self.chrome_options(
                config=config,
                **overrides,
            )
                
        except Exception as e:
                
            self.logger.exception(f"Erro ao configurar opções do Chrome: {e}")
                
            raise
            
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
                
            self.logger.info("Chrome WebDriver iniciado com sucesso.")
                
            return driver
            
        except Exception as e:
                
            self.logger.exception(f"Erro ao iniciar o Chrome WebDriver: {e}")
                
            raise
            
    
    def find(self, driver: WebDriver, selector: str, wait: int = 10, find_all: bool = False, visible: bool = True, by: By = By.XPATH) -> Optional[Union[WebElement, List[WebElement]]]:
        """
        Encontra elementos no DOM com espera explícita.
        
        Args:
            driver: Instância WebDriver
            selector: Seletor do elemento(s) a localizar (XPath, ID, classe, etc)
            wait: Timeout em segundos para aguardar elemento
            find_all: Se True, retorna todos elementos; se False, apenas um
            visible: Se True, apenas elementos visíveis; se False, qualquer um presente
            by: Tipo de seletor (By.XPATH, By.ID, By.CLASS_NAME, etc)
        
        Returns:
            WebElement, lista de WebElements, ou None/[] se não encontrado
        """
        
        if not selector:

            self.logger.warning("Seletor vazio fornecido para find()")

            return [] if find_all else None

        # Define a condição de espera com base nos parâmetros fornecidos
        if find_all:

            # retorna todos elementos
            condition = ( 
                EC.visibility_of_all_elements_located 
                if visible 
                else EC.presence_of_all_elements_located
            )

        else:

            # retorna apenas o primeiro elemento
            condition = (
                EC.visibility_of_element_located
                if visible
                else EC.presence_of_element_located
            )

        try:

            # Aguarda até que o elemento esteja presente ou visível, dependendo do parâmetro `visible`
            element = WebDriverWait(driver, wait).until(
                condition((by, selector))
            )

            return element
            
        except TimeoutException:

            # Loga um aviso se o elemento não for encontrado dentro do tempo limite
            self.logger.warning(f"Elemento não encontrado após {wait}s: {selector}")

            return [] if find_all else None

        except Exception as e:
            
            # Loga qualquer outro erro inesperado durante a busca do elemento
            self.logger.error(f"Erro ao procurar elemento: {e}", exc_info=True)

            # Retorna uma lista vazia ou None dependendo do parâmetro find_all
            return [] if find_all else None


    def safe_click(self, driver: WebDriver, selector: str, wait: int = 10, by: By = By.XPATH) -> bool:
        """
        Realiza clique robusto com fallback JavaScript.

        Tenta clicar no elemento de forma normal, e se falhar, usa JavaScript.
        
        Args:
            driver: Instância WebDriver
            selector: Seletor do elemento (XPath, ID, classe, etc)
            wait: Timeout em segundos para aguardar elemento clicável
            by: Tipo de seletor (By.XPATH, By.ID, By.CLASS_NAME, etc)
        
        Returns:
            True se clique bem-sucedido, False caso contrário
        """

        if not selector:
            
            self.logger.warning("Seletor vazio fornecido para safe_click()")

        try:

            element = WebDriverWait(driver, wait).until(
                EC.element_to_be_clickable((by, selector))
            )

            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                element
            )

            element.click() 

        except Exception as e:

            try:
                element = WebDriverWait(driver, wait).until(
                    EC.presence_of_element_located((by, selector))
                )

                driver.execute_script(
                    "arguments[0].click();",
                    element
                )
                
            except Exception as e2:

                self.logger.warning(
                    f"Erro ao clicar em {selector}. "
                    f"Tentativa normal falhou com: {e}. "
                    f"Fallback JavaScript falhou com: {e2}",
                    exc_info=True,
                )


    def close_window(self, driver: WebDriver) -> None:
        """Fecha a janela/aba atual do navegador."""
        
        try:
            driver.close()
            
            self.logger.debug("Janela fechada com sucesso")

        except Exception as e:
            
            self.logger.error(f"Erro ao fechar janela: {e}")


    def quit(self, driver: WebDriver) -> None:
        """Encerra o driver do Selenium e fecha todas as janelas."""

        if driver is None:
            
            self.logger.warning("Driver é None, não há nada para encerrar.")
            
            return
        
        try:
            
            driver.quit()
            
            self.logger.info("Driver fechado")

        except Exception as e:
            
            self.logger.error(f"Erro ao encerrar driver: {e}")


    @property
    def random_delay(self) -> int:
        """Retorna um valor aleatório de atraso em segundos."""
        
        time = randint(5, 20)
        
        if type(time) is not int:
            
            return 5

        return time
    
