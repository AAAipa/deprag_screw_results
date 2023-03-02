from functools import lru_cache
from pathlib import Path

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


@lru_cache
def _get_browser_options(download_directory: Path) -> Options:
    opts = Options()

    opts.add_argument("--headless")

    opts.set_preference("browser.download.folderList", 2)
    opts.set_preference("browser.download.manager.showWhenStarting", False)
    opts.set_preference("browser.download.dir", str(download_directory))
    opts.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv/ast")

    return opts


def download_curves(download_directory: Path, deprag_ip: str, target: int) -> None:
    with Firefox(options=_get_browser_options(download_directory)) as browser:
        browser.get(
            "http://"
            + deprag_ip
            + "/cgi-bin/cgiread?site=-&request=curves&args=&mode=-1-"
        )

        dropdown = browser.find_element(By.CLASS_NAME, "dd-selected")
        dropdown.click()
        choice = browser.find_elements(By.CLASS_NAME, "dd-option")
        choice[1].click()
        downloads = browser.find_elements(By.CLASS_NAME, "download")
        downloads[target].click()


def download_fvalues(download_directory: Path, deprag_ip: str) -> None:
    with Firefox(options=_get_browser_options(download_directory)) as browser:
        browser.get(
            "http://"
            + deprag_ip
            + "/cgi-bin/cgiread?site=-&request=fvalues&args=&mode=-1-"
        )

        downloads = browser.find_elements(By.CLASS_NAME, "download")
        downloads[len(downloads) - 2].click()
