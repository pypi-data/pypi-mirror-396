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

from __future__ import annotations

import sys
import traceback
from typing import Optional, Sequence

from .utils.arguments import Arguments
from .monitor.monitor import *
from .squidient import IgnoredKeyboardInterrupt, darwin_bad_ssh
from .connection.sshconfigchecker import test_darwin_ssh_config, darwin_ssh_config_file


def help():
    print("options:")
    jump()
    print("\tconfigure                             Configure squidient-monitor; configure -h to print configure help")
    print("\tall [-d | -t]                         Run all the monitor")
    print("\tterraform start                       Create the resources with terraform")
    print("\tterraform stop                        Destroy the resources with terraform")
    print("\tbuild                                 Run the builds only")
    print("\ttest [-d | -t]                        Run the tests only; this option requires to previously run all or build")
    print("\thelp                                  Print this help")
    jump()
    print("Additional options :")
    jump()
    print("\t-d | --dirs [list of directories]     Run only the tests included in these subdirectories")
    print("\t-t | --tests [list of tests]          Run only a list of tests")
    print("\t--terraform-keep-alive                Do not destroy the terraform resources at the end of the execution")


def _run_cli(argv: Sequence[str]) -> int:
    monitor = None
    terraform = None

    try:
        # Keep original behavior: if missing arg1 or arg1 contains "help" -> show help and exit
        if "help" == argv[0]:
            help()
            return 0

        arguments = Arguments()
        try:
            args = argv[0:]
        except Exception:
            args = None

        if not test_darwin_ssh_config():
            darwin_bad_ssh()
            return 1

        arguments.parse(args)

        terraform = Terraform()
        destroy_terraform = False

        if len(argv) >= 2 and "terraform" == argv[0]:
            if "start" == argv[1]:
                terraform.create()
                return 0
            elif "stop" == argv[1]:
                terraform.destroy()
                return 0

        if "all" == argv[0]:
            terraform.create()
            if "--terraform-keep-alive" not in argv:
                destroy_terraform = True

        monitor = Monitor(arguments, destroy_terraform=destroy_terraform)
        monitor.init()

        if "validate" == argv[0]:
            monitor.validate()

        elif "build" == argv[0]:
            monitor.lock(terraform)
            monitor.build(terraform)

        elif "test" == argv[0]:
            monitor.lock(terraform)
            monitor.test(terraform)

        elif "report" == argv[0]:
            monitor.lock(terraform)
            monitor.test(terraform, fake=True)

        elif "all" == argv[0]:
            monitor.lock(terraform)
            monitor.all(terraform)
            if monitor.destroy_terraform():
                terraform.destroy()

        else:
            help()

        return 0

    except KeyboardInterrupt:
        with IgnoredKeyboardInterrupt():
            try:
                if monitor is not None:
                    monitor.keyboard_interrupt()
            except Exception:
                pass

            try:
                if terraform is None:
                    terraform = Terraform()
                if monitor is not None and monitor.destroy_terraform():
                    terraform.destroy()
            except Exception:
                pass

            print("Exiting...")
            return 1

    except Exception:
        error()
        var = traceback.format_exc()
        command("echo -e \"" + var + "\" > client.err")
        print_line()
        try:
            if monitor is not None:
                monitor.kill_all()
                jump()
                monitor.end()
            if terraform is None:
                terraform = Terraform()
            if monitor is not None and monitor.destroy_terraform():
                terraform.destroy()
        except Exception:
            jump()
        print_line()
        print("Error:")
        print(var)
        print_line()
        print("Exiting...")
        return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Programmatic entry point.

    - If argv is None, uses sys.argv (CLI behavior).
    - Returns an exit code (0 for success).
    """
    if argv is None:
        argv = sys.argv[1:]
    return _run_cli(argv)


if __name__ == "__main__":
    _run_cli(sys.argv[1:])
