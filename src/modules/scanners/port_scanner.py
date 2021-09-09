"""This module attempts to configure and run a port scanner to detect
services on a given domain host or ip. This is bassically a wrapper
over nmap, but with the ability to save results to a database and further
analize it and process it in the scan pipeline"""

revision = "Missing"

from typing import Any, Callable
import src.handlers.scan_handlers as handlers
import halo

SETTINGS = {
    "handler": {
        "description": "Function to run over each scan result. Defaults to print",
        "value": handlers.print_scan,
        "required": False,
    },
    "hosts": {
        "description": "Hosts ranges to analyze with nmap",
        "value": "localhost",
        "required": False,
    },
    "ports": {
        "description": "Ports ranges to analyze",
        "value": "0-65536",
        "required": False,
    },
    "arguments": {
        "description": "arguments to pass to the underlying nmap system",
        "value": "",
        "required": False,
    },
}

import nmap


def params():
    return SETTINGS


def set(key: str, value: Any):
    try:
        SETTINGS[key]["value"] = value
    except Exception as e:
        print(e)


def run():
    hosts = SETTINGS["hosts"]["value"]
    ports = SETTINGS["ports"]["value"]
    arguments = SETTINGS["arguments"]["value"]
    port_scanner = nmap.PortScannerAsync()
    handler: Callable = SETTINGS["handler"]["value"]

    def callback(host, scan_result):
        print(host)
        print("-" * 30)
        handler(scan_result, SETTINGS, [])

    port_scanner.scan(hosts=hosts, ports=ports, arguments=arguments, callback=callback)

    with halo.Halo("Scanning", spinner="dots"):
        while port_scanner.still_scanning():
            pass
