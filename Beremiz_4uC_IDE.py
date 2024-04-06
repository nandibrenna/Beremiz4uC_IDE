#!/usr/bin/env python
# -*- coding: utf-8 -*-

import builtins
import gettext
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
beremiz_folder = os.path.join(dir_path, "beremiz")
sys.path.insert(1, beremiz_folder)
gettext.install("Beremiz_4uC_IDE")

from Beremiz import *


class Beremiz4uCIdeLauncher(BeremizIDELauncher):
    """
    Beremiz4uC IDE Launcher class
    """

    def __init__(self):
        BeremizIDELauncher.__init__(self)

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
        #     (
        #         "B4uC Modbus",
        #         "B4uC Modbus",
        #         "Adds modbus functions for B4uC",
        #         "b4uc_modbus.modbus.RootClass",
        #     )
        # )

# start Beremiz IDE
if __name__ == "__main__":
    beremiz = Beremiz4uCIdeLauncher()
    beremiz.Start()
