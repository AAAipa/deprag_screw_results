from functools import lru_cache
from pathlib import Path
from datetime import datetime
import requests
from html.parser import HTMLParser
from typing import List, Tuple, Union


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


class _DepragCurveDataGetter(HTMLParser):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.current_curve_specs: Union[List[str], None] = None
        self.curve_specs: List[Tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrib = {attrib: value for attrib, value in attrs}
        if attrib.get("class", "") != "download":
            return
        assert (
            self.current_curve_specs is None
        ), f"Abandoned curve specs: {self.current_curve_specs}"
        self.current_curve_specs = [attrib["href"]]

    def handle_endtag(self, tag):
        if tag != "a":
            return
        if self.current_curve_specs is not None:
            self.curve_specs = self.curve_specs + [self.current_curve_specs]
            self.current_curve_specs = None

    def handle_data(self, data):
        if self.current_curve_specs is not None:
            self.current_curve_specs = self.current_curve_specs + [data]


def _get_timestamp(graph_name: str) -> datetime:
    graph_name_elements = graph_name.split("_")
    if len(graph_name_elements) == 1:
        return datetime.now()
    _, date, time = graph_name_elements
    year, month, day = date.split("-")
    hour, minute, second = time.split(":")
    return datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second),
    )


def _get_filename(graph_link: str) -> str:
    elements = graph_link.split("'")
    assert len(elements) == 3, str(elements)
    return elements[1]


def current_curves(deprag_ip: str):
    url = f"http://{deprag_ip}/cgi-bin/cgiread"
    data = {
        "site": "-",
        "request": "curves",
        "args": "",
        "mode": "2-",
    }
    response = requests.post(url, data=data)

    parser = _DepragCurveDataGetter()
    parser.feed(response.text)

    curves = [
        (_get_timestamp(graph_name), _get_filename(graph_link))
        for graph_link, graph_name in parser.curve_specs
    ]

    return curves


def download_curves(
    download_directory: Path,
    file_name: str,
    deprag_ip: str,
    target: int,
    wait_time: int = 60,
) -> None:
    curves = current_curves(deprag_ip=deprag_ip)
    _, dlfile = curves[target]

    url = f"http://{deprag_ip}/cgi-bin/cgiread"
    data = {
        "site": "curves",
        "dltype": "csv",
        "dlfile": dlfile,
        "action": "download",
    }
    response = requests.post(url, data=data, stream=True)

    with open(download_directory / f'{file_name}.{data["dltype"]}', "w") as file_stream:
        for line in response.iter_lines(decode_unicode=True):
            file_stream.write(line)
            file_stream.write("\n")


def download_fvalues(download_directory: Path, deprag_ip: str) -> None:
    with Firefox(options=_get_browser_options(download_directory)) as browser:
        browser.get(
            "http://"
            + deprag_ip
            + "/cgi-bin/cgiread?site=-&request=fvalues&args=&mode=-1-"
        )

        downloads = browser.find_elements(By.CLASS_NAME, "download")
        downloads[len(downloads) - 2].click()
