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


import logging
import time
import os
import getpass
import json


def log_open_json(name):
	with open(name) as json_data:
		return json.load(json_data)


logging_context = "squidient"
#Initializing logger

if not os.path.isdir("log"):
	os.system("mkdir log")
try:
	config = log_open_json("configuration.json")
	if config["cleanLog"]:
		os.system("rm -rf log/*")
except:
	pass
	
logger = logging.getLogger(logging_context)
date = time.strftime("%Y_%m_%d_%H")
user = getpass.getuser()
fh = logging.FileHandler('log/'+date+'.log')

#Logger set debug level
logger.setLevel(logging.DEBUG)
fh.setLevel(logging.DEBUG)

#Set logger format
formatter = logging.Formatter('[%(asctime)s] [%(funcName)s():%(lineno)d] %(levelname)s - %(message)s','%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)
