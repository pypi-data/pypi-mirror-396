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



from ..definitions import lock_file
from .log import *

logger = logging.getLogger(logging_context)


class Lock:

    def __init__(self, ssh):
        self._ssh = ssh
        self._path = os.getcwd()

    def get_local_lock(self):
        return os.path.isfile(self._path + "/" + lock_file)

    def set_local_lock(self):
        if self.get_local_lock():
            return False
        try:
            with open(self._path + "/" + lock_file, 'w') as fp:
                pass
        except:
            return False
        return True

    def rm_local_lock(self):
        if not self.get_local_lock():
            return True
        try:
            os.remove(self._path + "/" + lock_file)
        except:
            return False
        return True

    def get_remote_lock(self, system):
        status = self._ssh.ssh(system=system, cmd="if test -f " + lock_file + "; then echo lock_present ; else echo lock_missing; fi", server_path=True, output=True)
        if "lock_present" in status:
            return True
        else:
            return False

    def set_remote_lock(self, system):
        if self.get_remote_lock(system):
            return False
        self._ssh.mkdir(system=system, path="", server_path=True, critical=True)
        return self._ssh.ssh(system=system, cmd="touch " + lock_file, server_path=True)

    def rm_remote_lock(self, system):
        if not self.get_remote_lock(system):
            return True
        return self._ssh.ssh(system=system, cmd="rm " + lock_file, server_path=True)

