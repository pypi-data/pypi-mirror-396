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

from .executablebuild import *
from ..utils.log import *

logger = logging.getLogger(logging_context)


class BenchmarkBuild(ExecutableBuild):

    def __init__(self, systemManager, hash, build_id, job, ssh, config, report_directory, db):
        super().__init__(systemManager, hash, build_id, job, ssh, config, report_directory)
        self._queue_type = "benchmarks"
        self._db = db
        self._max_jobs = max_jobs_monitor

    def add_to_db(self):
        db_build = {}
        db_build["modules"] = self._modules
        db_build["environment"] = self._env
        db_build["preExec"] = self._pre_exec
        db_build["preModules"] = self._pre_modules
        db_build["postModules"] = self._post_modules
        db_build["tags"] = self._tags
        db_build["codeCoverage"] = self._code_coverage
        db_build["system"] = self._system
        db_build["platform"] = self._platform
        db_build["type"] = self._type
        db_build["ctest"] = self._ctest
        db_configuration = self._options.get_configuration()
        self._db.add_build(name=self._build_id, compiler=self._compiler, version=self._version,
                           system=self._system, platform=self._platform, build=db_build, configuration=db_configuration)

    def launch_job(self):
        self.add_to_db()
        return super().launch_job()

