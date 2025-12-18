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
boolean = {True: "ON", False: "OFF"}


class CMakeOptions:

    def __init__(self, file, name):
        self._name = name
        self._file = file
        self._options = ""
        self._configuration = {}
        self._modules = []
        self.fill(self._file, self._name)

    def fill(self, file, name):
        data = open_critical_json(alya_config_dir+"/"+file)
        configuration = data[name]
        if "modules" in configuration:
            self._modules = configuration["modules"]
        if "configuration" in configuration:
            for i in configuration["configuration"]:
                if i not in self._configuration:
                    self._configuration[i] = configuration["configuration"][i]
        if "from" in configuration:
            f = file
            if "file" in configuration:
                f = configuration["file"]
            self.fill(f, configuration["from"])

    def options(self, install_path, cc_path=".", root_path=".", mpirun_flags=[]):
        replacements = {"%%CC_PATH%%": cc_path, "%%ALYA_SRC_PATH%%": root_path}
        mpiexec_preflags_found = False
        for configuration in self._configuration:
            if type(self._configuration[configuration]) == str:
                if self._configuration[configuration] == "":
                    continue
            self._options += "-D" + configuration + "="
            if type(self._configuration[configuration]) == bool:
                self._options += boolean[self._configuration[configuration]] + " "
            elif type(self._configuration[configuration]) == int:
                self._options += str(self._configuration[configuration]) + " "
            elif type(self._configuration[configuration]) == str:
                if configuration == "MPIEXEC_PREFIX":
                    mpiexec_preflags_found = True
                    mpiexec_preflags = self._configuration[configuration].replace("\"","")
                    for mpirun_flag in mpirun_flags:
                        mpiexec_preflags += " " + mpirun_flag
                    mpiexec_preflags = mpiexec_preflags.replace(" ", ";")
                    self._options += "\"" + self.replace_patterns(mpiexec_preflags, replacements) + "\"" + " "
                else:
                    self._options += self.replace_patterns(self._configuration[configuration], replacements) + " "
        if not mpiexec_preflags_found:
            mpiexec_preflags = ""
            for mpirun_flag in mpirun_flags:
                mpiexec_preflags += mpirun_flag + " "
            mpiexec_preflags = mpiexec_preflags.replace(" ", ";")
            if mpiexec_preflags:
                self._options += "-DMPIEXEC_PREFLAGS=" + "\"" + mpiexec_preflags[:-1] + "\"" + " "
        for module in self._modules:
            self._options += "-DWITH_MODULE_" + module.upper() + "=" + boolean[True] + " "
        self._options += "-DCMAKE_INSTALL_PREFIX=" + install_path + " "

    def get_modules(self):
        return self._modules

    def get_options(self):
        return self._options

    def replace_patterns(self, string, replacements):
        for pattern in replacements:
            string = string.replace(pattern, replacements[pattern])
        return string

    def get_configuration(self):
        return self._configuration

