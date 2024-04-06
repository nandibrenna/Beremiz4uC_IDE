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
import hashlib
import glob
import shutil
from typing import Callable, Optional
from util.ProcessLogger import ProcessLogger

class toolchain_b4arm(object):
    extension: Optional[str] = None
    target: Optional[str] = None
    Generate_plc_main: Callable
    Generate_plc_debugger: Callable

    def __init__(self, CTRInstance):
        self.CTRInstance = CTRInstance
        base_folder = os.path.dirname(os.path.abspath(__file__))
        # Define compiler and linker paths
        self.compiler = 'arm-none-eabi-gcc'
        self.linker = 'arm-none-eabi-gcc'
        # Define script paths
        self.ld_script = os.path.join(base_folder,"__script/code_before_data.ld")
        self.mkmodule = os.path.join(base_folder,"__script/mkmodule")
        self.rensym = os.path.join(base_folder,"__script/rename_obj")
        self.matiec_inc_path = os.path.join(base_folder,"__script/matiec")

        self.buildpath = None
        self.SetBuildPath(self.CTRInstance._getBuildPath())
        # Set PLC names and paths
        self.plc_name =  self.CTRInstance.GetProjectName()
        self.plc_file =  self.plc_name + ".bin"
        self.plc_path =  os.path.join(self.buildpath, self.plc_file)
        self.elf_file =  self.plc_name + ".elf"
        self.elf_path =  os.path.join(self.buildpath, self.elf_file)
        self.plc_main_code = ""
        self.plc_debug_code = ""
        self.md5key = None

    def log(self, message):
        """Write a log message."""
        self.CTRInstance.logger.write(message+'\n')

    def log_err(self, message):
        """Write an error message."""
        self.CTRInstance.logger.write_error(message+'\n')

    def GetBinaryPath(self):
        """Get the path of the binary file."""
        return self.plc_path

    def _GetMD5FileName(self):
        """Get the filename for the MD5 hash."""
        return os.path.join(self.buildpath, "lastbuildPLC.md5")

    def ResetBinaryMD5(self):
        """Reset the MD5 hash of the binary."""
        try:
            os.remove(self._GetMD5FileName())
        except Exception:
            pass

    def GetBinaryMD5(self):
        """Get the MD5 hash of the binary."""
        if self.md5key is not None:
            return self.md5key
        else:
            try:
                with open(self._GetMD5FileName(), "r", encoding="utf-8") as file:
                    return file.read()
            except Exception:
                return None

    def SetBuildPath(self, buildpath):
        """Set the build path."""
        if self.buildpath != buildpath:
            self.buildpath = buildpath
            self.bin = self.CTRInstance.GetProjectName() + self.extension
            self.bin_path = os.path.join(self.buildpath, self.bin)
            self.md5key = None
            self.srcmd5 = {}

    def build(self):
        """Compile and link the project to generate the binary file."""
        # Compiler and linker flags defined for building
        Builder_CFLAGS = '-c -g0 -O3 -fPIE -msingle-pic-base -mpic-register=r9 -fomit-frame-pointer -mno-pic-data-is-text-relative -mlong-calls -mthumb -mpoke-function-name'
        ALLldflags = f'-gdwarf-4 -nostartfiles -nodefaultlibs -nostdlib -Wl,--unresolved-symbols=ignore-in-object-files -Wl,--emit-relocs -Wl,-e,0 -T{self.ld_script}'
        IncFlags = f'-I {self.matiec_inc_path} -Wno-unused-function'

        # generate PLC C Code
        self.Generate_plc_main()
        self.Generate_plc_debugger()

        source_path = os.path.join("b4uc_targets", self.target, "beremiz.h")
        destination_path = os.path.join(self.buildpath, "beremiz.h")
        try:
            shutil.copyfile(source_path, destination_path)
        except IOError as e:
            self.log_err(f"Error copying 'beremiz.h': {e}")
            return False

        obj_names = []
        obj_files = []
        relink = not os.path.exists(self.plc_path)

        for Location, CFilesAndCFLAGS, _DoCalls in self.CTRInstance.LocationCFilesAndCFLAGS:
            # dont compile code for Locations
            if not Location and CFilesAndCFLAGS:
                if Location=="":
                    location_name = "main code"
                if Location=="()":
                    location_name = "plc code"

                self.log(f"\nCompiling PLCcode for: {Location}")

                for CFile, CFlags in CFilesAndCFLAGS:
                    if CFile.endswith(".c"):
                        c_file = os.path.basename(CFile)
                        obj_name = f"{os.path.splitext(c_file)[0]}.o"
                        obj_file = f"{os.path.splitext(CFile)[0]}.o"
                        relink = True
                        self.log(f"   [CC]  {c_file} -> {obj_name}")

                        status, _, _ = ProcessLogger(
                            self.CTRInstance.logger,
                            f"{self.compiler} {IncFlags} {CFile} -o {obj_file} {Builder_CFLAGS}"
                        ).spin()
                        if status:
                            self.log_err(f"C compilation of {c_file} failed.")
                            return False

                        status, _, _ = ProcessLogger(
                            None,
                            f"{self.rensym} {obj_file}"
                        ).spin()
                        if status:
                            self.log_err(f"Symbol rename of {c_file} failed.")
                            return False

                        obj_names.append(obj_name)
                        obj_files.append(obj_file)

        if relink:
            listobjstring = ' '.join(obj_files)
            self.log(f"\nLinking:   [LD]  {' '.join(obj_names)} -> {self.elf_file}")
            status, _, _ = ProcessLogger(
                self.CTRInstance.logger,
                f"{self.linker} {ALLldflags} {listobjstring} -o {self.elf_path}"
            ).spin()
            if status:
                self.log_err(f"Linking of {self.elf_file} failed.")
                return False

            self.log("\nGenerating PLC File:")
            self.log(f"   [UD]  {self.elf_file} -> {self.plc_file}")
            status, _, _ = ProcessLogger(
                self.CTRInstance.logger,
                f"{self.mkmodule} --no-debug --bin-name {self.plc_path} {self.elf_path}"
            ).spin()
            if status:
                return False
            else:
                self.log(f"Output file: {self.plc_file}")

        else:
            self.log(f"   [pass]  {' '.join(obj_names)} -> {self.bin}")

        for file_type in ('*.o', '*.elf'):
            for file_path in glob.glob(os.path.join(self.buildpath, file_type)):
                try:
                    os.remove(file_path)
                except Exception as _e:
                    pass

        self.md5key = hashlib.md5(open(self.plc_path, "rb").read()).hexdigest()
        self.log(f"\nCalculated MD5 for {self.plc_file} is {self.md5key}")
        md5_filename = self._GetMD5FileName()
        with open(md5_filename, "w") as f:
            f.write(self.md5key)
        self.log(f"MD5 written to {md5_filename}")

        return True