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



from .instance import *
from .test import Test
from .benchmarkinstance import BenchmarkInstance

logger = logging.getLogger(logging_context)


class BenchmarkTest(Test):

    def __init__(self, systemManager, hash, job, ssh, json_path, config, report_dir, remote_dir, source_dir, db):
        super().__init__(systemManager, hash, job, ssh, json_path, config, report_dir, remote_dir)
        self._source_dir = source_dir
        self._db = db
        json = self._json
        self._elements = 0
        self._nodes = 0
        if "geometry" in json:
            geometry = json["geometry"]
            if "nodes" in geometry:
                self._nodes = geometry["nodes"]
            if "elements" in geometry:
                self._elements = geometry["elements"]

    def run(self, build):
        self._db.add_benchmark(self._name, self._elements, self._nodes)
        return super().run(build)

    def prepare(self, build, instancemerger=None, fake=True):
        self._initialized = self._initialized
        self._instances[build.get_build_id()] = []
        self._pending_instances[build.get_build_id()] = []
        for execution in self._executions:
            openmp = True
            if "openmp" not in execution:
                openmp = False
                execution["openmp"] = 0
            elif execution["openmp"] == 0:
                openmp = False
            if self.valid(build, execution, openmp):
                instance = BenchmarkInstance(systemManager=self._systemManager,
                                             hash=self._hash,
                                             name=self._name,
                                             job=self._job,
                                             ssh=self._ssh,
                                             json=self._json,
                                             config=self._config,
                                             build=build,
                                             execution=execution,
                                             test_path=self._local_test_path,
                                             json_path=self._json_path,
                                             report_dir=self._report_dir,
                                             remote_dir=self._remote_dir,
                                             source_dir=self._source_dir,
                                             db=self._db)
                instance.initialize()
                if not fake:
                    self._pending_instances[build.get_build_id()].append(instance)
                else:
                    self._finished_instances[instance.get_id()] = instance
                    self._instances[build.get_build_id()].append(instance)


    def max_tasks(self, execution):
        return True

