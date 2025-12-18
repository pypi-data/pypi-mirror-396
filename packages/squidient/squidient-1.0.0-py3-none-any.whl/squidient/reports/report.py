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

logger = logging.getLogger(logging_context)


class Report:

    def __init__(self, tag):
        self._report = self.report()
        self._data = {}
        self._tag = tag
        self._valid = True
        self.open()

    def report(self):
        return report_dir + "/report.json"

    def init(self):
        self._data = {}
        self._data["alyaRevision"] = 0
        self._data["tag"] = self._tag
        self._data["valid"] = self._valid
        self.save()

    def open(self):
        try:
            self._data = open_critical_json(self._report)
        except:
            self.init()

    def clean(self):
        self.init()

    def valid(self, bool):
        self._valid = bool
        if "builds" in self._data:
            self._valid = self._valid and self._data["builds"]["status"]
        if "tests" in self._data:
            self._valid = self._valid and self._data["tests"]["status"]
        self._data["valid"] = self._valid
        self.save()

    def write_alya_revision(self, revision):
        self._data["alyaRevision"] = revision
        self.save()

    def get_alya_revision(self):
        return self._data["alyaRevision"]

    def get_tag(self):
        return self._data["tag"]

    def get_id(self):
        return str(self.get_alya_revision() + self.get_tag())

    def write_stage(self, stage, status, total, failed):
        data = {}
        data["status"] = status
        data["total"] = total
        data["failed"] = failed
        self._data[stage] = data
        self.save()

    def write_builds(self, status, total, failed):
        self.write_stage("builds", status, total, failed)

    def write_tests(self, status, total, failed):
        self.write_stage("tests", status, total, failed)

    def write_cc(self, coverage, total, failed, tool):
        data = {}
        data["coverage"] = coverage
        data["total"] = total
        data["failed"] = failed
        data["tool"] = tool
        self._data["code coverage"] = data
        self.save()

    def save(self):
        command("mkdir -p " + report_dir)
        save_json(self._data, self._report)
        json2js("report", self._report)

    def get_valid(self):
        return self._valid
