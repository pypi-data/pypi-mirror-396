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



from .instance import Instance
from ..utils.log import *
from ..definitions import max_jobs_monitor

logger = logging.getLogger(logging_context)


class BenchmarkInstance(Instance):

    def __init__(self, systemManager, hash, name, job, ssh, json, config, build, execution, test_path, json_path, report_dir,
                 remote_dir, source_dir, db):
        super().__init__(systemManager, hash, name, job, ssh, json, config, build, execution, test_path, json_path, report_dir,
                         remote_dir, source_dir)
        self._queue_type = "benchmarks"
        self._max_jobs = max_jobs_monitor

        self._db = db
        self._xp_id = -1

        self._remove_env = False

    def eval_timeout(self, timeout):
        return False

    def set_max_retry(self):
        self._max_retry = 0

    def add_xp_to_db(self):
        if not self._relaunch and self._report["status"]:
            self._xp_id = self._db.add_xp(self._name, self._build.get_build_id(), self._job_id, self._start, self._end,
                                          int(self._mpi), int(self._openmp), self._report["env"])

    def add_measures_to_db(self):
        coupling = False
        self._db.add_measure(coupling, "test", 1, None)
        if not self._relaunch and self._report["status"] and self._xp_id > 0:
            if len(self._report["performance"]) > 1:
                coupling = True
            for code in self._report["performance"]:
                for row in self._report["performance"][code]:
                    self._db.add_measure(self._xp_id, coupling, code, row)

    def add_counters_to_db(self):
        if not self._relaunch and self._report["status"] and self._xp_id > 0:
            for type in self._report["counters"]:
                self._db.add_counter(self._xp_id, type, self._report["counters"][type])

    def build_report(self, download_report=False):
        super().build_report(download_report)
        self.add_xp_to_db()
        self.add_measures_to_db()
        self.add_counters_to_db()
