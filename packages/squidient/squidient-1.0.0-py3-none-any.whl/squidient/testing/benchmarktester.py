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
from ..definitions import *
from ..git import *
from .tester import Tester
from .benchmarktest import BenchmarkTest

logger = logging.getLogger(logging_context)



class BenchmarkTester(Tester):

    def __init__(self, systemManager, hash, job, ssh, config, benchmarks, revision, db, directories=["."],
                 test_list=[]):

        super().__init__(systemManager, hash, job, ssh, config, revision, directories, test_list)
        self._merge = False
        self._benchmarks = benchmarks
        self._test_list = []
        self._local_dir = benchmark_dir
        self._test_paths = [benchmark_dir]
        self._remote_dir = benchmark_dir
        self._report_dir = benchmark_test_report_dir
        self._source_dir = self._remote_dir + "/.repositories"
        self._db = db

    def get_benchmark(self, benchmark, fake=False):
        b = self._benchmarks[benchmark]
        print("Downloading monitor " + benchmark)
        if "enabled" in b:
            if not b["enabled"]:
                print("Benchmark disabled")
                return False
        if not fake:
            if b["type"] == "git":
                print("Cloning/Updating the git repository")
                g = Git(git_https=b["url"], dir=self._local_dir + "/" + benchmark, force_https=True,
                        branch=b["revision"], no_password=True)
                try:
                    g.clone_or_update_tests()
                except:
                    return False
            elif b["type"] == "ssh":
                if not self._ssh.rsync_get(system=b["host"], remote=b["path"] + "/",
                                           local=self._local_dir + "/" + benchmark, delete=True, critical=False):
                    return False
            else:
                return False
        self._test_list.append(benchmark)
        return True

    def get_benchmarks(self, fake=False):
        jump()
        for benchmark in self._config["benchmarks"]["tests"]:
            if not self.get_benchmark(benchmark, fake):
                continue
        print_line()

    def send_benchmark(self, benchmark):
        print("Uploading monitor " + benchmark)
        for system in self._systemManager.get_systems():
            self._ssh.mkdir(system=system, path=self._source_dir + "/" + self._local_dir, server_path=True)
            self._ssh.rsync_send(system=system,
                                 local=self._local_dir + "/" + benchmark,
                                 remote=self._source_dir + "/" + self._local_dir + "/",
                                 options="--exclude .git/",
                                 server_path=True,
                                 delete=True,
                                 critical=True)

    def send_benchmarks(self):
        jump()
        print("Uploading benchmarks...")
        for system in self._systemManager.get_systems():
            self._ssh.mkdir(system=system, path=self._source_dir, server_path=True)
            self._ssh.rsync_send(system=system,
                                 local=self._local_dir,
                                 remote=self._source_dir + "/",
                                 options="--exclude .git/",
                                 server_path=True,
                                 delete=True,
                                 critical=True)
        print_line()

    def get_and_send_benchmarks(self, fake=False):
        for benchmark in self._config["benchmarks"]["tests"]:
            jump()
            if self.get_benchmark(benchmark, fake):
                self.send_benchmark(benchmark)
                self.clean_benchmark(benchmark)
            print_line()

    def clean_benchmark(self, benchmark):
        command("find " + self._local_dir + "/" + benchmark + " -type f -not -name '*.json' -delete")
        command("rm -fr " + self._local_dir + "/" + benchmark + "/.git")

    def set_test(self, json_file):
        return BenchmarkTest(systemManager=self._systemManager,
                             hash=self._hash,
                             job=self._job,
                             ssh=self._ssh,
                             json_path=json_file,
                             config=self._config,
                             report_dir=self._report_dir,
                             remote_dir=self._remote_dir,
                             source_dir=self._source_dir,
                             db=self._db)

    def build_report(self, fake=False):
        jump()
        self._relaunch = False
        print("Building monitor test report")
        self._status = True
        self._failed = 0
        report = {}
        command("mkdir -p " + self._report_dir)
        self._ssh.async_wait()
        if not self._empty:
            for system in self._systemManager.get_systems():
                if not self._ssh.rsync_get(system=system,
                                           remote=self._remote_dir + "/*",
                                           local=self._report_dir + "/",
                                           options='-m --include="*/" --include="report.json" --include="*.out" --include="*.err" --include="*.csv" --exclude="*"',
                                           server_path=True):
                    print("Timeout! Try again!")
                    if not self._ssh.rsync_get(system=system,
                                               remote=self._remote_dir + "/*",
                                               local=self._report_dir + "/",
                                               options='-m --include="*/" --include="report.json" --include="*.out" --include="*.err" --include="*.csv" --exclude="*"',
                                               server_path=True):
                        print("Second timeout! Leaving!")
                        raise Exception
        for t in self._tests:
            t.build_report(fake)
            report[t.get_name()] = t.get_report()
            if not report[t.get_name()]["status"]:
                self._failed += 1
            self._status = report[t.get_name()]["status"] and self._status
            if t.get_relaunch():
                self._relaunch = True
        f = self._report_dir + "/benchmark_tests.json"
        save_json(report, f)
        json2js("benchmark_tests", f)
        print_line()
        return self._status
