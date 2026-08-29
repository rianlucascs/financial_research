

import logging
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
CLICK_RETRY_EXCEPTIONS = (
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)


class ElementInteractor:
    """Interações robustas com elementos (clique com fallback JS)."""


    def __init__(
        self, 
        logger: logging.Logger
    ) -> None:
        
        self.logger = logger.getChild("element_interactor")
        

    def safe_click(self, driver: WebDriver, selector: str, wait: int = 10, by: str = "xpath") -> None:
        """
        Clica no elemento; usa fallback via JavaScript se o clique nativo falhar
        por timeout, interceptação ou elemento não interagível.

        Propaga a exceção se nem o clique nativo nem o fallback JS funcionarem.
        """
        
        if not selector:
            
            self.logger.warning("Seletor vazio fornecido para safe_click().")
            
            return

        try:
            
            element = WebDriverWait(driver, wait).until(EC.element_to_be_clickable((by, selector)))
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
            
        except CLICK_RETRY_EXCEPTIONS as e:
            
            try:
                
                element = WebDriverWait(driver, wait).until(EC.presence_of_element_located((by, selector)))
                driver.execute_script("arguments[0].click();", element)
                
            except Exception as e2:
                
                self.logger.warning(
                    f"Erro ao clicar em {selector}. Tentativa normal falhou com: {e}. "
                    f"Fallback JavaScript falhou com: {e2}",
                    exc_info=True,
                )
                
                raise