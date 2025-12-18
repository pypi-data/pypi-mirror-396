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
import signal
import logging
from typing import Optional, Sequence

from .utils.arguments import Arguments
from .staging.staging import *
from .connection.sshconfigchecker import test_darwin_ssh_config, darwin_ssh_config_file
from .terraform.terraform import *


class IgnoredKeyboardInterrupt(object):

    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        # self.signal_received = (sig, frame)
        logging.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        # signal.signal(signal.SIGINT, self.old_handler)
        # if self.signal_received:
        #     self.old_handler(*self.signal_received)
        logging.debug('Exiting from SIGINT handler.')


def help():
    print("options:")
    jump()
    print("\tall [-d | -t]                         Run all the testsuite")
    print("\tterraform start                       Create the resources with terraform")
    print("\tterraform stop                        Destroy the resources with terraform")
    print("\tbuild                                 Run the builds only")
    print("\ttest [-d | -t]                        Run the tests only; this option requires to previously run all or build")
    print("\tcc                                    Run the code coverage only; this option requires to previously run all or test; only work with intel compilers")
    print("\tclean                                 Clean the report")
    print("\thelp                                  Print this help")
    jump()
    print("Additional options :")
    jump()
    print("\t-d | --dirs [list of directories]     Run only the tests included in these subdirectories")
    print("\t-t | --tests [list of tests]          Run only a list of tests")
    print("\t--terraform-keep-alive                Do not destroy the terraform resources at the end of the execution")
    jump()
    print("Alamak options :")
    jump()
    print("\t--alamak-user [user]                  Alamak user")
    print("\t--alamak-token [user]                 Alamak token")


def darwin_bad_ssh():
    print_line()
    print("A problem with your ssh configuration has been detected!")
    jump()
    print("On Darwin systems, the presence of the following line in the " + darwin_ssh_config_file + " file:")
    jump()
    print("SendEnv LANG LC_*")
    jump()
    print("leads to issues when running squidient.")
    jump()
    print("Please, comment it as it follows before running this program:")
    jump()
    print("# SendEnv LANG LC_*")
    jump()
    print("Exiting...")


def _run_cli(argv: Sequence[str]) -> int:
    cicd = None
    terraform = None

    try:
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

        if len(argv) >= 1 and "terraform" == argv[0]:
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

        cicd = Staging(arguments, destroy_terraform=destroy_terraform)

        if "clean" == argv[0]:
            cicd.clean()
            return 0

        cicd.init()

        if "validate" == argv[0]:
            cicd.validate()

        elif "report" == argv[0]:
            if len(argv) >= 2:
                if "push" == argv[1]:
                    cicd.report_push()
                elif "pull" == argv[1]:
                    cicd.report_pull(argv[2])
            cicd.lock(terraform)
            cicd.test(terraform, fake=True)

        elif "build" == argv[0]:
            if not cicd.build_warning():
                raise Exception
            cicd.lock(terraform)
            cicd.build(terraform)

        elif "test" == argv[0]:
            if not cicd.test_warning():
                raise Exception
            cicd.lock(terraform)
            cicd.test(terraform)

        elif "all" == argv[0]:
            if not cicd.test_warning():
                raise Exception
            cicd.lock(terraform)
            cicd.all(terraform)
            if cicd.destroy_terraform():
                terraform.destroy()

        elif "cc" == argv[0]:
            cicd.lock(terraform)
            cicd.cc()

        elif "clean" == argv[0]:
            cicd.clean()

        else:
            help()

        return 0

    except KeyboardInterrupt:
        # Try to mimic the original cleanup, but keep it safe if cicd/terraform is None.
        with IgnoredKeyboardInterrupt():
            try:
                if cicd is not None:
                    cicd.keyboard_interrupt()
            except Exception:
                pass
            try:
                if terraform is None:
                    terraform = Terraform()
                if cicd is not None and cicd.destroy_terraform():
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
            if cicd is not None:
                cicd.kill_all()
                jump()
                cicd.end()
            if terraform is None:
                terraform = Terraform()
            if cicd is not None and cicd.destroy_terraform():
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
