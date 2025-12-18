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



import collections
import hashlib
import os.path

from ..builds.executablebuild import ExecutableBuild
from ..builds.builder import Builder
from ..builds.predefinedbuild import PredefinedBuild
from ..codecoverage.intelcodecoverage import *
from ..codecoverage.gcovrcodecoverage import *
from ..git import *
from ..connection.job import *
from ..utils.arguments import Arguments
from ..utils.lock import *
from ..reports.report import Report
from ..connection.ssh import *
from ..testing.tester import Tester
from ..utils.watchdog import *
from ..systems.systemmanager import *
from ..definitions import *

logger = logging.getLogger(logging_context)


class Staging:

    def __init__(self, arguments, destroy_terraform=False):
        self._arguments = arguments
        self._test_list = arguments.get_test_list()
        self._test_directories = arguments.get_test_directories()
        self._generic_arguments = arguments.get_generic_arg()
        self._gitlab = arguments.get_gitlab()
        self._config = open_critical_json(config_file)
        self._benchmarks = open_critical_json(benchmark_file)
        self._builder = None
        self._tester = None
        self._cc = None
        self._systemManager = None
        self._ssh = None
        self._job = None
        self._report = None
        self._password = ""
        self._force_https = False
        self._valid = True
        self._pid = os.getpid()
        self._watchdog = None
        self._lock = None
        self._hash = ""
        self._db = None
        self._enable = False
        self._destroy_terraform = destroy_terraform



    def init(self):
        self.banner()
        self.check_configuration_status()
        key = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self._hash = (hashlib.md5(key.encode())).hexdigest()
        self._systemManager = SystemManager(self._config)
        self._ssh = SSH(self._systemManager, self._config)
        self._job = Job(self._systemManager, self._ssh, self._hash)
        self._lock = Lock(self._ssh)
        self.init_valid()
        self.init_report()
        self.init_watchdog()
        self._enable = self._config["db"]["enable"]

    def banner(self):
        stagingbanner()

    def end(self):
        self.rm_lock()

    def lock(self, terraform):
        jump()
        print("Locking squidient...")
        if self._lock.get_local_lock():
            print("squidient is already running in this directory, or has terminated without removing the lock file")
            print("If you want to run a new squidient instance, clone squidient in another directory and launch it from there")
            print("If you want to clean the lock file, remove manually " + lock_file)
            raise Exception
        if not self._lock.set_local_lock():
            print("Could not create the lock file")
            print("squidient is maybe already running in this directory, or has terminated without removing the lock file")
            print("Check also your available disk space")
            print("If you want to run squidient, clone the squidient in another directory and launch it from there")
            print("If you want to clean the lock file, remove manually " + lock_file)
            raise Exception
        for system in self._systemManager.get_systems():
            if self._lock.get_remote_lock(system):
                print("squidient  is already running in the same server path, or has terminated without removing the lock file")
                print("If you want to run a new squidient instance, configure another server path with ./configure -p")
                print("If you want to clean the lock file, remove manually " +
                      self._systemManager.get_system(system).get_path() + "/" + lock_file + " on the " + system + " system")
                self._lock.rm_local_lock()
                raise Exception
        for system in self._systemManager.get_systems():
            terraform.wait_cloud_init(self._ssh, system)
            if not self._lock.set_remote_lock(system):
                print("Could not create the lock file on marenostrum")
                print("squidient is maybe already running in the same server path, or has terminated without removing the lock file")
                print("Check also your available disk space on the " + system + " system")
                print("If you want to run a new squidient instance, configure another server path with ./configure -p")
                print("If you want to clean the lock file, remove manually " +
                      self._systemManager.get_system(system).get_path() + "/" + lock_file + " on the " + system + " and run squidient again")
                self._lock.rm_local_lock()
                raise Exception
        print_line()

    def rm_lock(self):
        status = True
        for system in self._systemManager.get_systems():
            if not self._lock.rm_remote_lock(system):
                print("Could not remove the lock file on marenostrum")
                print("You should remove the lock file manually: " + self._systemManager.get_system(system).get_path() + "/" + lock_file +
                      "on the " + system + " before running squidient again")
                status = False
        if not self._lock.rm_local_lock():
            print("Could not remove the local lock file")
            print("You should remove the lock file manually: " + lock_file + " before running squidient again")
            status = False
        if not status:
            raise Exception

    def build_warning(self):
        if not self._gitlab:
            if len(self._config["staging"]["builds"]) > max_advised_builds:
                jump()
                print("You are currently running squidient with more than " +
                      str(max_advised_builds) + " builds.")
                print("It can last a lot, depending on the load of the system.")
                print("We generally advise to run squidient with fewer builds.")
                answer = ""
                while answer not in ["Y", "N"]:
                    answer = input("Are you sure that you want to continue? [Y/N]\n")
                print_line()
                return answer == "Y"
        return True

    def test_warning(self):
        if not self._gitlab:
            if len(self._config["staging"]["builds"]) > max_advised_builds \
                    and len(self._test_directories) == 0 and len(self._test_list) == 0:
                jump()
                print("You are currently running squidient with more than " +
                      str(max_advised_builds) + " builds and with all the tests.")
                print("It can last a lot, depending on the load of the system.")
                print("We generally advise to run squidient with fewer builds and/or fewer tests.")
                answer = ""
                while answer not in ["Y", "N"]:
                    answer = input("Are you sure that you want to continue? [Y/N]\n")
                print_line()
                return answer == "Y"
        return True

    def init_report(self):
        self._report = Report(self._config["tag"])
        self._report.valid(self._valid)

    def init_valid(self):
        if not self._gitlab:
            self._valid = self._valid and len(self._test_directories) == 0 and len(self._test_list) == 0
            predefined_builds = PredefinedBuild("builds").get_pb()
            self._valid = self._valid and collections.Counter(self._config["staging"]["builds"]) == collections.Counter(predefined_builds["all"])

    def init_watchdog(self):
        if self._gitlab and len(self._arguments.get_gitlab_pipeline()) > 0:
            self._watchdog = Watchdog(self._pid, self._arguments.get_gitlab_token(), self._arguments.get_gitlab_pipeline(), self._config['api'])
            self._watchdog.daemon = True
            self._watchdog.start()

    def check_configuration_status(self):
        jump()
        print("Checking if configure file is up to date...")
        if self._config["fileFormat"] != config_file_format():
            print("Your " + config_file + " version is obsolete! Please configure squidient again.")
            exit(1)
        print_line()

    def clean(self):
        command("rm -fr " + benchmark_build_report_dir)
        command("rm -fr " + benchmark_test_report_dir)
        command("rm -fr " + build_report_dir)
        command("rm -fr " + test_report_dir)
        command("rm -fr " + queue_report_dir)
        command("rm -fr " + cc_report_dir)

    def build(self, terraform):
        self._builder = Builder(
            systemManager=self._systemManager,
            hash=self._hash,
            job=self._job,
            ssh=self._ssh,
            config=self._config,
            password=self._password)
        self._builder.get_alya(force_https=self._force_https)
        self._builder.download_alamak(self._arguments.get_alamak_user(), self._arguments.get_alamak_token())
        self._builder.run_builds(terraform)
        status = self._builder.terminate_builds()
        self._builder.build_report()
        self._report.clean()
        self._report.write_alya_revision(self._builder.get_alya_revision())
        self._report.write_builds(status, self._builder.get_total(), self._builder.get_failed())
        jump()
        if not status:
            print("Some of your builds have failed!")
        else:
            print("All your builds have succeeded!")
        print("Open file://web/builds.html with your navigator to get more details!")
        print_line()
        self.end()
        if not status:
            exit(1)

    def test(self, terraform, fake=False):
        self._tester = Tester(
            systemManager=self._systemManager,
            hash=self._hash,
            job=self._job,
            ssh=self._ssh,
            config=self._config,
            revision=self._report.get_alya_revision(),
            directories=self._test_directories,
            test_list=self._test_list)
        self._tester.clean_remote(fake)
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
        for build in self._config["staging"]["builds"]:
            print("- Build: " + build)
            builds.append(ExecutableBuild(
                systemManager=self._systemManager,
                hash=self._hash,
                build_id=build,
                job=self._job,
                ssh=self._ssh,
                config=self._config,
                report_directory=build_report_dir))
            self._tester.prepare_tests(builds[-1], fake)
        if not fake:
            jump()
            print("Sending tests...")
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
        i = 0
        while self._tester.get_relaunch():
            i += 1
            if i > test_max_retry + 2:
                print("Maximum number of retries exceeded!!!")
                exit(1)
            jump()
            print("Some tests have been relaunched...")
            jump()
            self._tester.wait_tests()
            status = self._tester.build_report()
        self._report.write_tests(status, self._tester.get_total(), self._tester.get_failed())
        jump()
        if not status:
            print("Some of your tests have failed!")
        else:
            print("All your tests have succeeded!")
        print("Open file://web/tests.html with your navigator to get more details!")
        print_line()
        self.end()
        if not status:
            exit(1)

    def cc(self, all=False):
        builds = {}
        clean_cc()
        if not all:
            self._builder = Builder(
                systemManager=self._systemManager,
                hash=self._hash,
                job=self._job,
                ssh=self._ssh,
                config=self._config,
                password=self._password)
            self._builder.get_alya(fetch=False)
            self._builder.download_alamak(self._arguments.get_alamak_user(), self._arguments.get_alamak_token())
            for build in self._config["staging"]["builds"]:
                builds[build] = ExecutableBuild(
                    systemManager=self._systemManager,
                    hash=self._hash,
                    build_id=build,
                    job=self._job,
                    ssh=self._ssh,
                    config=self._config,
                    report_directory=build_report_dir)
        else:
            builds = self._builder.get_builds()
        if self._config["cc"]["tool"] == "intel":
            self._cc = IntelCodeCoverage(
                systemManager=self._systemManager,
                ssh=self._ssh,
                config=self._config,
                revision=self._report.get_alya_revision(),
                alya_repository=self._builder.get_alya_repository(),
                builds=builds)
        elif self._config["cc"]["tool"] == "gcovr":
            self._cc = GcovrCodeCoverage(
                systemManager=self._systemManager,
                ssh=self._ssh,
                config=self._config,
                revision=self._report.get_alya_revision(),
                alya_repository=self._builder.get_alya_repository(),
                builds=builds)
        else:
            if all:
                return
            else:
                print("Code coverage unavailable for the selected tool!")
                self.end()
                raise Exception
        jump()
        if not self._cc.is_cc_runnable():
            if all:
                return
            else:
                print("Code coverage unavailable for the selected builds!")
                self.end()
                exit(1)
        print("Processing code coverage")
        if not self._cc.process():
            if all:
                return
            else:
                self.end()
                raise Exception
        print("Getting code coverage files...")
        self._cc.get_files()
        print_line()
        jump()
        print("Postprocessing code coverage")
        self._cc.postprocess(self._gitlab)
        status = self._cc.build_report()
        self._report.write_cc(self._cc.get_coverage(), self._cc.get_total(), self._cc.get_failed(), self._cc.get_tool())
        jump()
        if all:
            return
        #if not status:
        #    print("Some of your contributions have not been covered! You should add new tests to alya to ensure a full code coverage!")
        #else:
        #    print("All your contributions have been covered!")
        print_line()
        if not all:
            self.end()
        if not status:
            exit(1)

    def all(self, terraform):
        self._builder = Builder(
            systemManager=self._systemManager,
            hash=self._hash,
            job=self._job,
            ssh=self._ssh,
            config=self._config,
            password=self._password)
        self._builder.get_alya(force_https=self._force_https)
        self._builder.download_alamak(self._arguments.get_alamak_user(), self._arguments.get_alamak_token())
        self._password = self._builder.get_alya_repository().get_password()
        self._report.clean()
        self._report.write_alya_revision(self._builder.get_alya_revision())
        self._tester = Tester(
            systemManager=self._systemManager,
            hash=self._hash,
            job=self._job,
            ssh=self._ssh,
            config=self._config,
            revision=self._report.get_alya_revision(),
            directories=self._test_directories,
            test_list=self._test_list)
        self._builder.run_builds(terraform)
        self._tester.clean_remote()
        self._tester.add_tests()
        self._tester.send_py()
        jump()
        b = self._builder.get_build()
        while b is not None:
            print("Preparing all the tests for build " + b.get_build_id())
            self._tester.prepare_tests(b)
            b = self._builder.get_build()
        jump()
        print("Sending tests...")
        self._tester.send_tests()
        print_line()
        jump()
        print("Waiting for available build...")
        jump()
        b = self._builder.next_valid_build(_print=True, oneprint=self._gitlab, stop_on_error=self._gitlab)
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
            b = self._builder.next_valid_build(_print=True, oneprint=self._gitlab, stop_on_error=self._gitlab)
        self._builder.build_report()
        self._report.write_builds(self._builder.get_status(), self._builder.get_total(), self._builder.get_failed())
        if self._builder.get_failed() > 0:
            print("One or several builds have failed.")
            print("Execution will stop.")
            print("Test report will not be generated.")
            print_line()
            self.kill_all()
            jump()
            self.end()
            return
        self._tester.wait_tests(oneprint=self._gitlab)
        status = self._tester.build_report()
        i = 0
        while self._tester.get_relaunch() and status:
            i += 1
            if i > test_max_retry + 2:
                print("Maximum number of retry exceeded!!!")
                break
            jump()
            print("Some tests have been relaunched...")
            jump()
            self._tester.wait_tests(oneprint=self._gitlab)
            status = self._tester.build_report()
        self._report.write_tests(status, self._tester.get_total(), self._tester.get_failed())
        self.cc(True)
        jump()
        self._report.valid(self._valid)
        print("Full staging has been executed!")
        print_line()
        self.end()

    def kill_all(self):
        if self._job is not None:
            self._job.kill_all()

    def keyboard_interrupt(self):
        mega_jump()
        print("Interruption detected!")
        print("All the running jobs are being killed...")
        print_line()
        self.kill_all()
        jump()
        self.end()

    def validate(self):
        if self._report.get_valid():
            exit()
        else:
            exit(1)

    def report_push(self):
        jump()
        print("Push report: ")
        self._ssh.rsync_send("bsc", report_dir, squidient_reports + "/reports-" + self._hash)
        print("To downoad the report: squidient report pull " + self._hash)
        exit()

    def report_pull(self, hash):
        jump()
        print("Pull report " + hash)
        self._ssh.rsync_get("bsc", squidient_reports + "/reports-" + hash + "/" + report_dir + "/", report_dir, delete=True)
        exit()

    def destroy_terraform(self):
        return self._destroy_terraform
