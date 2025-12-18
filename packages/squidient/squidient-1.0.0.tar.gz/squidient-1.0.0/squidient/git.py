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



# -*- coding: utf-8 -*-
import os.path

from .utils.utils import *
import getpass

logger = logging.getLogger(logging_context)


class Git:
    """
    Git repository manager class
    """

    def __init__(self, git_ssh="", git_https="", user="", branch="", dir=".", password="", force_https=False, no_password=False):
        """
        Init
        """
        self._git_ssh = git_ssh
        self._git_https = git_https
        self._user = user
        self._git_https_user_password = ""
        self._branch = branch
        self._dir = dir
        self._path = os.getcwd()
        self._password = password
        self._original_remote = ""
        self._force_https = force_https
        self._https = force_https
        self._no_password = no_password

    def set_https_password(self):
        if not self._no_password:
            if self._git_https_user_password == "":
                if self._password == "":
                    self._password = getpass.getpass(prompt="Enter your password for the HTTPS repository \n" + self._git_https + ":")
                self._git_https_user_password = self._git_https.replace("https://", "https://" + self._user + ":" +
                                                                        percent_encoding(self._password) + "@")
        else:
            self._git_https_user_password = self._git_https

    def cd_push(self):
        """
        Switch to git repository
        """
        if not os.path.isdir(self._path + "/" + self._dir):
            logger.error(self._dir + " does not exist")
            return False
        try:
            os.chdir(self._path + "/" + self._dir)
        except:
            logger.error("Changing directory to " + self._dir + " failed")
            return False
        return True

    def cd_pop(self):
        try:
            os.chdir(self._path)
        except:
            logger.error("Changing directory back failed")
            raise RuntimeError("An internal error happened...")

    def clone_ssh(self):
        self.cd_pop()
        command("rm -fr " + self._path + "/" + self._dir)
        remote = self._git_ssh
        if not command("git clone --recurse-submodules " + remote + " " + self._dir, timeout=3600):
            logger.error("Git repository " + remote + " cannot be cloned")
            return False
        return True

    def clone_https(self):
        self.cd_pop()
        command("rm -fr " + self._path + "/" + self._dir)
        self.set_https_password()
        remote = self._git_https_user_password
        if not command("git clone --recurse-submodules " + remote + " " + self._dir, silent=True, timeout=3600):
            logger.error("Git repository " + remote + " cannot be cloned")
            return False
        self.reset_remote()
        return True

    def test_git(self):
        if not os.path.isfile(self._path + "/" + self._dir + "/.git/config"):
            logger.error(self._dir + " is not a git repository, remove it")
            command("rm -fr " + self._path + "/" + self._dir)
            return False
        return True

    def is_https(self):
        self._https = self._force_https
        if not self._https:
            if self.cd_push():
                git_https = command('git remote get-url origin', output=True).strip()
                self._https = "https://" in git_https
                if self._https:
                    self._git_https = git_https
            self.cd_pop()
        if self._https:
            print("HTTPS mode detected! This mode is not optimal, use it only if SSH is not available!")
        return self._https

    def reset_remote(self, password=""):
        c = False
        if self.cd_push():
            remote = command('git remote get-url origin', output=True).strip()
            if self._original_remote != "" and remote != self._original_remote:
                c = command('git remote set-url origin ' + self._original_remote)
            else:
                c = command('git remote set-url origin ' + self._git_https)
            if password != "":
                command("sed -i 's/" + percent_encoding(password) + "/PASSWORD/g' .git/config", silent=True)
        self.cd_pop()
        return c

    def set_remote(self, remote, password=""):
        c = False
        if self.cd_push():
            self._original_remote = command('git remote get-url origin', output=True).strip()
            c = command('git remote set-url origin ' + remote, silent=True)
            if password != "":
                command("sed -i 's/PASSWORD/" + percent_encoding(password) + "/g' .git/config", silent=True)
        self.cd_pop()
        return c

    def update_common(self):
        if not self.cd_push():
            logger.warning("Git repository is not present")
            return False
        if not command("git fetch --all"):
            logger.warning("Fetching from remote directory failed")
            self.cd_pop()
            return False
        if not command("git pull --all"):
            logger.warning("Pulling from remote directory failed")
            self.cd_pop()
            return False
        if not command("git submodule update --recursive --remote"):
            logger.warning("Updating submodules failed")
            self.cd_pop()
            return False
        return True

    def update_ssh(self):
        if not self.cd_push():
            logger.warning("Git repository is not present")
            self.cd_pop()
            return False
        remote = self._git_ssh
        if not self.set_remote(remote):
            logger.warning("Setting the remote directory failed")
            self.cd_pop()
            return False
        if not self.update_common():
            return False
        self.cd_pop()
        return True

    def update_https(self, ssh=True):
        if not self.cd_push():
            logger.warning("Git repository is not present")
            self.cd_pop()
            return False
        self.set_https_password()
        remote = self._git_https_user_password
        if not self.set_remote(remote, self._password):
            logger.warning("Setting the remote directory failed")
            self.cd_pop()
            return False
        if not self.update_common():
            self.cd_pop()
            return False
        self.cd_pop()
        self.reset_remote(self._password)
        self.cd_pop()
        return True

    def detached(self):
        det = ""
        if self.cd_push():
            det = command("git status", output=True)
        else:
            logger.warning("Git repository is not present")
            self.cd_pop()
            return False
        self.cd_pop()
        return "HEAD" in det

    def branch(self):
        """
           Checkout branch
        """
        if self.cd_push():
            command("git clean -x -f")
            if not command("git checkout " + self._branch):
                logger.error("Cannot checkout branch " + self._branch)
                return False
            command("git reset --hard HEAD")
            command("git clean -x -f")
            command("git rebase")
            if self._https:
                self.set_https_password()
                remote = self._git_https_user_password
                if not self.set_remote(remote, self._password):
                    logger.warning("Setting the remote directory failed")
                    self.cd_pop()
                    return False
            if self.cd_push():
                command("git submodule update --init --recursive")
                command("git submodule update --recursive --remote")
            if self._https:
                self.reset_remote(self._password)
        else:
            logger.warning("Git repository is not present")
            self.cd_pop()
            return False
        self.cd_pop()
        return True

    def clone_or_update_tests(self):
        """
           Clone or update the repository
        """
        #print("Updating the repository")
        self.test_git()
        if not self._force_https:
            if not self.update_ssh():
                logger.info("SSH update failed")
                #print("Update failed, cloning the tests repository")
                if not self.clone_ssh():
                    logger.info("SSH clone failed")
                    raise RuntimeError("Git repository cannot be cloned using the ssh protocol. Change your testsuite repository to https!")
        else:
            if not self.update_https():
                logger.info("HTTPS update failed")
                # print("Update failed, cloning the tests repository")
                if not self.clone_https():
                    logger.info("HTTPS clone failed")
                    raise RuntimeError("Git repository cannot be cloned")
        print("Switching git directory to branch " + self._branch + "...")
        if not self.branch():
            raise RuntimeError("Cannot switch to " + self._branch + " and rebase it!")

    def revision_short(self):
        revision = ""
        if self.cd_push():
            revision = command("git log --pretty=format:'%h' -n 1", output=True).strip()
        self.cd_pop()
        return revision

    def revision_long(self):
        revision = ""
        if self.cd_push():
            revision = command("git rev-parse HEAD", output=True).strip()
        self.cd_pop()
        return revision

    def modified_files(self, commit="master"):
        files = []
        if self._branch == "master" and commit == "master":
            return files
        if self.cd_push():
            files = command("git diff --name-only " + commit, output=True)
        self.cd_pop()
        files = files.split("\n")[:-1]
        return files

    def git_is_up_to_date(self):
        """
           Test if current git repo is obsolete
        """
        if not self.cd_push():
            logger.error("Cannot switch to git repository")
            self.cd_pop()
            raise Exception
        if self.is_https():
            self.set_https_password()
            remote = self._git_https_user_password
            self.set_remote(remote)
        status = command('git remote update')
        if status:
            status = not command('git status | grep pull')
        if self._https:
            self.reset_remote()
        self.cd_pop()
        return status

    def get_password(self):
        return self._password

    def get_https(self):
        return self._https

