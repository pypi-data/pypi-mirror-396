#########################################################################
#                                                                       #
#  This file is part of squidient.                                      #
#                                                                       #
#  squidient is free software: you can redistribute it and/or modify    #
#  it under the terms of the GNU General Public License as published by #
#  the Free Software Foundation, either version 3 of the License, or    #
#  (at your option) any later version.                                  #
#                                                                       #
#  squidient is distributed in the hope that it will be useful,         #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of       #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        # 
#  GNU General Public License for more details.                         #
#                                                                       #
#  You should have received a copy of the GNU General Public License    #
#  along with squidient. If not, see <https://www.gnu.org/licenses/>.   #
#                                                                       #
#########################################################################



# -*- coding: utf-8 -*-

from ..utils.utils import *
from ..definitions import *

logger = logging.getLogger(logging_context)

class ConfigGenerator:

    def __init__(self, file, name):
        self._name = name
        self._file = file
        self._configuration = {}
        self._modules = []
        self._precompilation = []
        self._special = ""
        self.fill(self._file, self._name)

    def fill(self, file, name):
        data = open_critical_json(alya_config_dir+"/"+file)
        configuration = data[name]
        if len(self._modules) == 0 and "modules" in configuration:
            self._modules = configuration["modules"]
        if len(self._precompilation) == 0 and "precompilation" in configuration:
            self._precompilation = configuration["precompilation"]
        if self._special == "" and "special" in configuration:
            self._special = configuration["special"]
            self._precompilation = configuration["precompilation"]
        if "configuration" in configuration:
            for i in configuration["configuration"]:
                if i not in self._configuration:
                    self._configuration[i] = configuration["configuration"][i]
        if "from" in configuration:
            f = file
            if "file" in configuration:
                f = configuration["file"]
            self.fill(f, configuration["from"])

    def write(self, path, cc_path=".", root_path="."):
        c = self._configuration
        config = open(path+"/config.in", 'w')
        var_prefix = ""
        if "var_prefix" in c:
            var_prefix = c["var_prefix"]
        if "pre" in c:
            config.write(c["pre"]+"\n")
        config.write("EXTRALIB = \n")
        config.write("EXTRAINC = \n")
        config.write("CSALYA = \n")
        if "metis_cc" in c:
            config.write("export METIS_CC = " + c["metis_cc"] + "\n")
        if "metis5_cc" in c:
            config.write("export METIS5_CC = " + c["metis5_cc"] + "\n")
        for var in ["fa2p", "fa2plk"]:
            if var in c:
                config.write(var + " = " + c[var] +"\n")
        if "extralib" in c:
            config.write("EXTRALIB := $(EXTRALIB) " + c["extralib"] + "\n")
        if "extrainc" in c:
            config.write("EXTRAINC := $(EXTRAINC) " + c["extrainc"] + "\n")
        if "f77" in c:
            config.write("F77 = " + c["f77"] + "\n")
        if "f90" in c:
            config.write("F90 = " + c["f90"] + "\n")
        if "cc" in c:
            config.write("FCOCC = " + c["cc"] + "\n")
        if "fpp" in c:
            config.write("FPPFLAGS = " + c["fpp"] + "\n")
        if "objects" in c:
            config.write("FCFLAGS = " + c["objects"] + "\n")
        if "optimization" in c:
            config.write("FOPT = " + c["optimization"] + "\n")
        if "debug" in c:
            config.write("CSALYA := $(CSALYA) "+c["debug"]+"\n")
        if "std" in c:
            config.write("CSALYA := $(CSALYA) "+c["std"]+"\n")
        if "openmp" in c:
            config.write("CSALYA := $(CSALYA) "+c["openmp"]+"\n")
            config.write("EXTRALIB := $(EXTRALIB) "+c["openmp"]+"\n")
        if "mpi" in c:
            if not c["mpi"]:
                config.write("CSALYA := $(CSALYA) " + var_prefix + "-DMPI_OFF\n")
        if "integer" in c:
            if c["integer"] == 8:
                config.write("CSALYA := $(CSALYA) " + var_prefix + "-DI8 -m64\n")
        if "ndimepar" in c:
            if c["ndimepar"]:
                config.write("CSALYA := $(CSALYA) " + var_prefix + "-DNDIMEPAR\n")
        if "vector" in c:
            if c["vector"] != 0:
                c["vector"] = str(c["vector"])
                config.write("CSALYA := $(CSALYA) -DVECTOR_SIZE=" + c["vector"] + "\n")
        if "machine_opt" in c:
            config.write("CSALYA := $(CSALYA) "+c["machine_opt"]+"\n")
        if "ipo" in c:
            if c["ipo"]:
                config.write("CSALYA := $(CSALYA) -ipo\n")
        if "metis" in c:
            if "4" in c["metis"]:
                config.write("CSALYA := $(CSALYA) " + var_prefix + "-DMETIS\n")
            elif "5.1" in c["metis"]:
                config.write("CSALYA := $(CSALYA) " + var_prefix + "-DV51METIS\n")
            elif "5" in c["metis"]:
                config.write("CSALYA := $(CSALYA) " + var_prefix + "-DV5METIS\n")
        if "libmetis" in c:
            config.write("EXTRALIB := $(EXTRALIB) "+c["libmetis"]+"\n")
        if "cantera" in c:
            if c["cantera"]:
                config.write("CANTERA = 1" + "\n")
        if "root_boost" in c:
            config.write("ROOT_BOOST = " + c["root_boost"] + "\n")
        if "root_cantera" in c:
            config.write("ROOT_CANTERA = " + c["root_cantera"] + "\n")
        if "codeCoverage" in c:
            if c["codeCoverage"]:
                config.write("CSALYA := $(CSALYA) -prof-gen=srcpos -prof-dir " + cc_path + " -prof-src-root=" + root_path + "\n")
        if "custom" in c:
            for var in c["custom"]:
                config.write(var + " = " + c["custom"][var] +"\n")
        if "post" in c:
            config.write(c["post"]+"\n")
        config.write("FCFLAGS  := $(FCFLAGS) $(CSALYA) $(EXTRAINC)")

    def get_modules(self):
        return self._modules

    def get_precompilation(self):
        return self._precompilation

    def get_special(self):
        return self._special

