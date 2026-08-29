

import logging
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ElementFinder:
    """Localiza elementos no DOM com espera explícita."""


    def __init__(
        self, 
        logger: logging.Logger
    ) -> None:
        
        self.logger = logger.getChild("element_finder")
        

    def find_one(
        self, driver: WebDriver, selector: str, wait: int = 10,
        visible: bool = True, by: str = "xpath",
    ) -> WebElement | None:
        
        if not selector:
            
            self.logger.warning("Seletor vazio fornecido para find_one().")
            
            return None

        condition = EC.visibility_of_element_located if visible else EC.presence_of_element_located
        
        try:
            
            return WebDriverWait(driver, wait).until(condition((by, selector)))
        
        except TimeoutException:
            
            self.logger.warning(f"Elemento não encontrado após {wait}s: {selector}")
            
            return None
        
        except Exception:
            
            self.logger.error(f"Erro ao procurar elemento: {selector}", exc_info=True)
            
            return None


    def find_all(
        self, driver: WebDriver, selector: str, wait: int = 10,
        visible: bool = True, by: str = "xpath",
    ) -> list[WebElement]:
        
        if not selector:
            
            self.logger.warning("Seletor vazio fornecido para find_all().")
            
            return []

        condition = EC.visibility_of_all_elements_located if visible else EC.presence_of_all_elements_located
        
        try:
            
            return WebDriverWait(driver, wait).until(condition((by, selector)))
        
        except TimeoutException:
            
            self.logger.warning(f"Elementos não encontrados após {wait}s: {selector}")
            
            return []
        
        except Exception:
            
            self.logger.error(f"Erro ao procurar elementos: {selector}", exc_info=True)
            
            return []