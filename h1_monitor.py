import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime

import requests


@dataclass
class HLServiceMonitor:
    name: str
    address: str
    method: str

    def check(self):
        if self.method == "PING":
            return self.check_ping()
        return self.check_https()

    def check_https(self):
        try:
            url = requests.utils.requote_uri(self.address)
            start = time.perf_counter()

            response = requests.head(
                url, timeout=5, allow_redirects=True
            )

            if response.status_code in (405, 501):
                response = requests.get(
                    url, timeout=5, allow_redirects=True,
                    stream=True
                )

            elapsed = round((time.perf_counter() - start) * 1000)
            online = response.status_code < 500
            response.close()

            return hl_create_result(
                self.name, online, elapsed,
                f"HTTP {response.status_code}"
            )
        except requests.RequestException as error:
            return hl_create_result(
                self.name, False, None, str(error)
            )

    def check_ping(self):
        try:
            parameter = "-n" if os.name == "nt" else "-c"
            start = time.perf_counter()

            result = subprocess.run(
                ["ping", parameter, "1", self.address],
                capture_output=True,
                timeout=5
            )

            elapsed = round((time.perf_counter() - start) * 1000)

            return hl_create_result(
                self.name,
                result.returncode == 0,
                elapsed if result.returncode == 0 else None,
                "Ping sikeres" if result.returncode == 0
                else "Nincs válasz"
            )
        except (subprocess.SubprocessError, OSError) as error:
            return hl_create_result(
                self.name, False, None, str(error)
            )


def hl_create_result(name, online, response_time, message):
    return {
        "name": name,
        "online": online,
        "response_time": response_time,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
