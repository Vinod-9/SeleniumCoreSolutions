from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from Listeners.logger_settings import ui_logger


def _wait_for_loader_to_disappear(self, timeout=15, max_retries=None):
    """
    Waits until any common loading spinners or overlays are gone.
    Keeps retrying even if timeout is exceeded, unless max_retries is set.
    """
    loader_locator = (By.CSS_SELECTOR,
                      '.dw-loading-active, [aria-busy="true"], '
                      '[id="spinner"], [class="fa fa-3x fa-refresh fa-spin"], '
                      '[loader_uIBlocker], [class="spinner-border spinner-border-sm"],'
                      '[class="spinner-border spinner-border-sm"]'
                      )

    retries = 0
    while True:
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.5).until_not(
                EC.presence_of_element_located(loader_locator)
            )
            break  # Loader disappeared successfully
        except TimeoutException:
            retries += 1
            ui_logger.warning(f"[Retry {retries}] Loader still visible after {timeout} seconds...")
            if max_retries and retries >= max_retries:
                ui_logger.error("Loa/spinner der did not disappear after maximum retries.")
                break
