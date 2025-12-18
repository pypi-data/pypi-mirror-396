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


from ..staging.staging import *
from ..builds.benchmarkbuilder import *
from ..testing.benchmarktester import *
from ..reports.monitorreport import *
from .monitordb import *

logger = logging.getLogger(logging_context)


class Monitor(Staging):

    def banner(self):
        monitorbanner()

    def init_report(self):
        self._report = MonitorReport(self._config["tag"])
        self._report.valid(True)

    def all(self, terraform):
        low_disk_usage = self._config["benchmarks"]["lowDiskUsage"]
        self._db = MonitorDB(config=self._config, password=self._arguments.get_db_password(), enable=self._enable)
        self._db.connect()
        self._db.initialize_tables()
        if self._enable:
            print_line()
        self._builder = BenchmarkBuilder(
            systemManager=self._systemManager,
            hash=self._hash,
            job=self._job,
            ssh=self._ssh,
            config=self._config,
            db=self._db,
            password=self._password)
        self._builder.get_alya(force_https=self._force_https)
        self._builder.download_alamak(self._arguments.get_alamak_user(), self._arguments.get_alamak_token())
        self._db.start_session("alya", self._builder.get_alya_revision_long(), self._builder.get_alya_revision())
        self._password = self._builder.get_alya_repository().get_password()
        self._report.clean()
        self._report.write_alya_revision(self._builder.get_alya_revision())
        self._tester = BenchmarkTester(systemManager=self._systemManager,
                                       hash=self._hash,
                                       job=self._job,
                                       ssh=self._ssh,
                                       config=self._config,
                                       benchmarks=self._benchmarks,
                                       revision=self._report.get_alya_revision(),
                                       db=self._db,
                                       directories=self._test_directories,
                                       test_list=self._test_list)
        self._builder.run_builds(terraform)
        self._tester.clean_remote()
        if low_disk_usage:
            self._tester.get_and_send_benchmarks()
        else:
            self._tester.get_benchmarks()
            self._tester.send_benchmarks()
        self._tester.add_tests()
        self._tester.send_py()
        jump()
        b = self._builder.get_build()
        while b is not None:
            print("Preparing all the benchmarks for build " + b.get_build_id())
            self._tester.prepare_tests(b)
            b = self._builder.get_build()
        jump()
        print("Sending tests...")
        self._tester.send_tests()
        jump()
        print("Waiting for available build...")
        jump()
        b = self._builder.next_valid_build(_print=True, oneprint=self._gitlab, stop_on_error=False)
        while b is not None:
            jump()
            print("Running all the tests for build " + b.get_build_id())
            self._tester.run_tests(terraform, b, not self._gitlab)
            jump()
            print("Checking test jobs...")
            self._tester.check_tests(_print=True, noback=True)
            jump()
            print("Waiting for available build...")
            jump()
            b = self._builder.next_valid_build(_print=True, oneprint=self._gitlab, stop_on_error=False)
        self._builder.build_report()
        self._report.write_builds(self._builder.get_status(), self._builder.get_total(), self._builder.get_failed())
        self._tester.wait_tests(oneprint=self._gitlab)
        status = self._tester.build_report()
        self._report.write_tests(status, self._tester.get_total(), self._tester.get_failed())
        jump()
        self._db.end_session()
        self._report.valid(True)
        print("Full monitor has been executed!")
        print_line()
        self.end()

    def build(self, terraform):
        self._db = MonitorDB(self._config, enable=False)
        self._builder = BenchmarkBuilder(systemManager=self._systemManager,
                                         hash=self._hash,
                                         job=self._job,
                                         ssh=self._ssh,
                                         config=self._config,
                                         db=self._db,
                                         password=self._password)
        self._builder.get_alya(force_https=self._force_https)
        self._builder.download_alamak(self._arguments.get_alamak_user(), self._arguments.get_alamak_token())
        self._builder.run_builds(terraform)
        status = self._builder.terminate_builds()
        self._builder.build_report()
        self._report.clean()
        self._report.write_alya_revision(self._builder.get_alya_revision())
        self._report.write_builds(self._builder.get_status(), self._builder.get_total(), self._builder.get_failed())
        jump()
        if not status:
            print("Some of your builds have failed!")
        else:
            print("All your builds have succeeded!")
        print("Open file://web/bb.html with your navigator to get more details!")
        print_line()
        self.end()
        if not status:
            exit(1)

    def test(self, terraform, fake=False):
        self._db = MonitorDB(self._config, enable=False)
        self._tester = BenchmarkTester(systemManager=self._systemManager,
                                       hash=self._hash,
                                       job=self._job,
                                       ssh=self._ssh,
                                       config=self._config,
                                       benchmarks=self._benchmarks,
                                       revision=self._report.get_alya_revision(),
                                       db=self._db,
                                       directories=self._test_directories,
                                       test_list=self._test_list)
        self._tester.clean_remote(fake)
        self._tester.get_benchmarks(fake)
        self._tester.add_tests()
        if not fake:
            self._tester.send_py()
        jump()
        if not fake:
            print("Preparing tests:")
        else:
            print("Retrieving tests:")
        jump()
        builds = []
        for build in self._config["benchmarks"]["builds"]:
            print("- Build: " + build)
            builds.append(BenchmarkBuild(systemManager=self._systemManager,
                                         hash=self._hash,
                                         build_id=build,
                                         job=self._job,
                                         ssh=self._ssh,
                                         config=self._config,
                                         report_directory=benchmark_build_report_dir,
                                         db=self._db))
            self._tester.prepare_tests(builds[-1], fake)
        if not fake:
            print("Sending tests...")
            self._tester.send_benchmarks()
            self._tester.send_tests()
            jump()
            print("Running tests:")
            jump()
            for build in builds:
                print("- Running all the tests for build " + build.get_build_id())
                self._tester.run_tests(terraform, build)
                jump()
                self._tester.check_tests(_print=True, noback=True)
                jump()
            print_line()
            self._tester.wait_tests()
        status = self._tester.build_report(fake)
        self._report.write_tests(status, self._tester.get_total(), self._tester.get_failed())
        jump()
        if not status:
            print("Some of your tests have failed!")
        else:
            print("All your tests have succeeded!")
        print("Open file://web/btests.html with your navigator to get more details!")
        print_line()
        self.end()
        if not status:
            exit(1)
