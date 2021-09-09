"""This module attempt to configure and run a port scanner to detect
services on a given domain host or ip. This is bassically a wrapper
over nmap, but with the ability to save results to a database and further
analize it and process it in the scan pipeline"""

revision = "Missing"

from typing import Callable
import src.handlers.scan_handlers as handlers

SETTINGS = {
    "handler": {
        "description": "Function to run over each scan result. Defaults to print",
        "value": handlers.print_scan,
    }
}

import nmap


def params():
    return SETTINGS


def scan(host="localhost", port_range="1-65536", arguments=""):
    port_scanner = nmap.PortScannerAsync()
    handler: Callable = SETTINGS["handler"]["value"]

    def callback(host, scan_result):
        print(host)
        print("-" * 30)
        handler(scan_result, SETTINGS, [])

    port_scanner.scan(
        hosts=host, ports=port_range, arguments=arguments, callback=callback
    )
