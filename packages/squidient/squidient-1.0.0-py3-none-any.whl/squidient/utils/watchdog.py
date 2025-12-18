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


import threading
from ..definitions import watchdog_max_failures
from .utils import *
from .message import *

logger = logging.getLogger(logging_context)


class Watchdog(threading.Thread):

    def __init__(self, ts_pid, tokens, pipelines, api):
        threading.Thread.__init__(self)
        self._ts_pid = ts_pid
        self.threadID = 1
        self.name = "watchdog"
        self._pipeline_list = pipelines
        self._pipelines = {}
        self._token_list = tokens
        self._tokens = {}
        self._data = []
        self._failure_count = {}
        self._api = api

    def run(self):
        jump()
        print("Starting Watchdog:")
        i = 0
        for pipeline in self._pipeline_list:
            try:
                p = pipeline.split(":")  # format: project:pipeline
                self._pipelines[p[0]] = p[1]
                self._tokens[p[0]] = self._token_list[i]
                i += 1
                print("Pipeline detected: project " + p[0] + ", id " + p[1])
                self._failure_count[p[0]] = 0
            except:
                print("Pipeline does not have the good format! (project:pipeline):" + pipeline)
                self.killts(self._ts_pid)
        while True:
            for project in self._pipelines:
                try:
                    com = 'curl --header "PRIVATE-TOKEN: ' + self._tokens[project] + '" "' + self._api + "/" + project + '/pipelines/' + \
                          self._pipelines[project] + '"'
                    d = command(com, output=True, silent=True).split("\n")[-1]
                    self._data = json.loads(d)
                    if self._data["status"] != "running":
                        print("Pipeline " + self._pipelines[project] + " is not running!")
                        self.killts(self._ts_pid)
                except:
                    print("Impossible to connect to gitlab pipeline " + self._pipelines[project])
                    if self._failure_count[project] < watchdog_max_failures:
                        print("Trying again...")
                        self._failure_count[project] += 1
                    else:
                        self.killts(self._ts_pid)
                else:
                    self._failure_count[project] = 0
            time.sleep(30)

    def killts(self, pid):
        print("Kill squidient with fire!!!!")
        os.kill(pid, signal.SIGINT)
