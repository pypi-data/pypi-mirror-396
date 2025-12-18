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


logger = logging.getLogger(logging_context)


class InstanceMerger:

    def __init__(self, systemManager, hash, internalId, job, ssh, config, build, report_dir, remote_dir):
        self._queue_type = "tests"

        self._systemManager = systemManager
        self._hash = hash
        self._internalId = internalId
        self._job = job
        self._ssh = ssh
        self._build = build
        self._sbatch = {}
        self._id = self._build.get_build_id() + "_" + internalId
        self._system = build.get_system()
        self._platform = build.get_platform()
        self._sys = systemManager.get_platform(self._system, self._platform)
        self._report_path = report_dir + "/" + self._id + "/"
        self._remote_path = remote_dir + "/" + self._id + "/"
        self._config = config

        self._server_path = self._systemManager.get_system(self._system).get_path()
        self._account = self._sys.get_account()
        self._tasks = 0
        self._timeout = "00:00:00"
        offset = self._sys.get_timeoffset()
        self._timeout = sum(self._timeout, offset)
        self._job_status = "None"
        self._job_valid = False
        self._job_terminated = False
        self._job_launched = False
        self._job_id = 0
        self._waiting_job_id = False
        self._exec_modules = []

        self._queue = ""
        self._slurm_flag = ""
        self._exclusive = False

        self.set_sbatch()

        self._instances = {}

        self._empty = True

        self._max_jobs = max_jobs_staging

    def set_sbatch(self):
        self._sbatch["--cpus-per-task"] = self._sys.get_cpus_per_task()
        self._sbatch["--ntasks-per-node"] = self._sys.get_tasks_per_node()

    def eval_timeout(self, timeout):
        return timetosecond(timeout) > timetosecond(merged_max_timeout)

    def set_queue(self):
        queueTester = QueueTester(self._ssh, self._sys, self._hash, self._job)
        self._queue, self._slurm_flag, self._exclusive = queueTester.which_qos(
            self._queue_type, self._tasks, self._timeout, flex=False, tasks_per_node=self._sbatch["--ntasks-per-node"])
        self._exclusive = self._exclusive or self._build.get_exclusive_tests()

    def add_instance(self, instance):
        timeout = sum(instance.get_timeout(), self._timeout)
        if self.eval_timeout(timeout):
            return False
        else:
            self._timeout = timeout
            self._tasks = max(self._tasks, instance.get_tasks())
            self._instances[instance.get_id()] = instance
            instance.set_merged(True)
            self._empty = False
        return True

    def initialize(self):
        command("mkdir -p " + self._report_path)
        self.generate_job()

    def generate_job(self):
        gpu = False
        gpus = 0
        tasks = 0
        self.set_queue()
        spath = self._server_path + "/"
        script = open(self._report_path + "/JOB.SB", 'w')
        script.write("#!/bin/bash\n")
        script.write("#SBATCH -D " + spath + self._remote_path + "\n")
        script.write("#SBATCH --output=test.out\n")
        script.write("#SBATCH --error=test.err\n")
        script.write("#SBATCH --job-name=" + jtitle + self._hash + "\n")
        script.write("#SBATCH --ntasks=" + str(self._tasks) + "\n")
        ntask_per_node = "#SBATCH --ntasks-per-node=" + str(self._sys.get_tasks_per_node()) + "\n"
        script.write("#SBATCH --time=" + self._timeout + "\n")
        for parameter in self._sbatch:
            if parameter == "--ntasks-per-node":
                ntask_per_node = "#SBATCH --ntasks-per-node=" + str(self._sbatch[parameter]) + "\n"
            elif str(self._sbatch[parameter]) == "":
                script.write("#SBATCH " + parameter + "\n")
            else:
                script.write("#SBATCH " + parameter + "=" + str(self._sbatch[parameter]) + "\n")
        script.write(ntask_per_node)
        if self._account is not None:
            script.write("#SBATCH --account=" + self._account + "\n")
        if self._queue is not None:
            script.write("#SBATCH " + self._slurm_flag + "=" + self._queue + "\n")
        if self._exclusive:
            script.write("#SBATCH --exclusive\n")
        script.write("\n")
        for instance in self._instances:
            script.write("#---------------------------------\n")
            script.write("#Running test " + instance + "\n")
            script.write("#---------------------------------\n")
            script.write(self._instances[instance].get_script())
            script.write("touch test.out\n")
            script.write("touch test.err\n")
            script.write("\n")
        script.close()

    def run(self):
        self.launch_job()
        self._job_launched = False
        self._job_valid = True
        self._job_terminated = False

    def launch_job(self):
        self._job.launch_job(system=self._system,
                             platform=self._platform,
                             id=self._id,
                             path=self._remote_path + "/JOB.SB",
                             server_path=True,
                             asynchronous=True, max_jobs=self._max_jobs)

    def check_job(self):
        if not self._job_launched:
            if self._job.is_launched(system=self._system,
                                     platform=self._platform,
                                     id=self._id):
                self._job_launched = True
                self._job_id = self._job.get_job_id(system=self._system,
                                                    platform=self._platform,
                                                    id=self._id)
                for instance in self._instances:
                    self._instances[instance].set_job_id(self._job_id)
                    self._instances[instance].update_status(launched=True)
            else:
                return "Scheduled"
        if self._job_id == -1:
            self._job_valid = False
            self._job_terminated = True
            for instance in self._instances:
                self._instances[instance].update_status(valid=False, terminated=True)
        if self._job_valid and not self._job_terminated:
            self._job_status = self._job.check_job(job_id=self._job_id, system=self._system, platform=self._platform)
            if "Finished" in self._job_status:
                self._job_terminated = True
                for instance in self._instances:
                    self._instances[instance].update_status(terminated=True)
        elif not self._job_valid and self._job_terminated:
            return "Finished"
        return self._job_status

    def get_internalId(self):
        return self._internalId

    def is_empty(self):
        return self._empty
