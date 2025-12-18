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



from ..utils.log import *

logger = logging.getLogger(logging_context)

class ModuleGenerator:

    def __init__(self, build_id, modules, installation_path, module_path):
        self._build_id = build_id
        self._modules = modules
        self._installation_path = installation_path
        self._module_path = module_path

    def getmodule(self):
        out_module = "' >> " + self._module_path + "\n"
        echo = "echo '"
        module = echo + "#%Module1.0' > " + self._module_path + "\n"
        module += echo + "set PROG_NAME ALYA" + out_module
        module += echo + "set PROG_VERSION " + self._build_id + out_module
        module += echo + "set PROG_HOME " + self._installation_path + "/bin" + out_module
        module += echo + "proc ModulesHelp { } {" + out_module
        module += echo + 'puts stderr "$PROG_NAME version $PROG_VERSION"' + out_module
        module += echo + "}" + out_module
        module += echo + 'module-whatis "loads the $PROG_NAME $PROG_VERSION"' + out_module
        #module += echo + "conflict $PROG_NAME" + out_module
        if len(self._modules) > 0:
            for m in self._modules:
                module += echo + "prereq " + m + out_module
        module += echo + 'if { [module-info mode] != "whatis" } {' + out_module
        module += echo + 'puts stderr "[module-info mode] [module-info name] (PATH)"' + out_module
        module += echo + "}" + out_module
        module += echo + "prepend-path PATH $PROG_HOME" + out_module
        return module
