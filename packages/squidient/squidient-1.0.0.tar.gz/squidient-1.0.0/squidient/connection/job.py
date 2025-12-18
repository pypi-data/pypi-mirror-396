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



from ..utils.message import *
from ..utils.utils import *
from ..definitions import *
from ..connection.buildlock import *
import re
import threading
import queue

logger = logging.getLogger(logging_context)


class JobThread (threading.Thread):

    def __init__(self, ssh, system, platform, input_queue, output_queue, max_jobs=max_jobs_staging):
        threading.Thread.__init__(self)
        self._ssh = ssh
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._system = system
        self._platform = platform
        self._current_jobs = max_jobs
        self._check_jobs = 0
        self._max_jobs = max_jobs

    def run(self):
        while True:
            self._check_jobs += 1
            self._current_jobs += 1
            job = self._input_queue.get()
            while self._current_jobs > self._max_jobs or self._check_jobs > check_jobs_every_normal:
                self._check_jobs = 0
                self._current_jobs = self.get_job_numbers()
                if self._current_jobs > self._max_jobs:
                    time.sleep(20)
            output = self._ssh.ssh(cmd=job["command"], system=self._system, platform=self._platform,
                                   server_path=job["server_path"], output=True)
            try:
                job_id = re.findall("Submitted batch job \d+", output)[0]
                job_id = int(re.findall("\d+", job_id)[0])
            except:
                job_id = -1
            job["job_id"] = job_id
            job["launched"] = True
            self._output_queue.put(job)

    def get_job_numbers(self):
        job_number = 0
        try:
            #job_number = int(self._ssh.ssh("squeue | wc -l", system=self._system, platform=self._platform, output=True).strip()) - 1
            job_number = max(len(self._ssh.ssh("squeue", system=self._system, platform=self._platform, output=True).split("\n")) - 2, 0)
        except:
            print("Cannot determine running jobs")
            logger.warning("Cannot determine job number")
        logger.debug("Job number of " + self._platform + " retrieved with squeue: " + str(job_number))
        return job_number


class Job:

    def __init__(self, systemManager, ssh, hash):
        self._systemManager = systemManager
        self._hash = hash
        self._ssh = ssh
        self._time = -1
        self._build_lock = BuildLock()
        self._jobs = {}
        self._jobs_not_actualized = {}
        self._jobs_launched = {}
        self._jobs_not_launched = {}
        self._job_list = {}
        self._input_queues = {}
        self._output_queues = {}
        self._job_threads = {}
        self._thread_number = {}
        for system in systemManager.get_systems():
            self._jobs[system] = {}
            self._jobs_not_actualized[system] = {}
            self._jobs_launched[system] = {}
            self._jobs_not_launched[system] = {}
            self._job_list[system] = {}
            self._input_queues[system] = {}
            self._output_queues[system] = {}
            self._job_threads[system] = {}
            self._thread_number[system] = {}
            for platform in systemManager.get_platforms(system):
                self._thread_number[system][platform] = systemManager.get_platform(system, platform).get_threads()
        command("rm -fr squeue")
        command("mkdir -p squeue")

    def launch_job(self, id, path, system, platform, server_path=False, key_lock="", asynchronous=False, max_jobs=max_jobs_staging):
        dep = ""
        if key_lock != "":
            if asynchronous:
                print("You cannot launch an asynchronous job with a dependency!")
                raise Exception
            lock_id = self._build_lock.get_lock(key_lock)
            if lock_id != -1:
                dep = "--dependency=afterany:" + str(lock_id) + " "
        if platform not in self._job_threads[system]:
            self._input_queues[system][platform] = queue.Queue()
            self._output_queues[system][platform] = queue.Queue()
            self._job_threads[system][platform] = []
            if self._thread_number[system][platform] < 1:
                print("Thread number must be greater than 0!")
                raise Exception
            for i in range(self._thread_number[system][platform]):
                self._job_threads[system][platform].append(JobThread(self._ssh, system, platform,
                                                                     self._input_queues[system][platform],
                                                                     self._output_queues[system][platform],
                                                                     max_jobs=max_jobs))
                self._job_threads[system][platform][i].daemon = True
                self._job_threads[system][platform][i].start()
            self._jobs_not_launched[system][platform] = {}
            self._jobs_launched[system][platform] = {}
            self._jobs_not_actualized[system][platform] = {}
            self._jobs[system][platform] = {}
        job = {}
        job["id"] = id
        job["launched"] = False
        job["command"] = "sbatch " + dep + path
        job["server_path"] = server_path
        self._input_queues[system][platform].put(job)
        self._jobs_not_launched[system][platform][id] = job
        if not asynchronous:
            while not self.is_launched(system, platform, id):
                time.sleep(1)
            job_id = self.get_job_id(system, platform, id)
            if key_lock != "":
                self._build_lock.set_lock(key_lock, job_id)
            return job_id
        else:
            return -1

    def get_start_time(self, job_id, system, platform):
        output = self._ssh.ssh(cmd="squeue --start", system=system, platform=platform, output=True)
        logger.debug("squeue --start = " + output)
        output = output.split("\n")
        found = None
        for o in output:
            if str(job_id) in o:
                logger.debug("found job in squeue --start: " + o)
                found = " ".join(o.strip().split()).split()
                break
        try:
            if found is None:
                raise Exception
            status = found[4]
            logger.debug("status = " + status)
        except:
            logger.warning("Cannot parse status, trying to run squeue")
            output = self._ssh.ssh(cmd="squeue --noheader --format=\"%i %P %j %u %T %M %D %R\"", system=system, platform=platform, output=True)
            logger.debug("squeue = " + output)
            output = output.split("\n")
            found2 = None
            for o in output:
                if str(job_id) in o:
                    logger.debug("found job in squeue: " + o)
                    found2 = " ".join(o.strip().split()).split()
                    break
            try:
                if found2 is None:
                    raise Exception
                status = found2[4]
                logger.debug("status(2) = " + status)
            except:
                logger.error("Cannot parse status")
                return None
        if status in ["PD"] :
            logger.debug("Job is pending, continue")
        elif status in ["CG", "R"]:
            logger.debug("Job is not pending, return current time")
            return datetime.now()
        else:
            logger.error("Job status is invalid: " + status)
            return None
        try:
            dt = found[5]
        except:
            logger.error("Cannot parse start time")
            return None
        if "N/A" in dt:
            logger.debug("Start time is N/A")
            return datetime(year=datetime.now().year+100, month=1, day=1)
        else:
            date, time = dt.split("T")
            logger.debug("Start time is " + dt)
            year, month, day = date.split("-")
            hour, minute, second = time.split(":")
            return datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second))

        #26147407      main   JOB.SB alya_cic PD                 N/A     34 (null)               (Priority)
        #        6457904	main alyacicd alya_cic PD 2022-11-23T13:26:08	   1 p9r2n14              (Priority)

    def kill_job(self, job_id, system, platform):
        return self._ssh.ssh(cmd="scancel " + str(job_id), system=system, platform=platform)

    def synchronize_jobs(self, system, platform):
        while not self._output_queues[system][platform].empty():
            try:
                job = self._output_queues[system][platform].get(timeout=10)
            except:
                break
            else:
                self._jobs_launched[system][platform][job["id"]] = job
                self._jobs_not_launched[system][platform].pop(job["id"])

    def is_launched(self, system, platform, id):
        self.synchronize_jobs(system, platform)
        if id in self._jobs_not_launched[system][platform]:
            return False
        elif id in self._jobs_launched[system][platform]:
            return True
        return True

    def get_job_id(self, system, platform, id):
        job_id = -1
        if id in self._jobs_launched[system][platform]:
            job_id = self._jobs_launched[system][platform][id]["job_id"]
            self._jobs[system][platform][job_id] = job_id
            self._jobs_not_actualized[system][platform][job_id] = job_id
            self._jobs_launched[system][platform].pop(id)
        return job_id

    def kill_all(self):
        jump()
        for system in self._job_threads:
            for platform in self._job_threads[system]:
                self._ssh.ssh(cmd="scancel --name=" + jtitle + self._hash, system=system, platform=platform)
        self._jobs.clear()
        print()

    def job_list(self, force=False):
        timet = time.time()
        ok = {}
        if force or self._time == -1 or timet - self._time > actualize_time:
            self._time = timet
            for system in self._jobs:
                ok[system] = {}
                for platform in self._jobs[system]:
                    self._job_list[system][platform] = self._ssh.ssh(cmd="squeue --format=\"%i %P %j %u %T %M %D %R\"", system=system, platform=platform, output=True)
                    ok[system][platform] = "JOBID" in self._job_list[system][platform]
                    if ok[system][platform]:
                        write_text_file("squeue/" + system + "-" + platform, self._job_list[system][platform])
            for system in self._jobs_not_actualized:
                for platform in self._jobs_not_actualized[system]:
                    if ok[system][platform]:
                        self._jobs_not_actualized[system][platform].clear()

    def check_job(self, job_id, system, platform, force=False):
        self.job_list(force)
        if platform in self._jobs_not_actualized[system]:
            if job_id in self._jobs_not_actualized[system][platform]:
                return "Pending"
        elif platform in self._jobs[system]:
            if job_id not in self._jobs[system][platform]:
                return "Finished"

        with open("squeue/" + system + "-" + platform, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return "Error"

        headers = ["JOBID", "PARTITION", "NAME", "USER", "STATE", "TIME", "NODES", "REASON"]

        for line in lines[1:]:
            parts = line.split()

            if len(parts) > len(headers):
                parts = parts[:len(headers) - 1] + [' '.join(parts[len(headers) - 1:])]

            if len(parts) != len(headers):
                continue

            entry = dict(zip(headers, parts))

            if entry["JOBID"] is not None:
                try:
                    if int(job_id) == int(entry["JOBID"]):
                        if "CG" in entry["STATE"]:
                            return "Terminating"
                        elif "PD" in entry["STATE"]:
                            return "Pending"
                        elif "R" in entry["STATE"]:
                            duration = entry["TIME"]
                            return "Running " + duration
                        else:
                            return "Unknown"
                except:
                    # This is not a job
                    continue
        if job_id in self._jobs[system][platform]:
            self._jobs[system][platform].pop(job_id)
        return "Finished"
