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



from ..systems.platform import *


class SystemManager:

    def __init__(self, config):
        self._config = config
        self._systems = {}
        self._platforms = {}
        for system in self._config["systems"]:
            self._systems[system] = System(system, self._config)
            self._platforms[system] = {}
            for platform in self._config["systems"][system]["platforms"]:
                self._platforms[system][platform] = Platform(system, platform, config)

    def get_system(self, system):
        return self._systems[system]

    def get_platform(self, system, platform):
        return self._platforms[system][platform]

    def get_systems(self):
        return sorted(self._systems.keys())

    def get_platforms(self, system):
        return sorted(self._platforms[system].keys())