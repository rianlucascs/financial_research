

from pipelines.shared.utils.selenium_utils.config import ChromeDriverConfig
from pipelines.shared.utils.selenium_utils.driver_factory import ChromeDriverFactory


import logging
from contextlib import contextmanager
from typing import Iterator
from selenium.webdriver.remote.webdriver import WebDriver


class BrowserSession:
    """Gerencia o ciclo de vida do WebDriver: fecha/encerra mesmo em caso de exceção."""


    def __init__(
        self, 
        factory: ChromeDriverFactory, 
        logger: logging.Logger
    ) -> None:
        
        self.factory = factory
        self.logger = logger.getChild("browser_session")


    @contextmanager
    def open(self, config: ChromeDriverConfig | None = None, **overrides) -> Iterator[WebDriver]:
        
        driver = self.factory.create(config=config, **overrides)
        
        try:
            
            yield driver
            
        finally:
            
            self._quit(driver)


    def _quit(self, driver: WebDriver) -> None:
        
        try:
            
            driver.quit()
            self.logger.info("Driver encerrado.")
            
        except Exception:
            
            self.logger.error("Erro ao encerrar driver.", exc_info=True)
            

# factory = ChromeDriverFactory(logger)
# browser_session = BrowserSession(factory, logger)

# with browser_session.open(config) as driver:
#     finder.find_one(driver, "//button[@id='baixar']")
#     interactor.safe_click(driver, "//button[@id='baixar']")

# # driver.quit() garantido, mesmo se algo acima levantar exceção