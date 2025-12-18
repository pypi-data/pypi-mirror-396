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



import os
import logging
from .log import logging_context

logger = logging.getLogger(logging_context)


def print_line():
    print("----------------------------------------------------")


def jump():
    print("")


def mega_jump():
    jump()
    jump()
    jump()


def stagingbanner():
    os.system('clear')
    jump()
    print_line()
    print("                  squidient: staging                         ")
    print_line()


def monitorbanner():
    os.system('clear')
    jump()
    print_line()
    print("                  squidient: monitor                    ")
    print_line()


def error():
    mega_jump()
    print("Error detected during the execution of squidient")
    print("Try to update alya-staging (git pull) and to configure it again (configure --all)")
    print("Contact alya-support@bsc.es if the problem persists.")
    print("All the running jobs are being killed...")
