#!/usr/bin/env python

from os import listdir, path
import importlib
from connectors.ConnectorBase import ConnectorBase
_base_path = path.split(__file__)[0]

# We are using the ERPC Connector from Beremiz. However, an adaptation was necessary
# to accommodate the PLC's current data reception limitations.
connectors_packages = ["ERPC"]

# Reduced chunk size from 0xFFF (4K) to 0x200 (512B)
ConnectorBase.chuncksize = 0x200

def _GetLocalConnectorClassFactory(name):
    return lambda: getattr(importlib.import_module(f"connectors.{name}"),f"{name}_connector_factory")

connectors = {name: _GetLocalConnectorClassFactory(name) for name in connectors_packages}
