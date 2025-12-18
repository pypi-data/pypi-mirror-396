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
from ..definitions import max_async_threads

logger = logging.getLogger(logging_context)


class SSH:

    def __init__(self, system_manager, config):
        self._system_manager = system_manager
        self._config = config
        self._scp_legacy = config["scp_legacy"]
        self._running_threads = []
        self._running_lock_threads = {}
        self._pending_threads = {}
        self._lock = 0

    def dependency(self, lock, ssh_command, critical=False):
        while len(self._running_threads) + len(self._running_lock_threads) > max_async_threads:
            self.async_wait(soft=True)
            if len(self._running_threads) + len(self._running_lock_threads) > max_async_threads:
                time.sleep(1)
        if lock is None:
            thread = async_command(ssh_command, critical)
            if thread is None:
                raise Exception
            self._running_threads.append(thread)
        else:
            if lock not in self._pending_threads:
                self._pending_threads[lock] = []
            self._pending_threads[lock].append({"ssh": ssh_command, "critical": critical})
            logger.debug("New asynchronous command pending, lock: " + str(lock))
        locks = list(self._pending_threads.keys())
        for lock in locks:
            self.poll(lock)
        return True

    def run_next(self, lock):
        logger.debug("Running next asynchronous command, lock: " + str(lock))
        if lock in self._running_lock_threads:
            self._running_lock_threads.pop(lock)
        if lock in self._pending_threads:
            if len(self._pending_threads[lock]) > 0:
                com = self._pending_threads[lock].pop(0)
                self._running_lock_threads[lock] = async_command(com["ssh"], com["critical"])
                if self._running_lock_threads[lock] is None:
                    raise Exception
                return True
            else:
                self._pending_threads.pop(lock)
                return False

    def poll(self, lock):
        if lock in self._running_lock_threads:
            if async_poll(self._running_lock_threads[lock]):
                logger.debug("Asynchronous command finished, lock: " + str(lock))
                if not async_wait(self._running_lock_threads[lock]):
                    raise Exception
                return not self.run_next(lock)
            logger.debug("Asynchronous command still running, lock: " + str(lock))
            return False
        else:
            return not self.run_next(lock)

    def get_system(self, system, platform):
        if platform is None:
            sys = self._system_manager.get_system(system)
        else:
            sys = self._system_manager.get_platform(system, platform)
        return sys

    def ssh(self, cmd, system, platform=None, quotes="'", critical=False, output=False, server_path=False, path=None, asynchronous=False, lock=None):
        sys = self.get_system(system, platform)
        user = sys.get_user()
        host = sys.get_host()
        key = sys.get_ssh_key()
        authenticity = '-o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" -o "LogLevel=ERROR" '
        if key is not None:
            key = "-i " + key + " "
        else:
            key = ""
        ssh_command = "ssh " + key + authenticity + user + "@" + host
        ssh_path = None
        if path is not None and server_path:
            ssh_path = sys.get_path() + "/" + path
        elif server_path:
            ssh_path = sys.get_path()
        elif path is not None:
            ssh_path = path
        if ssh_path is not None:
            cmd = "cd " + ssh_path + " && " + cmd
        ssh_command += " " + quotes + cmd + quotes
        if asynchronous:
            return self.dependency(lock, ssh_command, critical)
        if critical:
            return critical_command(ssh_command)
        else:
            return command(ssh_command, output=output)

    def rmdir(self, system, path, platform=None, server_path=False, asynchronous=False, lock=None, critical=False):
        sys = self.get_system(system, platform)
        if server_path:
            path = sys.get_path() + "/" + path
        return self.ssh("rm -fr " + path, system, asynchronous=asynchronous, lock=lock, critical=critical)

    def mkdir(self, system, path, platform=None, server_path=False, asynchronous=False, lock=None, critical=False):
        sys = self.get_system(system, platform)
        if server_path:
            path = sys.get_path() + "/" + path
        return self.ssh("mkdir -p " + path, system, asynchronous=asynchronous, lock=lock, critical=critical)

    def rsync_send(self, system, local, remote="", options="", platform=None, critical=False, output=False, delete=False, server_path=False):
        sys = self.get_system(system, platform)
        user = sys.get_user()
        host = sys.get_host()

        scp_command = "rsync -zrhlpgoD "
        if delete:
            scp_command += "--delete "
        scp_command += options
        if options != "":
            scp_command += " "
        s = sys.get_ssh_key()
        if s is None:
            s = ""
        else:
            s = " -i " + "'" + s + "'"
        s += " -o 'UserKnownHostsFile=/dev/null' -o 'StrictHostKeyChecking=no' -o 'LogLevel=ERROR' "
        s = '-e "ssh' + s + '" '
        scp_command += s
        scp_command += local + " " + user + "@" + host + ":"
        if server_path:
            scp_command += sys.get_path()
        if remote != "":
            scp_command = scp_command + "/" + remote
        if critical:
            return critical_command(scp_command)
        else:
            return command(scp_command, output=output)

    def rsync_get(self, system, remote, local=".", options="", platform=None, critical=False, output=False, delete=False, server_path=False, timeout=3600):
        sys = self.get_system(system, platform)
        user = sys.get_user()
        host = sys.get_host()
        scp_command = "rsync -zrhlpgoD "
        if delete:
            scp_command += "--delete "
        scp_command += options
        if options != "":
            scp_command += " "
        s = sys.get_ssh_key()
        if s is None:
            s = ""
        else:
            s = " -i " + "'" + s + "'"
        s += " -o 'UserKnownHostsFile=/dev/null' -o 'StrictHostKeyChecking=no' -o 'LogLevel=ERROR' "
        scp_command += '-e "ssh' + s + '" '
        scp_command += user + "@" + host + ":"
        if server_path:
            scp_command += sys.get_path()
        scp_command = scp_command + "/" + remote + " "
        scp_command += local
        if critical:
            return critical_command(scp_command)
        else:
            return command(scp_command, output=output, timeout=timeout)

    def scp_send(self, system, local, remote, r=False, platform=None, critical=False, output=False, server_path=False, asynchronous=False, lock=None):
        sys = self.get_system(system, platform)
        user = sys.get_user()
        host = sys.get_host()
        key = sys.get_ssh_key()
        authenticity = '-o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" -o "LogLevel=ERROR" '
        if key is not None:
            key = "-i " + key + " "
        else:
            key = ""
        scp_command = "scp " + key + authenticity
        if self._scp_legacy:
            scp_command += "-O "
        if r:
            scp_command += "-r "
        scp_command += local + " " + user + "@" + host + ":"
        if server_path:
            scp_command += sys.get_path() + "/"
        scp_command += remote
        if asynchronous:
            return self.dependency(lock, scp_command, critical)
        if critical:
            return critical_command(scp_command)
        else:
            return command(scp_command, output=output)

    def scp_get(self, system, remote, local, r=False, platform=None, critical=False, output=False, server_path=False, asynchronous=False, lock=None):
        sys = self.get_system(system, platform)
        user = sys.get_user()
        host = sys.get_host()
        key = sys.get_ssh_key()
        authenticity = '-o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" -o "LogLevel=ERROR" '
        if key is not None:
            key = "-i " + key + " "
        else:
            key = ""
        scp_command = "scp " + key + authenticity
        if self._scp_legacy:
            scp_command += "-O "
        if r:
            scp_command += "-r "
        scp_command += user + "@" + host + ":"
        if server_path:
            scp_command += sys.get_path() + "/"
        scp_command += remote + " "
        scp_command += local
        if asynchronous:
            return self.dependency(lock, scp_command, critical)
        if critical:
            return critical_command(scp_command)
        else:
            return command(scp_command, output=output)

    def async_wait(self, soft=False):
        logger.debug("Asynchronous commands: wait")
        if not soft:
            poll = False
            while not poll:
                poll = True
                locks = list(self._pending_threads.keys())
                for lock in locks:
                    poll = poll and self.poll(lock)
                time.sleep(1)
            for thread in self._running_threads:
                if not async_wait(thread):
                    raise Exception
            self._running_threads.clear()
        else:
            locks = list(self._pending_threads.keys())
            for lock in locks:
                self.poll(lock)
            finished_thread = []
            for thread in self._running_threads:
                if async_poll(thread):
                    if not async_wait(thread):
                        raise Exception
                    finished_thread.append(thread)
            for thread in finished_thread:
                self._running_threads.remove(thread)

    def get_lock(self):
        return self._lock

    def next_lock(self):
        self._lock += 1
        return self.get_lock()

    def get_system_manager(self):
        return self._system_manager
