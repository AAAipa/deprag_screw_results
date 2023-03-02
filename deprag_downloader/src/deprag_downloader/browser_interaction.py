from functools import lru_cache
from pathlib import Path
import time

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@lru_cache
def _get_browser_options(download_directory: Path) -> Options:
    opts = Options()

    opts.add_argument("--headless")

    opts.set_preference("browser.download.folderList", 2)
    opts.set_preference("browser.download.manager.showWhenStarting", False)
    opts.set_preference("browser.download.dir", str(download_directory))
    opts.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv/ast")

    return opts


def download_curves(download_directory: Path, file_name: str, deprag_ip: str, target: int, wait_time: int = 60) -> None:
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
        
        # The magic below is based on the answer here: https://stackoverflow.com/a/56570364
        # Open the downloads window in the browser
        browser.execute_script("window.open()")
        WebDriverWait(browser,10).until(EC.new_window_is_opened)
        browser.switch_to.window(browser.window_handles[-1])
        browser.get("about:downloads")
        
        # Poll for the download to complete -- but it should be completed already, though?
        endTime = time.time() + wait_time
        while True:
            try:
                downloaded_file_name = browser.execute_script("return document.querySelector('#contentAreaDownloadsView .downloadMainArea .downloadContainer description:nth-of-type(1)').value")
                if downloaded_file_name:
                    break
            except Exception as e:
                print(e)
            time.sleep(1)
            if time.time() > endTime:
                break
    
    # Rename the downloaded file
    file_path = Path(download_directory / downloaded_file_name)
    file_path.rename(file_path.parent / f"{file_name}{file_path.suffix}")


def download_fvalues(download_directory: Path, deprag_ip: str) -> None:
    with Firefox(options=_get_browser_options(download_directory)) as browser:
        browser.get(
            "http://"
            + deprag_ip
            + "/cgi-bin/cgiread?site=-&request=fvalues&args=&mode=-1-"
        )

        downloads = browser.find_elements(By.CLASS_NAME, "download")
        downloads[len(downloads) - 2].click()
