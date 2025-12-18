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



class QoS:

    def __init__(self, name, config):
        self._name = name
        self._config = config
        try:
            self._size = config["size"]
        except:
            self._size = 0
        try:
            self._timeout = config["timeout"]
        except:
            self._timeout = ""

    def get_size(self):
        return self._size

    def get_timeout(self):
        return self._timeout

    def is_valid(self, size, timeout):
        if self._size < size:
            return False
        my_timeout = self._timeout.split(":")
        their_timeout = timeout.split(":")
        my_timeout = 3600 * int(my_timeout[0]) + 60 * int(my_timeout[1]) + int(my_timeout[2])
        their_timeout = 3600 * int(their_timeout[0]) + 60 * int(their_timeout[1]) + int(their_timeout[2])
        return my_timeout >= their_timeout

    def get_slurm_option(self):
        return "--qos"





