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
import re

from utils.compare import *
import sys


class Validate:

    def __init__(self, case):
        self._case = case
        self._file = case + ".json"
        self._json = None
        self._test = {}
        self._status = False
        self._error = "execution"
        self._cwd = os.getcwd()
        p = self._cwd.split("/")
        p = p[len(p)-1]
        self._mpi = p.split("_")[0]
        self._openmp = p.split("_")[1]
        p = self._cwd.split("/")
        p = p[len(p)-2]
        self._build = p
        self._base_dir = "base/1p"

    def run(self):
        self.open_json()
        self.set()
        self.env()
        if self.validate_execution():
            self.validate_files()
        self.save_json()

    def open_json(self):
        self._json = open_json(self._file)

    def set(self):
        json = self._json
        test = {}
        test["name"] = json["name"]
        test["mpi"] = int(self._mpi)
        test["openmp"] = int(self._openmp)
        test["build"] = self._build
        test["files"] = []
        test["hostname"] = "unknown"
        test["env"] = {}
        self._test = test

    def env(self):
        env = command('printenv', output=True)
        env = re.sub("\\{.*?^\\}", "", env, flags=re.DOTALL | re.MULTILINE)
        env = env.split("\n")
        env_dict = {}
        for i in env:
            try:
                d = i.split('=', 1)
                env_dict[d[0]] = d[1]
            except:
                continue
        self._test["env"] = env_dict
        self._test["hostname"] = env_dict["HOSTNAME"]

    def validate_execution(self):
        self._status = command("grep \"\-\-| ALYA  CALCULATIONS CORRECT\" alya.out")
        if not self._status:
            self._error = "execution"
        else:
            self._error = "OK"
        self._test["status"] = self._status
        self._test["error"] = self._error
        return self._status

    def validate_files(self):
        for file in self._json["comparisons"]:
            test = {}
            f = file["file"]
            test["file"] = f
            test["status"] = True
            test["error"] = "OK"
            test["maxAbs"] = 0
            test["maxRel"] = 0
            test["maxPower"] = 0
            test["differences"] = 0
            test["total"] = 0
            test["method"] = file["method"]
            if "rows" in file:
                rows = file["rows"]
            else:
                rows = None
            if "cols" in file:
                cols = file["cols"]
            else:
                cols = None
            if "tolerance" in file:
                test["tolerance"] = file["tolerance"]
            else:
                test["tolerance"] = 0
            if not self.present_file(self._base_dir + "/" + f):
                test["status"] = False
                test["error"] = "missing base"
            elif not self.present_file(f):
                test["status"] = False
                test["error"] = "missing test file"
            else:
                try:
                    res = self.compare(f, self._base_dir + "/" + f, test["method"], test["tolerance"], rows, cols)
                except Exception as e:
                    test["status"] = False
                    test["error"] = "comparison"
                    print(e)
                else:
                    test["maxAbs"] = res["maxAbs"]
                    test["maxRel"] = res["maxRel"]
                    test["maxPower"] = res["maxPower"]
                    test["differences"] = res["differences"]
                    test["total"] = res["total"]
                    test["status"] = res["status"]
                    test["error"] = res["error"]
            self.update_error(test["status"], test["error"])
            self._test["files"].append(test)
        self._test["status"] = self._status
        self._test["error"] = self._error

    def update_error(self, status, error):
        #New status is True, no need to update
        if status:
            return
        old_status = self._status
        #Updating status if new status is not True
        self._status = False
        #If old status is True, take error
        if old_status:
            self._error = error
            return
        #If old status is False, determine which error is the most important
        #Tolerance has the lowest priority
        #New error is tolerance, old one is not
        if "tolerance" in error and "tolerance" not in self._error:
            return
        #New error is not tolerance, new one is or is not
        if "tolerance" in self._error:
            self._error = error
            return
        #If new error is different, mixed, else, keep the same error
        if self._error != error:
            self._error = "mixed"
        return

    def save_json(self):
        save_json(self._test, "report.json")

    def present_file(self, file):
        return os.path.isfile(file)

    def compare(self, base, test, method, tolerance, rows=None, cols=None):
        c = Compare(base, test, method, tolerance, rows, cols)
        return c.compare()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: validate.py case")
        exit(1)
    validate = Validate(sys.argv[1])
    validate.run()
