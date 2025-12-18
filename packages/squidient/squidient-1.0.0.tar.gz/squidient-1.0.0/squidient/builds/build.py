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

from ..utils.utils import open_critical_json
from ..definitions import build_file
from ..utils.log import *

logger = logging.getLogger(logging_context)

class Build:

    def __init__(self, build_id):

        self._build_id = build_id

        #These variables propagates

        self._pre_modules = []
        self._modules = []
        self._post_modules = []
        self._pre_exec = []
        self._env = []
        self._tags = []
        self._compiler = ""
        self._code_coverage = ""
        self._configuration = ""
        self._exclusive_tests = ""
        self._flex = ""
        self._file = ""
        self._job = ""
        self._platform = ""
        self._lock = ""
        self._runnable = ""
        self._timeout = ""
        self._timeoffset = ""
        self._type = ""
        self._ctest = ""
        self._threads = ""
        self._version = ""
        self._system = ""
        self._cc_tool = ""
        self._sbatch = {}

        #these variables don't propagate
        self._installable = ""
        self._alias = ""

        #Configure build
        self._builds = open_critical_json(build_file)
        self.fill(build_id)

        if self._timeout == "":
            self._timeout = "02:00:00"

        if self._timeoffset == "":
            self._timeoffset = "00:00:00"

        if type(self._ctest) != bool:
            self._ctest = True
        if type(self._exclusive_tests) != bool:
            self._exclusive_tests = False

    def fill(self, build_id):
        build = self._builds[build_id]
        if len(self._modules) == 0 and "modules" in build:
            self._modules = build["modules"]
        if len(self._env) == 0 and "environment" in build:
            self._env = build["environment"]
        if len(self._pre_exec) == 0 and "preExec" in build:
            self._pre_exec = build["preExec"]
        if len(self._pre_modules) == 0 and "preModules" in build:
            self._pre_modules = build["preModules"]
        if len(self._post_modules) == 0 and "postModules" in build:
            self._post_modules = build["postModules"]
        if len(self._tags) == 0 and "tags" in build:
            self._tags = build["tags"]
        if len(self._sbatch) == 0 and "sbatch" in build:
            self._sbatch = build["sbatch"]
        if self._cc_tool == "" and "cc_tool" in build:
            self._cc_tool = build["cc_tool"]
        if self._compiler == "" and "compiler" in build:
            self._compiler = build["compiler"]
        if self._code_coverage == "" and "codeCoverage" in build:
            self._code_coverage = build["codeCoverage"]
        if self._exclusive_tests == "" and "exclusive" in build:
            self._exclusive_tests = build["exclusive"]
        if self._configuration == "" and "configuration" in build:
            self._configuration = build["configuration"]
        if self._file == "" and "file" in build:
            self._file = build["file"]
        if self._flex == "" and "flex" in build:
            self._flex = build["flex"]
        if self._job == "" and "job" in build:
            self._job = build["job"]
        if self._system == "" and "system" in build:
            self._system = build["system"]
        if self._platform == "" and "platform" in build:
            self._platform = build["platform"]
        if self._lock == "" and "lock" in build:
            self._lock = build["lock"]
        if self._runnable == "" and "runnable" in build:
            self._runnable = build["runnable"]
        if self._threads == "" and "threads" in build:
            self._threads = build["threads"]
        if self._type == "" and "type" in build:
            self._type = build["type"]
        if self._ctest == "" and "ctest" in build:
            self._ctest = build["ctest"]
        if self._timeout == "" and "timeout" in build:
            self._timeout = build["timeout"]
        if self._timeoffset == "" and "timeOffset" in build:
            self._timeoffset = build["timeOffset"]
        if self._version == "" and "version" in build:
            self._version = build["version"]
        if self._alias == "":
            if "alias" in build:
                self._alias = build["alias"]
            else:
                self._alias = self._build_id
        if self._installable == "":
            if "installable" in build:
                self._installable = build["installable"]
            else:
                self._installable = False
        if "from" in build:
            self.fill(build["from"])


    def get_tags(self):
        return self._tags

    def get_modules(self):
        return self._modules

    def get_pre_modules(self):
        return self._pre_modules

    def get_post_modules(self):
        return self._post_modules

    def get_pre_exec(self):
        return self._pre_exec

    def get_env(self):
        return self._env

    def get_compiler(self):
        return self._compiler

    def get_runnable(self):
        return self._runnable

    def get_version(self):
        return self._version

    def get_system(self):
        return self._system

    def get_platform(self):
        return self._platform

    def get_build_id(self):
        return self._build_id

    def get_code_coverage(self):
        return self._code_coverage

    def get_exclusive_tests(self):
        return self._exclusive_tests

    def get_cc_tool(self):
        return self._cc_tool

    def get_timeoffset(self):
        return self._timeoffset
