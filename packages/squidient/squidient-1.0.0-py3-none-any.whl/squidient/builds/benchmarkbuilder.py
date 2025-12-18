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



from .builder import *
from .benchmarkbuild import BenchmarkBuild


class BenchmarkBuilder(Builder):

    def __init__(self, systemManager, hash, job, ssh, config, db, password=""):
        super().__init__(systemManager, hash, job, ssh, config, password)
        self._db = db

    def set_build_list(self):
        self._build_list = self._config["benchmarks"]["builds"]

    def set_report_dir(self):
        self._report_dir = benchmark_build_report_dir

    def clean_builds(self):
        command("rm -fr " + benchmark_build_report_dir)

    def create_build(self, build):
        return BenchmarkBuild(systemManager=self._systemManager,
                              hash=self._hash,
                              build_id=build,
                              job=self._job,
                              ssh=self._ssh,
                              config=self._config,
                              report_directory=self._report_dir,
                              db=self._db)

    def build_report(self):
        jump()
        print("Building monitor build report")
        print_line()
        report = {}
        for b in self._builds:
            self._builds[b].build_report()
            report[b] = self._builds[b].get_report()
        f = self._report_dir+"/benchmark_builds.json"
        save_json(report, f)
        json2js("benchmark_builds", f)
