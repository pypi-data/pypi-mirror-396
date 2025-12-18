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



from ..utils.utils import *
from ..definitions import *
from ..utils.message import *
from abc import ABC, abstractmethod

logger = logging.getLogger(logging_context)


def clean_cc():
    command("rm -fr " + cc_report_dir)


class CodeCoverage(ABC):

    def __init__(self, systemManager, ssh, config, revision, alya_repository, builds):
        self._systemManager = systemManager
        self._ssh = ssh
        self._config = config
        self._alya_repository = alya_repository
        self._revision = revision
        self._cc_revision = self._config["cc"]["reference"]
        self._system = self._config["cc"]["system"]
        self._platform = self._config["cc"]["platform"]
        self._modules = self._config["cc"]["modules"]
        self._tool = self._config["cc"]["tool"]
        self._build = self._config["cc"]["build"]
        self._server_path = self._systemManager.get_system(self._system).get_path()
        self._summary = ""
        self._covered = ""
        self._uncovered = ""
        self._report = {"tool": self._tool, "files": []}
        self._current_path = os.getcwd()
        self._status = True
        self._builds = builds
        self._spi = ""
        self._total = 0
        self._failed = 0
        self._codecoverage = 0.0
        self._module_cmd = ""

    def get_tool(self):
        return self._tool

    def is_cc_runnable(self):
        for b in self._builds:
            if self._builds[b].get_system() == self._system and self._builds[b].get_platform() == self._platform and self._builds[b].get_cc_tool() == self._tool:
                if self._builds[b].get_code_coverage():
                    if self._builds[b].check_build_status():
                        return True
        return False

    def alya_path(self):
        alya_path = self._server_path + "/" + alya_dir
        alya_path = alya_path.replace("//", "/")
        return alya_path

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def get_files(self):
        pass

    @abstractmethod
    def postprocess(self, _print):
        pass

    def build_report(self):
        print("Building code coverage report")
        print_line()
        f = cc_report_dir + "/cc.json"
        save_json(self._report, f)
        json2js("cc", f)
        cc = open(cc_report_dir + "/cc.txt", 'w')
        cc.write("{:.2f}".format(self._codecoverage))
        cc.close()
        return self._status

    def get_total(self):
        return self._total

    def get_failed(self):
        return self._failed

    def get_coverage(self):
        return self._codecoverage
