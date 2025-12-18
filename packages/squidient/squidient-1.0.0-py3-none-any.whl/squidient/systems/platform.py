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



from ..systems.system import *
from ..systems.reservation import *
from ..systems.partition import *
from ..utils.utils import *

logger = logging.getLogger(logging_context)


class Platform(System):

    def __init__(self, system, platform, config):
        super().__init__(system, config)
        self._platform = platform

        c = config["systems"][system]["platforms"][platform]

        self._host = c["host"]
        self._account = c["account"]
        if self._account == "":
            self._account = None
        self._threads = c["jobThreads"]
        self._test_max_tasks = c["testMaxTasks"]

        # architecture
        architecture = c["architecture"]

        self._alya_mpio_tools = None
        if 'alya-mpio-tools' in c:
            self._alya_mpio_tools = c["alya-mpio-tools"]
        else:
            raise Exception
        self._bind = ""
        if "bind" in architecture:
            self._bind = architecture["bind"]
        self._mpirun = {}
        if "mpirun" in c:
            self._mpirun = c["mpirun"]
        self._cpus_per_task = architecture["cpus_per_task"]
        self._sjobexitmod = architecture["sjobexitmod"]
        self._tasks_per_node = architecture["tasks_per_node"]
        self._type = architecture["type"]

        self._gpus_per_node = 0
        self._gpu_sbatch = {}
        if "gpu" in architecture:
            self._gpu = architecture["gpu"]
            if "gpus_per_node" in self._gpu:
                self._gpus_per_node = self._gpu["gpus_per_node"]
            if "tasks_per_gpu" in self._gpu:
                self._tasks_per_gpu = self._gpu["tasks_per_gpu"]

        if self._type != "slurm":
            print("The platform " + self._platform + " is not compatible with slurm")
            raise Exception

        # installation
        self._application_path = c["installation"]["applicationPath"]
        self._module_path = c["installation"]["modulePath"]
        self._python_path = c["installation"]["pythonPath"]

        # qos
        self._qos = {}
        for qos in c["qos"]:
            self._qos[qos] = QoS(qos, c["qos"][qos])

        # partition
        self._partition = {}
        for partition in c["partition"]:
            self._partition[partition] = Partition(partition, c["partition"][partition])

        # queues
        self._queues = {}
        for queue in c["queues"]:
            self._queues[queue] = c["queues"][queue]

        self._best_queues = {}
        for queue in self._queues:
            if isinstance(self._queues[queue], str):
                self._best_queues[self._queues[queue]] = -1
            elif isinstance(self._queues[queue], list):
                for q in self._queues[queue]:
                    self._best_queues[q] = -1

        self._slow_queues_printed = {}
        for queue in self._queues:
            if isinstance(self._queues[queue], str):
                self._slow_queues_printed[self._queues[queue]] = False
            elif isinstance(self._queues[queue], list):
                for q in self._queues[queue]:
                    self._slow_queues_printed[q] = False

        # reservation
        self._reservation = Reservation(c["reservation"])

        # flex
        self._flex = config["flex"]

        # time offset
        self._timeoffset = "00:00:00"
        if "timeOffset" in c:
            self._timeoffset = c["timeOffset"]

        # merge
        self._merge = c["merge"]

        self._ssh_key = None
        if "sshKey" in c:
            self._ssh_key = c["sshKey"]

    def get_account(self):
        return self._account

    def is_queue_valid(self, queue, size, timeout):
        if queue in self._qos:
            return self._qos[queue].is_valid(size, timeout)
        elif queue in self._partition:
            return self._partition[queue].is_valid(size, timeout)
        else:
            return True

    def get_flag(self, queue):
        if queue == self._reservation.get_reservation_name():
            return self._reservation.get_slurm_option()
        elif queue in self._qos:
            return self._qos[queue].get_slurm_option()
        elif queue in self._partition:
            return self._partition[queue].get_slurm_option()
        else:
            return "--qos"

    def get_application_path(self):
        return self._application_path

    def get_module_path(self):
        return self._module_path

    def get_python_path(self):
        return self._python_path

    def get_bind(self):
        return self._bind

    def get_mpirun(self):
        return self._mpirun

    def get_mpirun_options(self, modules):
        mpirun = self._mpirun
        mpirun_options = []
        found = False
        for m in mpirun:
            for modu in modules:
                if m in modu:
                    if "options" in mpirun[m]:
                        mpirun_options = mpirun[m]["options"]
                        found = True
                    break
            if found:
                break
        return mpirun_options

    def get_cpus_per_task(self):
        return self._cpus_per_task

    def get_tasks_per_node(self):
        return self._tasks_per_node

    def get_sjobexitmod(self):
        return self._sjobexitmod

    def get_reservation(self):
        return self._reservation

    def get_threads(self):
        return self._threads

    def get_test_max_tasks(self):
        return self._test_max_tasks

    def get_timeoffset(self):
        return self._timeoffset

    def get_merge(self):
        return self._merge

    def get_flex(self):
        return self._flex

    def get_queues(self):
        return self._queues

    def get_best_queues(self):
        return self._best_queues

    def get_slow_queue_printed(self):
        return self._slow_queues_printed

    def get_qos(self):
        return self._qos

    def get_partition(self):
        return self._partition

    def get_platform(self):
        return self._platform

    def get_gpus_per_node(self):
        return self._gpus_per_node

    def get_tasks_per_gpu(self):
        return self._tasks_per_gpu

    def get_alya_mpio_tools_modules(self):
        return self._alya_mpio_tools["modules"]