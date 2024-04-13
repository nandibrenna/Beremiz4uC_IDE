#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gettext
import os
import sys
from importlib import import_module

dir_path = os.path.dirname(os.path.realpath(__file__))
beremiz_folder = os.path.join(dir_path, "beremiz")
image_folder = os.path.join(dir_path, "b4uc_images")
sys.path.insert(1, beremiz_folder)
gettext.install("Beremiz_4uC_IDE")

from util.BitmapLibrary import AddBitmapFolder
import logging

class CustomImporter:
    def find_module(self, fullname, path=None):
        if fullname == "graphics.FBD_Objects":
            return self
        if fullname == "controls.CustomToolTip":
            return self
        return None

    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]
        if name == "graphics.FBD_Objects":
            module = import_module("FBD_Objects_b4uc")
            sys.modules[name] = module
            return module
        if name == "controls.CustomToolTip":
            module = import_module("CustomToolTip_b4uc")
            sys.modules[name] = module
            return module
        raise ImportError("Cannot find module")

sys.meta_path.insert(0, CustomImporter())

from Beremiz import *

logging.basicConfig(level=logging.ERROR)


class Beremiz4uCIdeLauncher(BeremizIDELauncher):
    """
    Beremiz4uC IDE Launcher class
    """

    def __init__(self):
        BeremizIDELauncher.__init__(self)

        AddBitmapFolder(image_folder)
        import features

        # import connectors
        import b4uc_connector
        import connectors

        # update connectors
        connectors.connectors.update(b4uc_connector.connectors)

        # import targets and toolchains
        import b4uc_targets
        import targets

        # update targets and toolchains
        targets.toolchains.update(b4uc_targets.toolchains)
        targets.targets.update(b4uc_targets.targets)

        features.libraries = [("Native", "NativeLib.NativeLibrary", True)]

        # features
        # features.catalog.append(
        # (
        # 	"B4uC config",
        # 	"B4uC config",
        # 	"PLC configuration for B4uC",
        # 	"b4uc_hardware.b4uc_hw_config.Root",
        # ))

        # features.catalog.append(
        #     (
        #         "B4uC Modbus",
        #         "B4uC Modbus",
        #         "Modbus functions for B4uC",
        #         "b4uc_modbus.modbus.RootClass",
        #     )
        # )

# start Beremiz IDE
if __name__ == "__main__":
    beremiz = Beremiz4uCIdeLauncher()
    beremiz.Start()
