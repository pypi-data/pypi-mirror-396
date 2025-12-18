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



from .instancemerger import *

logger = logging.getLogger(logging_context)


class Test:

    def __init__(self, systemManager, hash, job, ssh, json_path, config, report_dir, remote_dir):
        self._systemManager = systemManager
        self._hash = hash
        self._job = job
        self._ssh = ssh
        self._config = config
        self._json_path = json_path
        self._local_test_path = json_path.rsplit('/', 1)[0]
        self._json = open_json(json_path)
        json = self._json
        self._name = json["name"]
        self._include = []
        self._exclude = []
        self._executions = json["executions"]
        if "command" in json:
            self._command = json["command"]
        if "include" in json:
            self._include = json["include"]
        if "exclude" in json:
            self._exclude = json["exclude"]
        self._instances = {}
        self._report = {}
        self._finished_instances = {}
        self._relaunch_instances = {}
        self._pending_instances = {}
        self._initialized = False
        self._status = False
        self._failed = 0
        self._relaunch = False
        self._report_dir = report_dir
        self._remote_dir = remote_dir

    def prepare(self, build, instancemerger=None, fake=True):
        merge = True
        if instancemerger is None:
            merge = False
        self._initialized = self._initialized
        self._instances[build.get_build_id()] = []
        self._pending_instances[build.get_build_id()] = []
        for execution in self._executions:
            openmp = True
            if "openmp" not in execution:
                openmp = False
                execution["openmp"] = 0
            elif execution["openmp"] == 0:
                openmp = False
            if self.valid(build, execution, openmp):
                instance = Instance(
                    self._systemManager,
                    self._hash,
                    self._name,
                    self._job,
                    self._ssh,
                    self._json,
                    self._config,
                    build,
                    execution,
                    self._local_test_path,
                    self._json_path,
                    self._report_dir,
                    self._remote_dir)
                instance.initialize()
                if instance.overloaded():
                    print("Instance " + instance.get_id() + " overloaded for this platform! Skipping!")
                    continue
                if not fake:
                    if merge and instance.get_mergeable():
                        tasks = instance.get_tasks()
                        if tasks not in instancemerger:
                            instancemerger[tasks] = [
                                InstanceMerger(
                                    systemManager=self._systemManager,
                                    hash=self._hash,
                                    internalId=str(tasks)+"_0",
                                    job=self._job,
                                    ssh=self._ssh,
                                    config=self._config,
                                    build=build,
                                    remote_dir=self._remote_dir,
                                    report_dir=self._report_dir)
                                ]
                        if not instancemerger[tasks][-1].add_instance(instance):
                            id = str(len(instancemerger[tasks]))
                            instancemerger[tasks].append(InstanceMerger(
                                systemManager=self._systemManager,
                                hash=self._hash,
                                internalId=str(tasks)+"_"+str(id),
                                job=self._job,
                                ssh=self._ssh,
                                config=self._config,
                                build=build,
                                remote_dir=self._remote_dir,
                                report_dir=self._report_dir)
                            )
                            instancemerger[tasks][-1].add_instance(instance)
                        self._instances[build.get_build_id()].append(instance)
                    else:
                        self._pending_instances[build.get_build_id()].append(instance)
                else:
                    self._finished_instances[instance.get_id()] = instance
                    self._instances[build.get_build_id()].append(instance)

    def run(self, build):
        i = 0
        for instance in self._pending_instances[build.get_build_id()]:
            i += 1
            instance.run()
            self._instances[build.get_build_id()].append(instance)
        self._pending_instances.pop(build.get_build_id())
        return i

    def valid(self, build, execution, openmp):
        if not build.get_runnable():
            return False
        else:
            tags = list(build.get_tags())
            if ("openmp" in tags and not openmp) or ("openmp" not in tags and openmp):
                return False
            if openmp:
                tags.remove("openmp")
            tags.append(build.get_compiler())
            tags.append(build.get_compiler() + "/" + build.get_version())
            for i in self._exclude:
                if i in tags:
                    return False
            for i in self._include:
                if i not in tags:
                    return False
            if "exclude" in execution:
                for i in execution["exclude"]:
                    if i in tags:
                        return False
            if "include" in execution:
                for i in execution["include"]:
                    if i not in tags:
                        return False
            if "system" in execution:
                if execution["system"] != build.get_system():
                    return False
                if "platform" in execution:
                    if execution["platform"] != build.get_platform():
                        return False
        return True

    def get_name(self):
        return self._name

    def get_report(self):
        return self._report

    def get_status(self):
        return self._status

    def get_failed(self):
        return self._failed

    def check_jobs(self):
        jobs = {}
        jobs["scheduled"] = 0
        jobs["terminating"] = 0
        jobs["pending"] = 0
        jobs["running"] = 0
        jobs["finished"] = 0
        jobs["unknown"] = 0
        jobs["total"] = 0
        for build in self._instances:
            for instance in self._instances[build]:
                status = instance.check_job()
                if "Finished" in status:
                    if instance.get_id() not in self._finished_instances:
                        self._finished_instances[instance.get_id()] = instance
                if not instance.get_merged():
                    if "Scheduled" in status:
                        jobs["scheduled"] += 1
                        jobs["total"] += 1
                    elif "Terminating" in status:
                        jobs["terminating"] += 1
                        jobs["total"] += 1
                    elif "Pending" in status:
                        jobs["pending"] += 1
                        jobs["total"] += 1
                    elif "Running" in status:
                        jobs["running"] += 1
                        jobs["total"] += 1
                    elif "Finished" in status:
                        jobs["finished"] += 1
                        jobs["total"] += 1
                    else:
                        jobs["unknown"] += 1
                        jobs["total"] += 1
        return jobs

    def build_report(self, fake=False, download_report=False):
        if len(self._report) > 0 and not self._relaunch:
            return
        self._relaunch = False
        self._failed = 0
        self._report["name"] = self._name
        self._report["authors"] = self._json["authors"]
        self._report["description"] = self._json["description"]
        self._report["modules"] = self._json["modules"]
        self._report["postprocess"] = self._json["postprocess"]
        self._report["instances"] = []
        self._report["status"] = True
        self._report["error"] = "OK"
        self._report["retry"] = False
        for instance in self._finished_instances:
            self._finished_instances[instance].build_report(download_report=download_report)
            if (not fake) and self._finished_instances[instance].get_relaunch():
                self._finished_instances[instance].run()
                self._relaunch_instances[instance] = self._finished_instances[instance]
                self._relaunch = True
            else:
                report = self._finished_instances[instance].get_report()
                status = report["status"]
                if not status:
                    self._failed += 1
                error = report["error"]
                self._report["instances"].append(report)
                self._report["status"] = self._report["status"] and status
                self._report["retry"] = report["retries"] > 0 or self._report["retry"]
                self._status = self._report["status"]
                if not status:
                    if ("OK" in self._report["error"] or "tolerance" in self._report["error"]) and "tolerance" in error:
                        self._report["error"] = "tolerance"
                    elif (error != self._report["error"]) and "tolerance" not in error:
                            if "OK" in self._report["error"] or "tolerance" in self._report["error"]:
                                self._report["error"] = error
                            else:
                                self._report["error"] = "KO"
        for instance in self._relaunch_instances:
            self._finished_instances.pop(instance)
        self._relaunch_instances = {}

    def get_relaunch(self):
        return self._relaunch





