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



from ..utils.utils import *
from ..utils.message import *
from ..utils.log import *
from ..definitions import *
from .test import Test

logger = logging.getLogger(logging_context)

alya_tests = "alya/tests"


class Tester:

    def __init__(self, systemManager, hash, job, ssh, config, revision, directories=["."], test_list=[]):
        self._systemManager = systemManager
        self._hash = hash
        self._job = job
        self._ssh = ssh
        self._revision = revision
        self._config = config
        self._start_time = time.time()
        self._json = []
        self._tests = []
        self._directories = directories
        if len(self._directories) == 0:
            self._directories = ["."]
        self._test_list = test_list
        self._status = True
        self._failed = 0
        self._relaunch = False
        self._empty = False
        self._test_paths = open_json(test_file)["paths"]
        self._remote_dir = remote_test_dir
        self._report_dir = test_report_dir
        self._instancemerger = {}
        self._instancemerger_launched = []
        self._merge = False
        if "merge" in self._config:
            self._merge = self._config["merge"]

    def send_py(self):
        jump()
        print("Uploading python scripts...")
        for system in self._systemManager.get_systems():
            self._ssh.rmdir(system=system, path=remote_ts_dir, server_path=True, critical=True)
            self._ssh.rsync_send(system=system, local="src-remote/", remote=remote_ts_dir, options="-L", delete=True, server_path=True, critical=True)
        print_line()

    def send_tests(self):
        for system in self._systemManager.get_systems():
            self._ssh.mkdir(system=system, path=self._remote_dir, server_path=True, critical=True)
            if os.path.isdir(self._report_dir) and os.path.exists(self._report_dir):
                self._ssh.scp_send(system=system, local=self._report_dir+"/*", remote=self._remote_dir+"/", server_path=True, r=True, critical=True)
            else:
                print("No tests are compatible with the builds you have selected. Skipping...")

    def clean_remote(self, fake=False):
        if fake:
            return
        jump()
        print("Cleaning the remote test directory...")
        for system in self._systemManager.get_systems():
            self._ssh.rmdir(system=system, path=self._remote_dir, server_path=True, critical=True)
        print_line()

    def clean_tests(self):
        command("rm -fr " + self._report_dir)

    def add_tests(self):
        self.clean_tests()
        jump()
        print("Adding tests:\n")
        for dir in self._directories:
            self.find_tests(dir, self._test_list)
        for j in self._json:
            self._tests.append(self.set_test(j))
        print_line()

    def prepare_tests(self, build, fake=False):
        instance = None
        if self._merge and build.get_merge():
            self._instancemerger[build.get_build_id()] = {}
            instance = self._instancemerger[build.get_build_id()]
        for test in self._tests:
            test.prepare(build, instance, fake)
        if build.get_build_id() in self._instancemerger:
            for threads in self._instancemerger[build.get_build_id()]:
                for instancemerger in self._instancemerger[build.get_build_id()][threads]:
                    if not instancemerger.is_empty():
                        instancemerger.initialize()

    def run_tests(self, terraform, build, _print=True):
        i = 0
        jump()
        while not terraform.get_platform_state(self._ssh, build.get_system(), build.get_platform()):
            time.sleep(60)
        for test in self._tests:
            i += test.run(build)
            if _print:
                print("\033[1A", end='')
                print(str(i) + " unmerged test jobs")
        if build.get_build_id() in self._instancemerger:
            print()
            i = 1
            for threads in self._instancemerger[build.get_build_id()]:
                for instancemerger in self._instancemerger[build.get_build_id()][threads]:
                    if not instancemerger.is_empty():
                        instancemerger.run()
                        self._instancemerger_launched.append(instancemerger)
                        if _print:
                            print("\033[1A", end='')
                            print(str(i) + " merged test jobs")
                            i += 1

    def check_tests(self, _print=True, noback=False):
        finished = True

        #Merged jobs
        merged_jobs = {}
        merged_jobs["scheduled"] = 0
        merged_jobs["terminating"] = 0
        merged_jobs["pending"] = 0
        merged_jobs["running"] = 0
        merged_jobs["finished"] = 0
        merged_jobs["unknown"] = 0
        merged_jobs["total"] = 0
        for instancemerger in self._instancemerger_launched:
            status = instancemerger.check_job()
            if "Scheduled" in status:
                merged_jobs["scheduled"] += 1
                merged_jobs["total"] += 1
            elif "Terminating" in status:
                merged_jobs["terminating"] += 1
                merged_jobs["total"] += 1
            elif "Pending" in status:
                merged_jobs["pending"] += 1
                merged_jobs["total"] += 1
            elif "Running" in status:
                merged_jobs["running"] += 1
                merged_jobs["total"] += 1
            elif "Finished" in status:
                merged_jobs["finished"] += 1
                merged_jobs["total"] += 1
            else:
                merged_jobs["unknown"] += 1
                merged_jobs["total"] += 1
            if merged_jobs["finished"] != merged_jobs["total"]:
                finished = False

        #Normal jobs
        jobs = {}
        jobs["scheduled"] = 0
        jobs["finished"] = 0
        jobs["running"] = 0
        jobs["terminating"] = 0
        jobs["pending"] = 0
        jobs["total"] = 0
        jobs["unknown"] = 0
        for test in self._tests:
            test_jobs = test.check_jobs()
            jobs["scheduled"] += test_jobs["scheduled"]
            jobs["finished"] += test_jobs["finished"]
            jobs["running"] += test_jobs["running"]
            jobs["terminating"] += test_jobs["terminating"]
            jobs["pending"] += test_jobs["pending"]
            jobs["total"] += test_jobs["total"]
            jobs["unknown"] += test_jobs["unknown"]
            if test_jobs["finished"] != test_jobs["total"]:
                finished = False

        #Grouping normal + merged jobs
        jobs["scheduled"] += merged_jobs["scheduled"]
        jobs["finished"] += merged_jobs["finished"]
        jobs["running"] += merged_jobs["running"]
        jobs["terminating"] += merged_jobs["terminating"]
        jobs["pending"] += merged_jobs["pending"]
        jobs["total"] += merged_jobs["total"]
        jobs["unknown"] += merged_jobs["unknown"]
        self._empty = jobs["total"] == 0
        if _print:
            print('{:<13}{:>9}'.format("Total:",      jobs["total"]))
            print('{:<13}{:>9}'.format("Finished:",   jobs["finished"]))
            print('{:<13}{:>9}'.format("Terminating:",jobs["terminating"]))
            print('{:<13}{:>9}'.format("Running:",    jobs["running"]))
            print('{:<13}{:>9}'.format("Pending:",    jobs["pending"]))
            print('{:<13}{:>9}'.format("Scheduled:",  jobs["scheduled"]))
            print('{:<13}{:>9}'.format("Unknown:",    jobs["unknown"]))
            print("Elapsed time: ", int((time.time() - self._start_time) / 60), "minutes", "              ")
        if not noback and _print and not finished:
            print("\033[8A", end='')
        return finished

    def wait_tests(self, oneprint=False):
        jump()
        print("Waiting for tests to finish and getting reports...")
        jump()
        _print = True
        while not self.check_tests(_print):
            time.sleep(1)
            if oneprint:
                _print = False
        print_line()

    def find_tests(self, directory, tests=[]):
        for p in self._test_paths:
            print("Looking into: " + p + "/" + directory)
            if os.path.isdir(p):
                for r, d, f in os.walk(p + "/" + directory):
                    for file in f:
                        if file.endswith(".json"):
                            j = os.path.join(r, file)
                            jt = j.replace("//", "/").replace(p, "").split("/")[-1].split(".json")[0]
                            if (j not in self._json) and (len(tests) == 0 or jt in tests):
                                status = "Unknown"
                                res = self.valid(j)
                                if res == 0:
                                    status = "OK"
                                    self._json.append(j)
                                elif res == 1:
                                    status = "Disabled"
                                else:
                                    status = "Invalid"
                                ch = - min(len(jt), 38)
                                print('{:<42}{:>9}'.format("- " + jt[ch:] + ": ", status))

    def set_test(self, json_file):
        return Test(self._systemManager,
                    self._hash, self._job, self._ssh, json_file, self._config, self._report_dir, self._remote_dir)

    def valid(self, file):
        directory = ""
        try:
            directory = file.rsplit('/', 1)[0]  # Remove .json from name
        except:
            print("Error: cannot parse directory name")
            return 2
        try:
            f = open_json(file)
        except:
            print("Error: cannot open file")
            return 2
        else:
            fields = ["authors", "name", "comparisons", "description", "executions", "postprocess"]
            for field in fields:
                try:
                    f[field]
                except:
                    print("Error: missing field: " + field)
                    return 2
        for execution in f["executions"]:
            if "mpi" not in execution:
                print("Missing mpi field in execution")
                return 2
        if "enabled" in f:
            if not f["enabled"]:
                return 1
        if not f["name"] in directory:
            print("Error: incorrect name test: " + f["name"])
            return 2
        if not os.path.isdir(directory):
            print("Error: directory does not exist: " + directory)
            return 2
        return 0

    def build_report(self, fake=False):
        jump()
        has_been_relaunched = self._relaunch
        self._relaunch = False
        print("Building test report")
        self._status = True
        self._failed = 0
        report = {}
        command("mkdir -p " + self._report_dir)
        self._ssh.async_wait()
        if not has_been_relaunched and not self._empty:
            for system in self._systemManager.get_systems():
                if not self._ssh.rsync_get(system=system,
                                           remote=self._remote_dir + "/*",
                                           local=self._report_dir + "/",
                                           options='-m --include="*/" --include="report.json" --include="*.out" --include="*.err" --exclude="*"',
                                           server_path=True):
                    print("Timeout! Try again!")
                    if not self._ssh.rsync_get(system=system,
                                               remote=self._remote_dir + "/*",
                                               local=self._report_dir + "/",
                                               options='-m --include="*/" --include="report.json" --include="*.out" --include="*.err" --exclude="*"',
                                               server_path=True):
                        print("Second timeout! Leaving!")
                        raise Exception
        for t in self._tests:
            t.build_report(fake=fake, download_report=has_been_relaunched)
            report[t.get_name()] = t.get_report()
            if not report[t.get_name()]["status"]:
                self._failed += 1
            self._status = report[t.get_name()]["status"] and self._status
            if t.get_relaunch():
                self._relaunch = True
        f = self._report_dir+"/tests.json"
        save_json(report, f)
        json2js("tests", f)
        print_line()
        return self._status

    def get_failed(self):
        return self._failed

    def get_total(self):
        return len(self._tests)

    def get_relaunch(self):
        return self._relaunch

