from pathlib import Path
from time import time

import rospy
import requests as requester

from deprag_downloader.download_directory import (
    get_download_directory as _get_download_directory,
)
from deprag_downloader.browser_interaction import (
    download_curves as _download_curves,
    download_fvalues as _download_fvalues,
)
from deprag_msgs.msg import screwing
from deprag_msgs.srv import download_requestRequest, download_requestResponse


def _find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


class DepragDownloader:
    def __init__(
        self, download_directory: Path, deprag_ip: str, curve_publisher: rospy.Publisher
    ) -> None:
        self.download_directory = download_directory
        self.deprag_ip = deprag_ip
        self.publisher = curve_publisher

    def __call__(self, data: download_requestRequest) -> download_requestResponse:
        pub = data.iTarget < 0
        data.iTarget = 1 if pub else data.iTarget
        download_directory = _get_download_directory(
            None if pub else self.download_directory
        )
        _download_curves(download_directory, self.deprag_ip, data.iTarget)

        if pub:
            self._publish(download_directory)
        
        return download_requestResponse()

    def _publish(self, download_directory: Path) -> None:

        curve_file = next(download_directory.iterdir())

        rospy.logdebug(f'Publishing curve "{curve_file.stem}"...')

        sub_dir = (
            download_directory / "sub"
        )  # sub directory to determine what program was used
        sub_dir.mkdir(exist_ok=True)

        _download_fvalues(sub_dir, self.deprag_ip)

        with open(sub_dir / "actual.csv", "r") as info:
            _info = info.read()
        _info = _info[20:]
        c = _info.find(",")
        _info = _info[:c]

        _prgrmNumber = int(_info)

        rospy.logdebug(f'Focusing on program no. "{_prgrmNumber}"...')

        # get programm info
        _str = (
            "http://"
            + self.deprag_ip
            + "/cgi-bin/cgiread?site=getprg&program="
            + str(_prgrmNumber)
        )
        r = requester.get(_str)
        prgmInfo = r.text

        rospy.logdebug("Got program info: " + prgmInfo)

        msg = screwing()
        msg.prgrmInfo = prgmInfo

        curve_file = curve_file.rename(download_directory / "data.txt")  # type: ignore[func-returns-value]

        with open(curve_file, "r") as _csv:
            _csv_str = _csv.read()
        c = _csv_str.find("Temperatur") + 15
        _csv_str = _csv_str[c:]
        msg.csv = _csv_str

        self.publisher.publish(msg)

        filepath = self.download_directory / f"{time()}.json"

        with open(filepath, "w") as _f:
            jsonInfo = prgmInfo.replace("\n", ',\n"')
            jsonInfo = jsonInfo.replace("=", '":')
            jsonInfo = '"' + jsonInfo
            c = _find_nth(jsonInfo, ":", 2) + 1
            jsonInfo = jsonInfo[:c] + '"' + jsonInfo[c:]
            c = _find_nth(jsonInfo, ",", 2)
            jsonInfo = jsonInfo[:c] + '"' + jsonInfo[c:]
            _f.write("{ \n")
            _f.write(jsonInfo)

            zeit = "["
            Dmess1 = "["
            Wmess1 = "["
            Dmotor = "["
            Wmotor = "["
            DZ = "["
            Schritt = "["
            Strom = "["
            Temp = "["
            lines = _csv_str.count("\n") + 1  # anzahl Zeilen
            for i in range(0, lines):
                # Zeit
                c = _csv_str.find(",")
                zeit = zeit + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]
                # Mess1 Dreh
                c = _csv_str.find(",")
                Dmess1 = Dmess1 + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]
                # W mess1
                c = _csv_str.find(",")
                Wmess1 = Wmess1 + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]
                # D motor
                c = _csv_str.find(",")
                Dmotor = Dmotor + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]
                # W Motor
                c = _csv_str.find(",")
                Wmotor = Wmotor + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]
                # Drehzahl
                c = _csv_str.find(",")
                DZ = DZ + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]
                # Schritt
                c = _csv_str.find(",")
                Schritt = Schritt + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]
                # Strom
                c = _csv_str.find(",")
                Strom = Strom + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]
                # temp
                c = _csv_str.find("\n")
                Temp = Temp + _csv_str[:c] + ","
                _csv_str = _csv_str[c + 1 :]

            zeit = zeit.replace("\n", "")

            zeit = zeit[: (len(zeit) - 2)] + "],"
            Dmess1 = Dmess1[: (len(zeit) - 2)] + "],"
            Wmess1 = Wmess1[: (len(zeit) - 2)] + "],"
            Dmotor = Dmotor[: (len(zeit) - 2)] + "],"
            Wmotor = Wmotor[: (len(zeit) - 2)] + "],"
            DZ = DZ[: (len(zeit) - 2)] + "],"
            Schritt = Schritt[: (len(zeit) - 2)] + "],"
            Strom = Strom[: (len(zeit) - 2)] + "],"
            Temp = Temp[: (len(zeit) - 2)] + "]"

            _f.write('csv" : { \n')
            t = '   "Zeit(0.001 ms)":' + zeit
            t.replace("\n", "")
            _f.write(t + "\n")
            _f.write('  "Drehmoment Messsystem 1 (Nm)":' + Dmess1 + "\n")
            _f.write('  "Winkel Messsystem 1":' + Wmess1 + "\n")
            _f.write('  "Drehmoment Motor (Nm)":' + Dmotor + "\n")
            _f.write('  "Winkel Motor":' + Wmotor + "\n")
            _f.write('  "Drehzahl (U/min)":' + DZ + "\n")
            _f.write('  "Schritt":' + Schritt + "\n")
            _f.write('  "Stromstaerke (A)":' + Strom + "\n")
            _f.write('  "Temperatur (C)":' + Temp + "\n")

            _f.write("}\n")
            _f.write("  }")

        rospy.logdebug(f'Removing "{str(download_directory)}"...')

        download_directory.unlink()
