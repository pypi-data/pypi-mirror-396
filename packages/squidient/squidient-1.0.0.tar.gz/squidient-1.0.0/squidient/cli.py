#########################################################################
#                                                                       #
#  This file is part of gazix.                                          #
#                                                                       #
#  gazix is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by #
#  the Free Software Foundation, either version 3 of the License, or    #
#  (at your option) any later version.                                  #
#                                                                       #
#  gazix is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of       #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        # 
#  GNU General Public License for more details.                         #
#                                                                       #
#  You should have received a copy of the GNU General Public License    #
#  along with gazix. If not, see <https://www.gnu.org/licenses/>.       #
#                                                                       #
#########################################################################

import sys

from .configure import configure_help as chelp
from .init import copy_packaged_tree_flat
from .utils.message import jump
from .squidient import help as shelp
from .squidientmonitor import help as mhelp
from .configure import main as cmain
from .squidient import main as smain
from .squidientmonitor import main as mmain
from .utils.package import check_latest_package_any_index

def help():
    print("squidient [option]")
    jump()
    print("\tsquidient help                   Print this help")
    jump()
    print("\tIntialization options:")
    print("\tsquidient init [directory]       Initialize the directory")
    jump()
    print("\tConfiguration options:")
    print("\tsquidient configure [options]    Configure squidient")
    chelp()
    jump()
    print("\tBuild and test options:")
    print("\tsquidient run [options]")
    shelp()
    jump()
    print("\tsquidient monitor [options]")
    mhelp()

def main():
    info = check_latest_package_any_index("squidient")

    if not info["up_to_date"]:
        print(
            f"⚠ squidient {info['installed']} is outdated. "
            f"Latest is {info['latest']} on {info['latest_index']}."
        )
        print("Please update to the last version running python -m pip install --upgrade squidient")
    else:
        print(
            f"squidient {info['installed']} is up to date "
            f"(checked: {info['checked']})"
        )

    program = sys.argv[0]
    try:
        args = sys.argv[1:]
        if args[0] == "help":
            exit()
        if args[0] == "init":
            try:
                dist_directory = args[1]
            except IndexError:
                dist_directory = "./"
            copy_packaged_tree_flat("squidient", "data", dist_directory, overwrite=True)
            copy_packaged_tree_flat("squidient", "utils", dist_directory+"/src-remote/utils", overwrite=True)
            exit(0)
        if args[0] == "configure":
            return cmain(args[1:])
        elif args[0] == "run":
            return smain(args[1:])
        elif args[0] == "monitor":
            return mmain(args[1:])
        else:
            help()
    except Exception as e:
        print(e)
        print("Exception")



if __name__ == "__main__":
    main()
