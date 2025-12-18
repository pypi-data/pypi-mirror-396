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



from platform import system
from os.path import exists
from ..utils.utils import *

logger = logging.getLogger(logging_context)
darwin_ssh_config_file = "/etc/ssh/ssh_config"


def is_system_darwin():
    return "Darwin" in system()


def exist_ssh_config():
    return exists(darwin_ssh_config_file)


def is_config_ok():
    try:
        ssh_config_file = read_text_file(darwin_ssh_config_file).split("\n")
        for line in ssh_config_file:
            l = line.strip()
            if l.startswith("#"):
                continue
            if "SendEnv" in l and ("LANG" in l or "LC_*" in l):
                return False
        return True
    except:
        return True


def test_darwin_ssh_config():
    if is_system_darwin():
        if exist_ssh_config():
            if not is_config_ok():
                return False
    return True
