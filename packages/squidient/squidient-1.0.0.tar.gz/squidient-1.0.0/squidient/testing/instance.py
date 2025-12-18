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



from ..connection.job import *
import csv
from ..systems.queuetester import *


logger = logging.getLogger(logging_context)


class Instance:

    def __init__(self, systemManager, hash, name, job, ssh, json, config, build, execution, test_path, json_path, report_dir, remote_dir, source_dir=None):
        self._queue_type = "tests"
        self._mergeable = True
        self._merged = False
        self._systemManager = systemManager
        self._hash = hash
        self._name = name
        self._job = job
        self._ssh = ssh
        self._build = build
        self._execution = execution
        self._sbatch = {}
        self._mpi = str(execution["mpi"])
        self._openmp = str(execution["openmp"])
        self._id = self._name + "_" + self._build.get_build_id() + "_" + self._mpi + "_" + self._openmp
        self._system = build.get_system()
        self._platform = build.get_platform()
        self._sys = systemManager.get_platform(self._system, self._platform)
        self._report_path = report_dir + "/" + self._name + "/" + self._build.get_build_id() + "/" + self._mpi + "_" + self._openmp
        self._remote_path = remote_dir + "/" + self._name + "/" + self._build.get_build_id() + "/" + self._mpi + "_" + self._openmp
        self._test_path = test_path
        self._json_path = json_path
        self._config = config

        self._server_path = self._systemManager.get_system(self._system).get_path()
        self._account = self._sys.get_account()

        if source_dir is not None:
            self._source_path = self._server_path + "/" + source_dir
        else:
            self._source_path = self._server_path

        self._json = json
        self._postprocess = json["postprocess"]
        if "timeout" in json:
            self._timeout = json["timeout"]
        else:
            self._timeout = test_default_timeout

        try:
            if self.eval_timeout(self._timeout):
                raise Exception
        except:
            self._timeout = test_default_timeout

        offset = self._sys.get_timeoffset()
        self._timeout = sum(self._timeout, offset)

        offset = self._build.get_timeoffset()
        self._timeout = sum(self._timeout, offset)

        self._start = 0
        self._end = 0

        self._job_status = "None"
        self._job_valid = False
        self._job_terminated = False
        self._job_launched = False
        self._job_id = 0
        self._relaunch = False
        self._retry = 0
        self._build_report = True

        self._report = {}

        self._alya_cmd = ""
        self._pp_cmd = ""
        self._exec_modules = []

        self._queue = ""
        self._slurm_flag = ""
        self._exclusive = False

        self._max_retry = 0

        self.set_max_retry()

        self._remove_env = True

        self._run_bind = self._sys.get_bind()
        self._run_map = ""

        self._mpirun_options = self._sys.get_mpirun_options(self._build.get_modules())
        self._run_options = None


        self.set_sbatch()
        self.set_bind_and_map()
        self.set_run_options()

        self._binding_report = "BINDING_REPORT"

        self._script = ""

        self._max_jobs = max_jobs_staging

    def overloaded(self):
        return int(self._sys.get_test_max_tasks())<int(self._mpi)*int(max(1,int(self._openmp)))

    def set_sbatch(self):

        self._sbatch["--cpus-per-task"] = self._sys.get_cpus_per_task()
        self._sbatch["--ntasks-per-node"] = self._sys.get_tasks_per_node()
        if "sbatch" in self._execution:
            for parameter in self._execution["sbatch"]:
                self._sbatch[parameter] = self._execution["sbatch"][parameter]
                self._mergeable = False

    def set_bind_and_map(self):
        if "commands" in self._execution:
            if "bind" in self._execution["commands"]:
                self._run_bind = self._execution["commands"]["bind"]
                self._mergeable = False
            if "map" in self._execution["commands"]:
                self._run_map = self._execution["commands"]["map"]
                self._mergeable = False

    def set_run_options(self):
        self._run_options = ""
        for option in self._mpirun_options:
            self._run_options += option + " "

    def eval_timeout(self, timeout):
        return timetosecond(timeout) > timetosecond(test_max_timeout)

    def set_queue(self):
        queueTester = QueueTester(self._ssh, self._sys, self._hash, self._job)
        self._queue, self._slurm_flag, self._exclusive = queueTester.which_qos(
            queue_type=self._queue_type,
            cpus=self.get_tasks(),
            timeout=self._timeout,
            flex=False,
            tasks_per_node=self._sbatch["--ntasks-per-node"])
        self._exclusive = self._exclusive or self._build.get_exclusive_tests()

    def set_max_retry(self):
        self._max_retry = test_max_retry

    def initialize(self):
        command("mkdir -p " + self._report_path)
        critical_command("cp " + self._json_path + " " + self._report_path)
        self.custom_commands()
        self.generate_job()

    def custom_commands(self):
        alya_custom = ""
        pp_custom = ""
        alya_out = " >> alya.out 2>> alya.err"
        run_exec = "mpirun"
        run_proc = "-np"
        run_sep = ":"
        alya_default = run_exec + " " + self._run_bind + " " + self._run_map + " " + self._run_options + " $" + self._binding_report + " " + run_proc + " " + self._mpi + " $ALYA " + self._name
        pp_out = " >> post.out 2>> post.err"
        pp_default = 'echo "Nothing to do"'
        pp = ""
        pp_function = ""
        if "alya2pos" in self._postprocess:
            pp = "$ALYA2POS"
            pp_default = pp + " " + self._name
        elif "mpio2txt" in self._postprocess:
            pp_modules = "module purge "
            if len(self._sys.get_alya_mpio_tools_modules()) > 0:
                pp_modules += "&& module load "
                for m in self._sys.get_alya_mpio_tools_modules():
                    pp_modules += m + " "
            pp_modules += "&& "
            pp_function_cmd = pp_modules + run_exec + " " + self._run_bind + " " + self._run_map + " " + self._run_options + " " + run_proc + " " + self._mpi + " " + mpio2txt_bin + " -m "
            pp_function = "\nfmpio2txt()\n{\n\t" + pp_function_cmd + "$1\n}\n"
            pp = "fmpio2txt "
            pp_default = "fmpio2txt " + self._name
        self._alya_cmd = alya_default + alya_out
        self._pp_cmd = pp_function + pp_default + pp_out
        if "commands" in self._execution:
            if "alya" in self._execution["commands"]:
                alya_custom = self._execution["commands"]["alya"]
            if "modules" in self._execution["commands"]:
                self._exec_modules = self._execution["commands"]["modules"]
            if "postprocess" in self._execution["commands"]:
                pp_custom = self._execution["commands"]["postprocess"]
        if alya_custom != "":
            alya_custom = alya_custom.replace("[RUN]", run_exec + " " + self._run_bind + " " + self._run_map + " " + self._run_options)
            alya_custom = alya_custom.replace("[NP]", run_proc)
            alya_custom = alya_custom.replace("[MPI]", self._mpi)
            alya_custom = alya_custom.replace("[NAME]", self._name)
            alya_custom = alya_custom.replace("[SEP]", run_sep)
            alya_custom = alya_custom.replace("[ALYA]", "$ALYA")
            alya_custom = alya_custom.replace(";", alya_out + ";")
            alya_custom = alya_custom.replace("&&", alya_out + "&&")
            self._alya_cmd = alya_custom + alya_out
        if pp_custom != "":
            pp_custom = pp_custom.replace("[POST]", pp)
            pp_custom = pp_custom.replace("[NAME]", self._name)
            pp_custom = pp_custom.replace("[ALYA-PATH]", self._server_path + "/" + alya_dir)
            pp_custom = pp_custom.replace(";", pp_out + ";")
            pp_custom = pp_custom.replace("&&", pp_out + "&&")
            self._pp_cmd = pp_function + pp_custom + pp_out

    def send(self, asynchronous=False):
        if not asynchronous:
            lock = None
        else:
            lock = self._ssh.next_lock()
        self._ssh.mkdir(system=self._system,
                        path=self._remote_path,
                        server_path=True,
                        asynchronous=asynchronous,
                        lock=lock,
                        critical=True)
        self._ssh.scp_send(system=self._system,
                           local=self._report_path + "/JOB.SB",
                           remote=self._remote_path,
                           server_path=True,
                           critical=True,
                           asynchronous=asynchronous,
                           lock=lock)

    def run(self):
        self.launch_job()
        self._job_launched = False
        self._job_valid = True
        self._job_terminated = False

    def generate_job(self):
        self.set_queue()
        spath = self._server_path + "/"
        script = open(self._report_path + "/JOB.SB", 'w')
        script.write("#!/bin/bash\n")
        script.write("#SBATCH -D " + spath + self._remote_path + "\n")
        script.write("#SBATCH --output=test.out\n")
        script.write("#SBATCH --error=test.err\n")
        #script.write("#SBATCH --kill-on-bad-exit=0\n")
        script.write("#SBATCH --job-name=" + jtitle + self._hash + "\n")
        script.write("#SBATCH --ntasks=" + str(self.get_tasks()) + "\n")
        ntask_per_node = "#SBATCH --ntasks-per-_node=" + str(self._sys.get_tasks_per_node()) + "\n"
        script.write("#SBATCH --time=" + self._timeout + "\n")
        for parameter in self._sbatch:
            if parameter == "--ntasks-per-node":
                ntask_per_node = "#SBATCH --ntasks-per-node=" + str(self._sbatch[parameter]) + "\n"
            elif str(self._sbatch[parameter]) == "":
                script.write("#SBATCH " + parameter + "\n")
            else:
                script.write("#SBATCH " + parameter + "=" + str(self._sbatch[parameter]) + "\n")
        script.write(ntask_per_node)
        if self._queue is not None:
            script.write("#SBATCH " + self._slurm_flag + "=" + self._queue + "\n")
        if self._exclusive:
            script.write("#SBATCH --exclusive\n")
        if self._account is not None:
            script.write("#SBATCH --account=" + self._account + "\n")
        script.write("\n")
        self._script = "cd " + spath + self._remote_path + "\n"
        self._script += "date '+%s' > time.out\n"
        self._script += "module purge\n"
        for pre_module in self._build.get_pre_modules():
            self._script += pre_module + "\n"
        for module in self._build.get_modules():
            self._script += "module load " + module + "\n"
        for module in self._exec_modules:
            self._script += "module load " + module + "\n"
        for post_module in self._build.get_post_modules():
            self._script += post_module + "\n"
        self._script += "\n"
        for env in self._build.get_env():
            self._script += env + "\n"
        self._script += "export ALYA=" + spath + remote_bin_dir + "/alya_" + self._build.get_build_id() + "\n"
        self._script += "export ALYA2POS=" + spath + remote_bin_dir + "/alya2pos_" + self._build.get_build_id() + "\n"
        self._script += "ln -s " + self._source_path + "/" + self._test_path + "/* .\n"
        if int(self._openmp) > 0:
            self._script += "export OMP_NUM_THREADS=" + self._openmp + "\n"
        else:
            self._script += "unset OMP_NUM_THREADS\n"
        for pre_exec in self._build.get_pre_exec():
            self._script += pre_exec + "\n"
        self._script += 'if mpirun -V | grep "Open MPI"; then export ' + self._binding_report + '="--report-bindings"' + "; fi\n"
        self._script += 'if mpirun -V | grep "Intel"; then export ' + self._binding_report + '="-print-rank-map"' + "; fi\n"
        self._script += "echo $" + self._binding_report + "\n"
        self._script += "rm -f alya.out alya.err infiniband.out\n"
        self._script += "cat /sys/class/infiniband/hfi1_0/ports/1/counters/port_rcv_data > infiniband.out\n"
        self._script += "cat /sys/class/infiniband/hfi1_0/ports/1/counters/port_xmit_data >> infiniband.out\n"
        self._script += "date '+%s' >> time.out\n"
        self._script += self._alya_cmd + "\n"
        self._script += "date '+%s' >> time.out\n"
        self._script += "cat /sys/class/infiniband/hfi1_0/ports/1/counters/port_rcv_data >> infiniband.out\n"
        self._script += "cat /sys/class/infiniband/hfi1_0/ports/1/counters/port_xmit_data >> infiniband.out\n"
        self._script += "rm -f post.out post.err\n"
        self._script += self._pp_cmd + "\n"
        self._script += "date '+%s' >> time.out\n"
        self._script += self._sys.get_python_path() + "/python3 " + spath + remote_ts_dir + "/validate.py " + self._name + "\n"
        self._script += "date '+%s' >> time.out\n"
        self._script += "\n"
        script.write(self._script)
        script.close()

    def launch_job(self):
        if self._relaunch:
            self._merged = False
            self._build_report = True
            self._ssh.ssh(system=self._system, cmd='rm -frv !("JOB.SB")', server_path=True, path=self._remote_path)
        self._job.launch_job(system=self._system,
                             platform=self._platform,
                             id=self._id + "_" + str(self._retry),
                             path=self._remote_path + "/JOB.SB",
                             server_path=True,
                             asynchronous=True, max_jobs=self._max_jobs)

    def check_job(self):
        if self._merged:
            if self._job_terminated:
                return "Finished"
            elif not self._job_launched:
                return "Scheduled"
            else:
                return "Unknown"
        if not self._job_launched:
            if self._job.is_launched(system=self._system,
                                     platform=self._platform,
                                     id=self._id + "_" + str(self._retry)):
                self._job_launched = True
                self._job_id = self._job.get_job_id(system=self._system,
                                                    platform=self._platform,
                                                    id=self._id + "_" + str(self._retry))
            else:
                return "Scheduled"
        if self._job_id == -1:
            self._job_valid = False
            self._job_terminated = True
        if self._job_valid and not self._job_terminated:
            self._job_status = self._job.check_job(job_id=self._job_id, system=self._system, platform=self._platform)
            if "Finished" in self._job_status:
                self._job_terminated = True
        elif not self._job_valid and self._job_terminated:
            return "Finished"
        return self._job_status

    def download_report(self):
        if not self._ssh.rsync_get(system=self._system,
                                   remote=self._remote_path + "/*",
                                   local=self._report_path + "/",
                                   options='-m --include="*/" --include="report.json" --include="*.out" --include="*.err" --exclude="*"',
                                   server_path=True):
            if not self._ssh.rsync_get(system=self._system,
                                       remote=self._remote_path + "/*",
                                       local=self._report_path + "/",
                                       options='-m --include="*/" --include="report.json" --include="*.out" --include="*.err" --exclude="*"',
                                       server_path=True):
                raise Exception

    def build_report(self, download_report=False):
        if not self._build_report:
            return
        if download_report:
            try:
                self.download_report()
            except:
                print("Cannot download the report. Instance: " + self._id)
        error = "unknown"
        if not self._job_valid and self._job_terminated:
            error = "slurm"
        try:
            self._report = open_critical_json(self._report_path + "/report.json")
        except:
            print("Warning: report not found! Create a dummy report. Instance: " + self._id)
            self.build_failed_report(error)
        critical_command("cp " + self._json_path + " " + self._report_path)
        self._report["path"] = self._test_path
        self._report["relaunched"] = self._retry > 0
        self._report["retries"] = self._retry
        self._report["jobId"] = self._job_id

        if self._remove_env:
            self._report["env"] = {}

        self._relaunch = False

        if self._report["error"] in ["slurm"]:
            self.retry()
        else:
            if command("grep 'DUE TO TIME LIMIT' " + self._report_path + "/test.err"):
                self._report["error"] = "timeout"
                self.retry()
            elif command("grep 'already completing or completed' " + self._report_path + "/post.err"):
                self._report["error"] = "timeout"
                self.retry()
            elif command("grep 'Expired or invalid job' " + self._report_path + "/post.err"):
                self._report["error"] = "timeout"
                self.retry()
            elif command("grep 'All nodes which are allocated for this job are already filled' " + self._report_path + "/alya.err"):
                self._report["error"] = "overload"
            elif command("grep 'A request was made to bind to that would result in binding more' " + self._report_path + "/alya.err"):
                self._report["error"] = "binding"
            elif command("grep 'Integer overflow in xmallocarray' " + self._report_path + "/alya.err"):
                self.retry()
            elif not command("grep 'START ALYA' " + self._report_path + "/alya.out"):
                self._report["error"] = "job"
                self.retry()
            elif command("grep 'Program received signal SIGSEGV' " + self._report_path + "/alya.err"):
                self.retry()
            elif command("grep 'Bus error' " + self._report_path + "/alya.err"):
                self.retry()
            elif command("grep 'Transport retry count exceeded on' " + self._report_path + "/alya.err"):
                self.retry()
            elif command("grep 'Transport retry count exceeded on' " + self._report_path + "/post.err"):
                self.retry()
            elif command("grep 'srun: error: Unable to create step for job' " + self._report_path + "/post.err"):
                self.retry()
            elif command("grep 'Fatal error in PMPI_Init: Unknown error class, error stack' " + self._report_path + "/post.err"):
                self.retry()
            if not self.compute_times():
                self._report["error"] = "timeout"
                self.retry()
            elif self._merged and timetosecond(self._report["jobTime"]) > timetosecond(self._timeout):
                self._report["error"] = "timeout"
        self.build_performance()
        self.build_counters()
        if self._relaunch:
            self._report["error"] = "skipped"
        save_json(self._report, self._report_path + "/report.json")
        if self._relaunch:
            self.backup_outputs()
        self._build_report = False

    def build_performance(self):

        self._report["performance"] = {}
        perflist = []
        if "performance" in self._execution:
            perflist = self._execution["performance"]
        if len(perflist) == 0:
            perflist = [self._name]

        for name in perflist:

            try:
                logger.debug("Opening performance file")
                performance_table = []

                with (open(self._report_path + "/" + name + "-performance.csv", newline='') as csvfile):
                    logger.debug("Processing performance file")
                    performance = csv.DictReader(csvfile, delimiter=',', skipinitialspace=True)
                    for row in performance:
                        rrow = {}
                        for r in row:
                            try:
                                rrow[r] = float(row[r])
                            except:
                                rrow[r] = row[r]
                            try:
                                rrow[r] = int(row[r])
                            except:
                                rrow[r] = row[r]
                        performance_table.append(rrow)
                    self._report["performance"][name] = performance_table

            except:
                logger.error("Performance building failed")
                self._report["performance"][name] = []

    def build_counters(self):
        try:
            logger.debug("Opening bandwidth file")
            with open(self._report_path + "/infiniband.out", newline='') as bandwidth:
                logger.debug("Processing bandwidth file")
                type = "InfiniBand"
                rcv = "port_rcv_data"
                xmit = "port_xmit_data"
                counters = {type: []}
                counters[type].append({"name": rcv, "date": self._start, "value": int(bandwidth.readline()), "unit": "1/s"})
                counters[type].append({"name": xmit, "date": self._start, "value": int(bandwidth.readline()), "unit": "1/s"})
                counters[type].append({"name": rcv, "date": self._end, "value": int(bandwidth.readline()), "unit": "1/s"})
                counters[type].append({"name": xmit, "date": self._end, "value": int(bandwidth.readline()), "unit": "1/s"})
                self._report["counters"] = counters
        except:
            logger.error("Counter building failed")
            self._report["counters"] = []

    def retry(self):
        if not self._relaunch:
            self._retry += 1
            self._relaunch = self._retry < self._max_retry

    def compute_times(self):
        self._start = 0
        self._end = 0
        no_timeout = True
        try:
            t = read_text_file(self._report_path + "/" + "time.out").split("\n")
        except:
            self._report["jobTime"] = "none"
            no_timeout = False
            return no_timeout
        i = 0
        for field in "initTime", "alyaTime", "postprocessTime", "validationTime":
            self._report[field] = duration2str(0, 0)
        for field in "initTime", "alyaTime", "postprocessTime", "validationTime":
            try:
                start = int(t[i])
                if self._start == 0:
                    self._start = start
                j = i + 1
                end = int(t[j])
                self._end = max(self._end, end)
                self._report[field] = duration2str(start, end)
                i = j
            except:
                self._report[field] = "timeout"
                no_timeout = False
                break
        try:
            self._report["jobTime"] = duration2str(int(t[0]), int(t[i]))
        except:
            self._report["jobTime"] = "none"
            no_timeout = False
        return no_timeout

    def build_failed_report(self, error):
        self._report = {}
        self._report["name"] = self._name
        self._report["mpi"] = int(self._mpi)
        self._report["openmp"] = int(self._openmp)
        self._report["build"] = self._build.get_build_id()
        self._report["files"] = []
        self._report["status"] = False
        self._report["error"] = error
        self._report["env"] = {}
        save_json(self._report, self._report_path + "/report.json")

    def get_report(self):
        return self._report

    def create_empty_outputs(self):
        open(self._report_path + "/test.out", 'a+').close()
        open(self._report_path + "/test.err", 'a+').close()
        open(self._report_path + "/alya.out", 'a+').close()
        open(self._report_path + "/alya.err", 'a+').close()
        open(self._report_path + "/post.out", 'a+').close()
        open(self._report_path + "/post.err", 'a+').close()
        open(self._report_path + "/time.out", 'a+').close()

    def backup_outputs(self):
        command("mv " + self._report_path + "/report.json " + self._report_path + "/report.json.bak." + str(self._retry))
        command("mv " + self._report_path + "/test.out " + self._report_path + "/test.out.bak." + str(self._retry))
        command("mv " + self._report_path + "/test.err " + self._report_path + "/test.err.bak." + str(self._retry))
        command("mv " + self._report_path + "/alya.out " + self._report_path + "/alya.out.bak." + str(self._retry))
        command("mv " + self._report_path + "/alya.err " + self._report_path + "/alya.err.bak." + str(self._retry))
        command("mv " + self._report_path + "/post.out " + self._report_path + "/post.out.bak." + str(self._retry))
        command("mv " + self._report_path + "/post.err " + self._report_path + "/post.err.bak." + str(self._retry))
        command("mv " + self._report_path + "/time.out " + self._report_path + "/time.out.bak." + str(self._retry))

    def get_path(self):
        return self._report_path

    def get_id(self):
        return self._id

    def get_job_id(self):
        return self._job_id

    def get_relaunch(self):
        return self._relaunch

    def get_mergeable(self):
        return self._mergeable

    def get_tasks(self):
        openmp = max(1, int(self._openmp))
        return int(self._mpi) * openmp

    def get_timeout(self):
        return self._timeout

    def get_script(self):
        return self._script

    def set_job_id(self, job_id):
        self._job_id = job_id

    def update_status(self, launched=None, valid=None, terminated=None):
        if launched is not None:
            self._job_launched = launched
        if valid is not None:
            self._job_valid = valid
        if terminated is not None:
            self._job_terminated = terminated

    def get_merged(self):
        return self._merged

    def set_merged(self, merged):
        self._merged = merged
