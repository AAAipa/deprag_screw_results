import requests

url = "http://172.10.25.100/cgi-bin/cgiread"
data = {
    "site": "-",
    "request": "curves",
    "args": "", 
    "mode": "2-",
}

response = requests.post(url, data=data)

from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    current_curve_specs = None
    curve_specs = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrib = {attrib: value for attrib, value in attrs}
        if attrib.get("class", "") != "download":
            return
        assert self.current_curve_specs is None, f"Abandoned curve specs: {self.current_curve_specs}"
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


parser = MyHTMLParser()
parser.feed(response.text)

from datetime import datetime


def get_timestamp(graph_name: str) -> datetime:
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


def get_filename(graph_link: str) -> str:
    elements = graph_link.split("'")
    assert len(elements) == 3, str(elements)
    return elements[1]


curves = [(get_timestamp(graph_name), get_filename(graph_link)) for graph_link, graph_name in parser.curve_specs]


for timestamp, filename in curves:
    print(timestamp, ":", filename)

exit()

data = {
    "site": "curves",
    "dltype": "csv",
    "dlfile": "/deprag/curvedata/007_graph.bin", 
    "action": "download",
}

response = requests.post(url, data=data, stream=True)

print("Took", response.elapsed, "seconds", flush=True)

from pathlib import Path

with open(Path.home() / "Downloads" / "test_download.csv", "w") as file_stream:
    for line in response.iter_lines(decode_unicode=True):
        file_stream.write(line)
        file_stream.write("\n")
