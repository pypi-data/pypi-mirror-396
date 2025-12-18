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



class System:

    def __init__(self, system, config):
        self._system = system
        c = config["systems"][system]
        self._host = c["host"]
        self._user = c["user"]
        self._path = c["path"]
        self._ssh_key = None
        if "sshKey" in c:
            self._ssh_key = c["sshKey"]
        if self._host in c["platforms"]:
            p = c["platforms"][self._host]
            self._user = p["user"]
            if "sshKey" in p:
                self._ssh_key = p["sshKey"]
            self._host = c["platforms"][self._host]["host"]

    def get_system(self):
        return self._system

    def get_host(self):
        return self._host

    def get_user(self):
        return self._user

    def get_path(self):
        return self._path

    def get_ssh_key(self):
        return self._ssh_key