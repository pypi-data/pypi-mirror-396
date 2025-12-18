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



from ..systems.qos import *


class Reservation(QoS):

    def __init__(self, config):
        super().__init__("reservation", config)
        try:
            self._reservation_name = self._config["name"]
        except:
            self._reservation_name = None
        self._enable = self._config["enable"]

    def get_enable(self):
        return self._enable

    def get_reservation_name(self):
        return self._reservation_name

    def get_slurm_option(self):
        return "--reservation"
