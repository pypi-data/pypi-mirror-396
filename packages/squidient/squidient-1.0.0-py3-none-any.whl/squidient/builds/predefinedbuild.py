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
from ..utils.message import *
from ..definitions import *

logger = logging.getLogger(logging_context)


class PredefinedBuild:

    def __init__(self, type):
        self._pb = open_json(predefined_build_file)[type]
        if type == "builds":
            self._pb["all"] = (
                    self._pb["gpp"]
                    + self._pb["amd"]
            )
            self._pb["gnu"] = []
            self._pb["intel"] = []
            self._pb["oneapi"] = []
            for i in self._pb["all"]:
                if "gnu" in i:
                    self._pb["gnu"].append(i)

                if "intel" in i:
                    self._pb["intel"].append(i)

                if "oneapi" in i:
                    self._pb["oneapi"].append(i)

    def get_pb(self):
        return self._pb