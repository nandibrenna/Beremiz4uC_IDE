#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************************
#  Project Name: Beremiz 4 uC                                               		#
#  Author(s): nandibrenna                                                   		#
#  Created: 2024-03-15                                                      		#
#  =================================================================================#
#  Copyright © 2024 nandibrenna                                             		#
#                                                                           		#
# This file is part of Beremiz, a Integrated Development Environment for			#
# programming IEC 61131-3 automates supporting plcopen standard and CanFestival.	#
#																					#
# Copyright (C) 2007: Edouard TISSERANT and Laurent BESSARD							#
# Copyright (C) 2017: Paul Beltyukov												#
#																					#
# See COPYING file for copyrights details.											#
#																					#
# This program is free software; you can redistribute it and/or						#
# modify it under the terms of the GNU General Public License						#
# as published by the Free Software Foundation; either version 2					#
# of the License, or (at your option) any later version.							#
#																					#
# This program is distributed in the hope that it will be useful,					#
# but WITHOUT ANY WARRANTY; without even the implied warranty of					#
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the						#
# GNU General Public License for more details.										#
#																					#
# You should have received a copy of the GNU General Public License					#
# along with this program; if not, write to the Free Software						#
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.	#
#***********************************************************************************/

import os
from ..toolchain_b4arm import toolchain_b4arm

class PLCF407VE_target(toolchain_b4arm):
    extension = ".bin"
    target = "PLCF407VE"

    def Generate_plc_main(self):
        locstrs = ["_".join(map(str, x)) for x in [loc for loc, _Cfiles, DoCalls in
                    self.CTRInstance.LocationCFilesAndCFLAGS if loc and DoCalls]]

        disable_extensions = self.CTRInstance.BeremizRoot.getDisable_Extensions()

        template_path = os.path.join("b4uc_targets", self.target, f"{self.target}_main.c")

        if not os.path.exists(template_path):
            self.log_err(f"Template-Datei {template_path} nicht gefunden.")
            return

        with open(template_path, "r", encoding="utf-8") as template_file:
            template_content = template_file.read()

        if not disable_extensions:
            plc_main_code = template_content % {
                "calls_prototypes": "\n".join([
                    f"int __init_{locstr}(int argc,char **argv);\n" +
                    f"void __cleanup_{locstr}(void);\n" +
                    f"void __retrieve_{locstr}(void);\n" +
                    f"void __publish_{locstr}(void);" for locstr in locstrs]),
                		"retrieve_calls": "\n    ".join([
                    	"__retrieve_%s();" % locstr for locstr in locstrs]),
                		"publish_calls": "\n    ".join([
                    	"__publish_%s();" % locstrs[i - 1] for i in range(len(locstrs), 0, -1)]),
                		"init_calls": "\n    ".join([
                    	"init_level=%d; if((res = __init_%s(argc,argv))) { return res; }" % (i + 1, locstr)
                    for i, locstr in enumerate(locstrs)]),
                		"cleanup_calls": "\n    ".join([
                    	"if(init_level >= %d) __cleanup_%s();" % (i, locstrs[i - 1])
                    for i in range(len(locstrs), 0, -1)])
            }
        else:
            plc_main_code = template_content % {
                "calls_prototypes": "\n",
                "retrieve_calls": "\n",
                "publish_calls": "\n",
                "init_calls": "\n",
                "cleanup_calls": "\n"
            }

        target_file_path = os.path.join(self.buildpath, "plc_main.c")
        with open(target_file_path, "w", encoding="utf-8") as target_file:
            target_file.write(plc_main_code)
        self.plc_main_code = plc_main_code

    def Generate_plc_debugger(self):
        """
        Generates plc_debug.c using templates from the specified target directory.
        """
        # Ensure GetIECProgramsAndVariables is called
        if not self.CTRInstance.GetIECProgramsAndVariables():
            self.log_err("Error retrieving IEC programs and variables")
            return

        ProgramList = self.CTRInstance._ProgramList
        VariablesList = self.CTRInstance._VariablesList
        DbgVariablesList = self.CTRInstance._DbgVariablesList

        # Paths to the template files
        debug_template_path = os.path.join("b4uc_targets", self.target, f"{self.target}_debug.c")
        var_access_path = os.path.join("b4uc_targets", self.target, "var_access.c")

        # Prepare the debug code
        variable_decl_array = []
        retain_indexes = []

        for i, v in enumerate(DbgVariablesList):
            variable_decl_array.append(
                "{&(%(C_path)s), " % v +
                {
                    "EXT": "%(type)s_P_ENUM",
                    "IN":  "%(type)s_P_ENUM",
                    "MEM": "%(type)s_O_ENUM",
                    "OUT": "%(type)s_O_ENUM",
                    "VAR": "%(type)s_ENUM"
                }[v["vartype"]] % v +
                "}")

            if v["retain"] == "1":
                retain_indexes.append(f"/* {v['C_path']} */ {i}")

        ptr_assignment_lines = [f"\tptr[{i}] = dbgvardsc[{i}].ptr;" for i in range(len(variable_decl_array))]

        # Read the debug template
        try:
            with open(debug_template_path, "r", encoding="utf-8") as template_file:
                debug_template_content = template_file.read()
        except IOError:
            self.log_err(f"Cannot read debug template file {debug_template_path}.")
            return

        # Load the variable access code
        try:
            with open(var_access_path, "r", encoding="utf-8") as var_access_file:
                var_access_code = var_access_file.read()
        except IOError:
            self.log_err(f"Cannot read Var-Access file {var_access_path}.")
            return

        debug_code = debug_template_content % {
            "programs_declarations": "\n".join([f"extern {p['type']} {p['C_path']};" for p in ProgramList]),
            "extern_variables_declarations": "\n".join([
                {
                    "EXT": "extern __IEC_%(type)s_p %(C_path)s;",
                    "IN":  "extern __IEC_%(type)s_p %(C_path)s;",
                    "MEM": "extern __IEC_%(type)s_p %(C_path)s;",
                    "OUT": "extern __IEC_%(type)s_p %(C_path)s;",
                    "VAR": "extern __IEC_%(type)s_t %(C_path)s;",
                    "FB":  "extern       %(type)s   %(C_path)s;"
                }[v["vartype"]] % v
                for v in VariablesList if '.' not in v["C_path"]]),
            "variable_decl_array": ",\n".join(variable_decl_array),
            "retain_vardsc_index_array": ",\n".join(retain_indexes),
            "var_access_code": var_access_code,
            "dbg_ptr_cnt": "\n".join(ptr_assignment_lines)
        }

        # Write to the target file: plc_debug.c in the build directory
        target_file_path = os.path.join(self.buildpath, "plc_debugger.c")
        try:
            with open(target_file_path, "w", encoding="utf-8") as target_file:
                target_file.write(debug_code)
        except IOError:
            self.log_err(f"Cannot write target file {target_file_path}.")

        self.plc_debug_code = debug_code
