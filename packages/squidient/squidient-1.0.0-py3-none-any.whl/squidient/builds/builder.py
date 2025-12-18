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
import sys

from ..utils.utils import *
from ..terraform.terraform import *
from ..git import Git
from .executablebuild import ExecutableBuild
import time

from ..definitions import *

logger = logging.getLogger(logging_context)


class Builder:

    def __init__(self, systemManager, hash, job, ssh, config, password=""):
        self._systemManager = systemManager
        self._hash = hash
        self._alya_repository = None
        self._config = config
        self._builds = {}
        self._start_time = time.time()
        self._finished_builds = {}
        self._pending_builds = {}
        self._gotten_builds = {}
        self._unlaunched_builds = {}
        self._platform_ready = {}
        self._ssh = ssh
        self._job = job
        self._password = password
        self._build_list = {}
        self.set_build_list()
        self._report_dir = ""
        self.set_report_dir()
        self._p = ""

    def cd_push(self, path):
        """
        Switch to git repository
        """
        self._p = os.getcwd()

        if not os.path.isdir(path):
            logger.error(path + " does not exist")
            return False
        try:
            os.chdir(path)
        except:
            logger.error("Changing directory to " + path + " failed")
            return False
        return True

    def cd_pop(self):
        try:
            os.chdir(self._p)
        except:
            logger.error("Changing directory back failed")
            raise RuntimeError("An internal error happened...")

    def set_build_list(self):
        self._build_list = self._config["staging"]["builds"]

    def set_report_dir(self):
        self._report_dir = build_report_dir

    def clean_builds(self):
        command("rm -fr " + build_report_dir)

    def run_builds(self, terraform):
        self.send_alya()
        self.clean_builds()
        sorted_builds = {}
        for system in self._systemManager.get_systems():
            sorted_builds[system] = {}
            for platform in self._systemManager.get_platforms(system):
                sorted_builds[system][platform] = []
        for b in self._build_list:
            bui = self.init_build(b)
            self._unlaunched_builds[b] = bui
            sorted_builds[bui.get_system()][bui.get_platform()].append(b)
        while len(self._unlaunched_builds) > 0:
            for system in self._systemManager.get_systems():
                for platform in self._systemManager.get_platforms(system):
                    if terraform.get_platform_state(self._ssh, system, platform):
                        for b in sorted_builds[system][platform]:
                            self.run_build(self._unlaunched_builds[b])
                            if self._unlaunched_builds[b].get_job_id() != -1:
                                self._builds[b] = self._unlaunched_builds[b]
                                del self._unlaunched_builds[b]
                            else:
                                raise Exception
                        sorted_builds[system][platform] = []
            time.sleep(60)
        print_line()

    def terminate_builds(self):
        finished = False
        jump()
        print("Waiting for builds to finish:")
        print_line()
        while not finished:
            finished = self.check_builds()
        return self.get_status()

    def get_status(self):
        for b in self._finished_builds:
            if not self._finished_builds[b]:
                return False
        return True

    def get_failed(self):
        failed = 0
        for b in self._finished_builds:
            if not self._finished_builds[b]:
                failed += 1
        return failed

    def get_total(self):
        return len(self._builds)

    def next_valid_build(self, _print=True, oneprint=False, stop_on_error=False):
        __print = _print
        while len(self._pending_builds) == 0:
            if self.check_builds(__print, __print, False):
                if self.get_failed() > 1 and stop_on_error:
                    return None
                break
            __print = __print and not oneprint
        build = None
        for b in self._pending_builds:
            build = b
            break
        if build is not None:
            self._pending_builds.pop(build)
            return self._builds[build]
        else:
            return None

    def get_build(self):
        self.check_builds(False, False, False)
        if len(self._pending_builds) > 0:
            for build in self._pending_builds:
                if build not in self._gotten_builds:
                    self._gotten_builds[build] = self._pending_builds[build]
                    return self._builds[build]
        for build in self._builds:
            if build not in self._gotten_builds:
                self._gotten_builds[build] = True
                return self._builds[build]
        return None

    def ready(self, build):
        self.check_builds(False, False, False)
        if build.get_build_id() in self._pending_builds:
            self._pending_builds.pop(build.get_build_id())
            return True
        return False

    def build_report(self):
        jump()
        print("Building build report")
        print_line()
        report = {}
        for b in self._builds:
            if b in self._finished_builds:
                self._builds[b].build_report()
                report[b] = self._builds[b].get_report()
        f = self._report_dir+"/builds.json"
        save_json(report, f)
        json2js("builds", f)

    def check_build_job_status(self, build):
        status = self._builds[build].check_job_status()
        if "Finished" in status:
            finished = True
        else:
            finished = False
        return {"finished": finished, "status": status}

    def check_build_status(self, build):
        status = self._builds[build].check_build_status()
        return status

    def check_builds(self, _print=True, minutes=True, back=True):
        count = len(self._builds) + 1
        if not minutes:
            count -= 1
        count = str(count)
        check = True
        time.sleep(1)
        status = {}
        one_success = False
        for b in self._builds:
            if b in self._finished_builds:
                status["finished"] = True
                test = True
                if self._finished_builds[b]:
                    status["status"] = "Success"
                else:
                    status["status"] = "Failed"
            else:
                status = self.check_build_job_status(b)
                if status["finished"]:
                    test = True
                    if self.check_build_status(b):
                        status["status"] = "Success"
                        self._finished_builds[b] = True
                        self._pending_builds[b] = True
                        one_success = not back
                    else:
                        status["status"] = "Failed"
                        self._finished_builds[b] = False
                    self._builds[b].build_report()
                else:
                    test = False
            check = check and test
            if _print:
                print('{:<35}{:>16}'.format("- " + b[:31] + ": ", status["status"]))
        if _print and minutes:
            print("Elapsed time: ", int((time.time() - self._start_time) / 60), "minutes")
        if (not check) and _print and not one_success:
            print("\033[" + count + "A", end='')
        time.sleep(1)
        return check

    def get_alya(self, fetch=True, force_https=False):
        jump()
        self._alya_repository = Git(git_ssh=self._config["alyaGitRepository"]["ssh"],
                                    git_https=self._config["alyaGitRepository"]["https"],
                                    user=self._config["alyaGitRepository"]["user"],
                                    branch=self._config["alyaGitRepository"]["branch"],
                                    dir="alya",
                                    password=self._password,
                                    force_https=force_https)
        if fetch:
            print("Cloning/Updating the alya git repository...")
            self._alya_repository.clone_or_update_tests()
            print_line()
        self._revision = self._alya_repository.revision_short()
        self._revision_long = self._alya_repository.revision_long()
        return self._alya_repository

    def download_alamak(self, user="", token=""):
        jump()
        if self._config["alamak"]["enable"]:
            print("Cloning alamak")
            self.cd_push(self._config["alamak"]["path"])
            critical_command("./alamak.sh --clean")
            if self._config["alamak"]["revision"] is not None:
                ref = "--revision " + self._config["alamak"]["revision"]
            else:
                ref = "--branch " + self._config["alamak"]["branch"]
            alamak_command = ""
            if user != "" and token != "":
                alamak_command = "./alamak.sh --https " + ref + " --user " + user + " --token " + token
            else:
                alamak_command = "./alamak.sh --ssh " + ref
            try:
                critical_command(alamak_command, silent=True)
            except:
                print("The cloning of alamak has failed. Showing the error and terminating...")
                command("./alamak.sh --clean")
                print(command(alamak_command, output=True, silent=True))
                raise Exception
            self.cd_pop()
            print_line()

    def get_alya_repository(self):
        return self._alya_repository

    def send_alya(self):
        jump()
        for system in self._systemManager.get_systems():
            print("System: " + system)
            print("Cleaning the remote build directory...")
            self._ssh.rmdir(system=system, path=remote_bin_dir, server_path=True)
            if self._config["clean"]:
                self._ssh.rmdir(system=system, path=remote_build_dir, server_path=True)
            self._ssh.rmdir(system=system, path=remote_cc_dir, server_path=True)
            #self._ssh.ssh(system=system, cmd="rm " + remote_cc_dir + "/*/*.dyn", server_path=True)
            print("Creating the remote build directory infrastructure...")
            self._ssh.mkdir(system=system, path=remote_bin_dir, server_path=True)
            self._ssh.mkdir(system=system, path=remote_build_dir, server_path=True)
            self._ssh.mkdir(system=system, path=remote_cc_dir, server_path=True)
            print("Uploading alya...")
            self._ssh.rsync_send(system=system, local=alya_dir, options="--exclude .git/", delete=True, server_path=True, critical=True)
        print_line()

    def create_build(self, build):
        return ExecutableBuild(systemManager=self._systemManager, hash=self._hash, build_id=build, job=self._job, ssh=self._ssh,
                               config=self._config, report_directory=self._report_dir)

    def init_build(self, build):
        jump()
        print("Build: " + build)
        b = self.create_build(build)
        print("\tGenerating alya configuration file...")
        b.generate_configuration()
        print("\tGenerating job file...")
        b.generate_job()
        print("\tUploading files...")
        b.send_files()
        return b

    def run_build(self, b):
        time.sleep(5)
        print("\tSubmitting job...")
        job_id = b.launch_job()
        if job_id == -1:
            print("\tJob submission has failed!")
        else:
            print("\tJob id: " + str(job_id))

    def get_builds(self):
        return self._builds

    def get_alya_revision(self):
        return self._revision

    def get_alya_revision_long(self):
        return self._revision_long
