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



from ..definitions import *
from ..connection.ssh import *
from time import sleep

logger = logging.getLogger(logging_context)


class QueueTester:

    def __init__(self, ssh, platform, hash, job):
        self._ssh = ssh
        self._platform = platform
        self._hash = hash
        self._queues = self._platform.get_queues()
        self._qos = self._platform.get_qos()
        self._reservation = self._platform.get_reservation()
        self._flex = self._platform.get_flex()
        self._path = self._platform.get_path()
        self._job = job

    def get_waiting_time(self, queue, tasks_per_node):
        if queue not in self._platform.get_slow_queue_printed():
            self._platform.get_slow_queue_printed()[queue] = False
        if queue not in self._platform.get_best_queues():
            self._platform.get_best_queues()[queue] = -1
        elif self._platform.get_best_queues()[queue] >= 0:
            return self._platform.get_best_queues()[queue]
        print("\tTesting queue " + queue + " with a dummy job...")
        tasks = tasks_per_node
        timeout = queue_max_timeout
        if queue in self._queues:
            if timetosecond(self._qos[queue].get_timeout()) < timetosecond(queue_max_timeout):
                timeout = self._qos[queue].get_timeout()
        self._platform.get_best_queues()[queue] = self.run_test_job(queue, tasks, timeout)
        return self._platform.get_best_queues()[queue]

    def run_test_job(self, queue, tasks, timeout):
        spath = self._path + "/" + remote_queue_dir + "/" + self._platform.get_platform() + "/" + queue
        lpath = queue_report_dir + "/" + queue
        critical_command("mkdir -p " + lpath)
        self._ssh.rmdir(system=self._platform.get_system(), path=spath)
        self._ssh.mkdir(system=self._platform.get_system(), path=spath, critical=True)
        self.write_test_job(spath, lpath, queue, tasks, timeout)
        self._ssh.scp_send(system=self._platform.get_system(), local=lpath+"/JOB.SB", remote=spath)
        job_id = self._job.launch_job(id=self._platform.get_platform() + "-" + queue, path=spath + "/JOB.SB",
                                      system=self._platform.get_system(), platform=self._platform.get_platform())
        sleep(queue_test_sleep_before_get_launch_time)
        start_time = self._job.get_start_time(job_id=job_id, system=self._platform.get_system(),
                                              platform=self._platform.get_platform())
        self._job.kill_job(job_id=job_id, system=self._platform.get_system(),
                           platform=self._platform.get_platform())
        if start_time is None:
            print("\t\tError when getting the dummy job expected start time, ignoring...")
            return infinitewtime()
        waiting_time = wtime(start_time)
        print("\t\tDummy job expected start time: in " + str(int(waiting_time)) + " hours")
        return waiting_time

    def write_test_job(self, spath, lpath, queue, tasks, timeout):
        script = open(lpath + "/JOB.SB", 'w')
        script.write("#!/bin/bash\n")
        script.write("#SBATCH -D " + spath + "\n")
        script.write("#SBATCH --output=queue.out\n")
        script.write("#SBATCH --error=queue.err\n")
        script.write("#SBATCH --job-name=" + jtitle + self._hash + "\n")
        script.write("#SBATCH --ntasks=" + str(tasks)+"\n")
        script.write("#SBATCH --time=" + timeout + "\n")
        script.write("#SBATCH " + self._platform.get_flag(queue) + "=" + queue + "\n")
        script.write("#SBATCH --exclusive\n")
        script.write("sleep " + str(timetosecond(timeout)) + "\n")
        script.write("\n")

    # return queue, flag, exclusive
    def which_qos(self, queue_type, cpus, timeout, flex=False, tasks_per_node=None, bypass_reservation=False,
                  enable_fast_queue=True):
        if tasks_per_node is None:
            tasks_per_node = self._platform.get_tasks_per_node()
        if self._reservation.get_enable() and not bypass_reservation:
            if self._flex and flex:
                queue = self._queues["flex"]
                if self._platform.is_queue_valid(queue, cpus / tasks_per_node, timeout):
                    return queue, self._platform.get_flag(queue), True
            reservation = self._reservation.get_reservation_name()
            if self._reservation.is_valid(cpus / tasks_per_node, timeout):
                return reservation, self._platform.get_flag(reservation), cpus / tasks_per_node >= 1
        queue = self._queues[queue_type]
        if self._platform.is_queue_valid(queue, cpus / tasks_per_node, timeout):
            if enable_fast_queue and "fast" in self._queues:
                best_wtime = self.get_waiting_time(queue, tasks_per_node)
                fast_queues = self._queues["fast"]
                if not isinstance(fast_queues, list):
                    fast_queues = [self._queues["fast"]]
                for fast_queue in fast_queues:
                    wtime = self.get_waiting_time(fast_queue, tasks_per_node)
                    if wtime < best_wtime:
                        if self._platform.is_queue_valid(fast_queue, cpus / tasks_per_node, timeout):
                            best_wtime = wtime
                            old_queue = queue
                            queue = fast_queue
                            if not self._platform.get_slow_queue_printed()[old_queue]:
                                print("\t\tQueue " + queue + " is faster than " + old_queue + "!")
                                self._platform.get_slow_queue_printed()[old_queue] = True
                        else:
                            if not self._platform.get_slow_queue_printed()[fast_queue]:
                                print("\t\tQueue " + fast_queue + " is not valid!")
                                self._platform.get_slow_queue_printed()[fast_queue] = True
                    else:
                        if not self._platform.get_slow_queue_printed()[fast_queue]:
                            print("\t\tQueue " + fast_queue + " is slower than " + queue + "!")
                            self._platform.get_slow_queue_printed()[fast_queue] = True
        else:
            if "default" in self._queues:
                queue = self._queues["default"]
            else:
                return None, None, cpus / tasks_per_node >= 1
        return queue, self._platform.get_flag(queue), cpus / tasks_per_node >= 1


