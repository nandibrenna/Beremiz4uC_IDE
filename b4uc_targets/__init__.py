#!/usr/bin/env python
# -*- coding: utf-8 -*-

#****************************************************************************
#  Project Name: Beremiz 4 uC                                               #
#  Author(s): nandibrenna                                                   #
#  Created: 2024-03-15                                                      #
#  ======================================================================== #
#  Copyright © 2024 nandibrenna                                             #
#                                                                           #
#  Licensed under the Apache License, Version 2.0 (the "License");          #
#  you may not use this file except in compliance with the License.         #
#  You may obtain a copy of the License at                                  #
#                                                                           #
#      http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                           #
#  Unless required by applicable law or agreed to in writing, software      #
#  distributed under the License is distributed on an "AS IS" BASIS,        #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or          #
#  implied. See the License for the specific language governing             #
#  permissions and limitations under the License.                           #
#                                                                           #
#***************************************************************************/

import importlib
from os import listdir, path
import util.paths as paths


'''				### 	Target Directory Structure with Toolchain Configurations	###
...
│
├─  targets/													# main targets directory containing all predefined target directories
│	│
│	...
│
├─	b4uc_targets/												# base directory containing all b4uc target directories
│	│
│	├── __init__.py												# b4uc target integration into main targets
│	│
│	├── XSD_toolchain_b4arm										# XSD file for toolchain_b4arm configurations
│	├── toolchain_b4arm.py										# Python file for toolchain_b4arm logic
│	│
│	├── __script												# script directory
│	│   ├── code_before_data.ld									# module linker file
│	│   ├── mkmodule											# module generation script
│	│	├── rename_obj											# script to rename symbols in object files
│	│	└── matiec/												# matiec include files
│	│		├── accessor.h
│	│		├── iec_std_FB_no_ENENO.h
│	│		├── iec_std_FB.h
│	│		├── iec_std_functions.h
│	│		├── iec_std_lib.h
│	│		├── iec_types_all.h
│	│   	└── iec_types.h
│	│
│	├── PLCF407VE/												# specific PLCF407VE directory
│	│   ├── XSD 												# XSD file for target PLCF407VE
│	│   ├── PLCF407VE_main.c									# main c template file for target PLCF407VE
│	│	├── var_access.c										# Variable access C file (switch to if changed)
│	│	├── PLCF407VE__debug.c									# debugger code template
│	│	├── beremiz.h											# Header file for extensions
│	│   └── (other .c files starting with "PLCF407VE_main")		# other C files for target PLCF407VE
│	│
│	├── target2/												# specific target2 directory
│	│   ├── XSD 												# XSD file for target2
│	│   ├── target2_main.c										# main c template file for target2
│	│	├── var_access.c										# Variable access C file (switch to if changed)
│	│	├── target2__debug.c									# debugger code template
│	│	├── beremiz.h											# Header file for extensions
│	│   └── (other .c files starting with "target2_main")		# other C files for target target2
│	│
│	└── __temp/													# a directory starting with __, which is ignored
...

'''


_base_path = paths.AbsDir(__file__)

def _GetLocalTargetClassFactory(name):
    return lambda: getattr(importlib.import_module(f"b4uc_targets.{name}"), f"{name}_target")

targets = dict(
    [
        (
            name,
            {
                "xsd":      path.join(_base_path, name, "XSD"),
                "class":    _GetLocalTargetClassFactory(name),
                "code":     {
                            fname: path.join(_base_path, name, fname)
                            for fname in listdir(path.join(_base_path, name))
                            if fname.startswith(f"{name}_main") and fname.endswith(".c")
                },
            },
        )
        for name in listdir(_base_path)
        if path.isdir(path.join(_base_path, name)) and not name.startswith("__")
    ]
)

toolchains = {"b4arm": path.join(_base_path, "XSD_toolchain_b4arm")}
