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


from .build import Build
# -*- coding: utf-8 -*-

from ..compilation.configgenerator import *
from ..compilation.cmakeoptions import *
from ..deployment.modulegenerator import *
from ..systems.queuetester import *

logger = logging.getLogger(logging_context)

time_file = "time.out"
env_file = "env.out"
build_out_file = "build.out"
build_err_file = "build.err"
build_all_files = "build.*"

date_string = "date '+%s' >> " + time_file
test_string_sjobexitmod = 'if [ $? -ne 0 ]; then ' + date_string + '; exit 1; fi\n'
clean_string = "find . -name 'CMakeCache.txt' -print0 -o -name '*.cmake' -print0 -o -name 'Makefile' -print0 " \
               "-o -name 'CMakeFiles' -print0 -o -name '*.o' -print0 -o -name '*.mod' -print0 " \
               "-o -name '*.build' -print0 | xargs -0 rm -fr && "


class ExecutableBuild(Build):

    def __init__(self, systemManager, hash, build_id, job, ssh, config, report_directory):
        super().__init__(build_id)
        self._queue_type = "builds"

        #create local directory
        self._report_dir = report_directory + "/" + build_id
        critical_command("mkdir -p " + self._report_dir)

        #class configuration
        self._hash = hash
        self._systemManager = systemManager
        self._jobm = job
        self._ssh = ssh
        self._config = config
        self._build_path = remote_build_dir + "/" + build_id

        #System/platform
        self._sys = systemManager.get_platform(self._system, self._platform)

        #Merge
        self._merge = self._sys.get_merge()

        #Server, installation and module directories
        install_dir = self._sys.get_application_path()
        module_dir = self._sys.get_module_path()
        self._install_path = install_dir + "/" + self._alias
        self._install = self._config["installation"] and self._installable
        if self._install:
            self._queue_type = "install"
        self._module_path = module_dir + "/" + self._alias
        self._module_dir = module_dir
        self._server_path = self._sys.get_path()

        self._sjobexitmod = self._sys.get_sjobexitmod()

        self._queue = ""
        self._slurm_flag = ""
        self._exclusive = False
        self._account = self._sys.get_account()

        self._generator = None
        self._options = None
        self._job_id = ""
        self._report = {}
        self._cmake = False
        self._link_dir = ""

        self._max_jobs = max_jobs_staging

    def set_queue(self):
        queueTester = QueueTester(self._ssh, self._sys, self._hash, self._jobm)
        self._queue, self._slurm_flag, self._exclusive = queueTester.which_qos(
            queue_type=self._queue_type,
            cpus=self._threads,
            timeout=self._timeout,
            flex=self._flex)

    def fill(self, build_id):
        build = self._builds[build_id]
        if len(self._modules) == 0 and "modules" in build:
            self._modules = build["modules"]
        if len(self._env) == 0 and "environment" in build:
            self._env = build["environment"]
        if len(self._pre_exec) == 0 and "preExec" in build:
            self._pre_exec = build["preExec"]
        if len(self._pre_modules) == 0 and "preModules" in build:
            self._pre_modules = build["preModules"]
        if len(self._post_modules) == 0 and "postModules" in build:
            self._post_modules = build["postModules"]
        if len(self._tags) == 0 and "tags" in build:
            self._tags = build["tags"]
        if len(self._sbatch) == 0 and "sbatch" in build:
            self._sbatch = build["sbatch"]
        if self._cc_tool == "" and "cc_tool" in build:
            self._cc_tool = build["cc_tool"]
        if self._compiler == "" and "compiler" in build:
            self._compiler = build["compiler"]
        if self._code_coverage == "" and "codeCoverage" in build:
            self._code_coverage = build["codeCoverage"]
        if self._exclusive_tests == "" and "exclusive" in build:
            self._exclusive_tests = build["exclusive"]
        if self._configuration == "" and "configuration" in build:
            self._configuration = build["configuration"]
        if self._file == "" and "file" in build:
            self._file = build["file"]
        if self._flex == "" and "flex" in build:
            self._flex = build["flex"]
        if self._job == "" and "job" in build:
            self._job = build["job"]
        if self._system == "" and "system" in build:
            self._system = build["system"]
        if self._platform == "" and "platform" in build:
            self._platform = build["platform"]
        if self._lock == "" and "lock" in build:
            self._lock = build["lock"]
        if self._runnable == "" and "runnable" in build:
            self._runnable = build["runnable"]
        if self._threads == "" and "threads" in build:
            self._threads = build["threads"]
        if self._type == "" and "type" in build:
            self._type = build["type"]
        if self._ctest == "" and "ctest" in build:
            self._ctest = build["ctest"]
        if self._timeout == "" and "timeout" in build:
            self._timeout = build["timeout"]
        if self._timeoffset == "" and "timeOffset" in build:
            self._timeoffset = build["timeOffset"]
        if self._version == "" and "version" in build:
            self._version = build["version"]
        if self._alias == "":
            if "alias" in build:
                self._alias = build["alias"]
            else:
                self._alias = self._build_id
        if self._installable == "":
            if "installable" in build:
                self._installable = build["installable"]
            else:
                self._installable = False
        if "from" in build:
            self.fill(build["from"])

    def generate_configuration(self):
        if self._type == "cmake":
            spath = self._server_path + "/"
            options = CMakeOptions(self._file, self._configuration)
            if self._link_dir == "":
                self._link_dir = spath + remote_bin_dir + "/" + self._build_id
            mpirun_options = self._sys.get_mpirun_options(self._modules)
            options.options("$" + cmake_link_dir, spath + remote_cc_dir + "/" + self._build_id, (spath + "/" + alya_dir).replace("//", "/"), mpirun_options)
            self._options = options
            self._cmake = True
        else:
            spath = self._server_path + "/"
            generator = ConfigGenerator(self._file, self._configuration)
            generator.write(self._report_dir, spath + remote_cc_dir + "/" + self._build_id, (spath + self._build_path + "/" + alya_dir).replace("//", "/"))
            self._generator = generator
            self._cmake = False

    def generate_job(self):
        self.set_queue()
        spath = self._server_path + "/"
        script = open(self._report_dir + "/JOB.SB", 'w')
        script.write("#!/bin/bash\n")
        script.write("#SBATCH -D " + spath + self._build_path + "\n")
        script.write("#SBATCH --output=" + build_out_file + "\n")
        script.write("#SBATCH --error=" + build_err_file + "\n")
        script.write("#SBATCH --job-name=" + jtitle + self._hash + "\n")
        script.write("#SBATCH --ntasks=" + str(self._threads)+"\n")
        script.write("#SBATCH --ntasks-per-node=" + str(self._sys.get_tasks_per_node()) + "\n")
        script.write("#SBATCH --time=" + self._timeout + "\n")
        for parameter in self._sbatch:
            if str(self._sbatch[parameter]) == "":
                line = "#SBATCH " + parameter + "\n"
            else:
                line = "#SBATCH " + parameter + "=" + str(self._sbatch[parameter]) + "\n"
            script.write(line)
        if self._queue is not None:
            script.write("#SBATCH " + self._slurm_flag + "=" + self._queue + "\n")
        if self._exclusive:
            script.write("#SBATCH --exclusive\n")
        if self._account is not None:
            script.write("#SBATCH --account=" + self._account + "\n")
        script.write("\n")
        script.write("date '+%s' > " + time_file +"\n")
        script.write("printenv | grep HOSTNAME > " + env_file + "\n")
        script.write("module purge\n")
        for pre_module in self._pre_modules:
            script.write(pre_module + "\n")
        for module in self._modules:
            script.write("module load " + module + "\n")
        for post_module in self._post_modules:
            script.write(post_module + "\n")
        script.write("\n")
        for env in self._env:
            script.write(env + "\n")
        script.write("\n")
        rm_string = "rm " + spath + remote_bin_dir + "/alya_" + self._build_id + "\n"
        rm_string += "rm " + spath + remote_bin_dir + "/alya2pos_" + self._build_id + "\n"
        script.write(rm_string)
        if self._sjobexitmod:
            test_string = test_string_sjobexitmod
        else:
            test_string = "if [ $? -ne 0 ]\n"
            test_string += "then\n"
            test_string += rm_string
            test_string += date_string + "\n"
            test_string += "exit 1\n"
            test_string += "fi\n"
        if not self._cmake:
            #TODO no cmake build should be removed from the TS
            script.write("cp -r " + spath + alya_dir + " " + alya_dir+"\n")
            script.write("cp config.in " + alya_dir + "/configure/\n")
            script.write("cp time.out " + alya_dir + "/configure/\n")
            script.write("cd " + alya_dir + "/configure\n")
            alya_modules = ""
            for m in self._generator.get_modules():
                alya_modules += m
                alya_modules += " "
            script.write("./configure -x " + alya_modules + "\n")
            for prec in self._generator.get_precompilation():
                script.write("make " + prec + "\n")
            if self._generator.get_special() != "":
                script.write("make " + self._generator.get_special() + " -j" + str(self._threads) + "\n")
            else:
                script.write("make -j" + str(self._threads) + "\n")
            script.write("export current_dir=`pwd -P`\n")
            script.write("if [ -f $current_dir/Alya.x ]\n")
            script.write("then\n")
            script.write("ln -s $current_dir/Alya.x " + spath + remote_bin_dir + "/alya_" + self._build_id + "\n")
            script.write("fi\n")
            script.write("if [ -f $current_dir/../../Utils/user/alya2pos/alya2pos.x ]\n")
            script.write("then\n")
            script.write("ln -s $current_dir/../../Utils/user/alya2pos/alya2pos.x " + spath + remote_bin_dir + "/alya2pos_" + self._build_id + "\n")
            script.write("fi\n")
            script.write("cd " + spath + self._build_path + "\n")
        else:
            script.write("rm -fr " + spath + remote_bin_dir + "/" + self._build_id +"\n")
            script.write("rm -fr cmake.err\n")
            script.write("export " + cmake_link_dir + "=" + self._link_dir + "\n")
            if not self._code_coverage:
                script.write("cmake " + self._options.get_options() + " " + spath + alya_dir + ' 2> cmake.err\n')
                script.write('if [ $? -ne 0 ]; then echo "RESET CMAKE: You have changed variables that require your cache to be deleted" >> cmake.err; fi\n')
                script.write(">&2 cat cmake.err\n")
                script.write('grep "You have changed variables that require your cache to be deleted" cmake.err && ')
                script.write(clean_string)
            build_string = 'cmake ' + self._options.get_options() + " " + spath + alya_dir + '\n'
            build_string += "make install -j" + str(self._threads) + "\n"
            script.write(build_string)
            if self._code_coverage:
                script.write(test_string)
            else:
                script.write('if [ $? -ne 0 ]\n')
                script.write('then\n')
                script.write(clean_string)
                script.write(build_string)
                script.write(test_string)
                script.write('fi\n')
            if self._ctest:
                ctest_string = ""
                for pre_exec in self._pre_exec:
                    ctest_string += pre_exec + " && "
                ctest_string += "ctest\n"
                ctest_string += "if [ $? -ne 0 ]\n"
                ctest_string += "then\n"
                ctest_string += "cat Testing/Temporary/LastTest.log 1>&2\n"
                ctest_string += rm_string
                ctest_string += date_string + "\n"
                ctest_string += "exit 1\n"
                ctest_string += "fi\n"
                script.write(ctest_string)
            script.write("export link_dir=" + spath + remote_bin_dir + "/" + self._build_id + "/bin\n")
            link_string = "ln -s $link_dir/alya " + spath + remote_bin_dir + "/alya_" + self._build_id + "\n"
            link2_string = "ln -s $link_dir/alya2pos " + spath + remote_bin_dir + "/alya2pos_" + self._build_id + "\n"
            script.write(link_string)
            script.write(test_string)
            script.write(link2_string)
            script.write(test_string)
            if self._install:
                install_string = "cmake " + " -DCMAKE_INSTALL_PREFIX=" + self._install_path + " " + spath + alya_dir + ' &&'
                install_string += "rm -fr " + self._install_path + "\n"
                install_string += "make install -j" + str(self._threads) + "\n"
                script.write(install_string)
                m = ModuleGenerator(self._alias, self._modules, self._install_path, self._module_path)
                script.write(m.getmodule())
                if self._alias == self._default:
                    script.write("cp " + self._module_path + " " + self._module_dir + "/default\n")
            configuration = open(self._report_dir + "/config.in", 'w')
            configuration.write("#This file is not actually used to configure squidient\n")
            configuration.write("#You'll find here the commands to manually build alya with the same options as with squidient\n")
            configuration.write("#Execute these commands in the alya root directory\n")
            configuration.write("module purge\n")
            for pre_module in self._pre_modules:
                configuration.write(pre_module + "\n")
            for module in self._modules:
                configuration.write("module load " + module + "\n")
            for post_module in self._post_modules:
                configuration.write(post_module + "\n")
            configuration.write("rm -fr build\n")
            configuration.write("mkdir -p build\n")
            configuration.write("cd build\n")
            configuration.write('cmake ' + self._options.get_options().split("-DCMAKE_INSTALL_PREFIX=")[0] + ' ..\n')
            configuration.write("make -j4\n")
            for pre_exec in self._pre_exec:
                configuration.write(pre_exec + "\n")
            configuration.write("ctest\n")
            configuration.write("cat Testing/Temporary/LastTest.log\n")
            configuration.close()
        script.write(date_string + "\n")
        script.close()

    def send_files(self):
        if (not self._cmake) or self._code_coverage:
            self._ssh.rmdir(system=self._system, path=self._build_path, server_path=True)
        self._ssh.mkdir(system=self._system, path=self._build_path, server_path=True)
        self._ssh.rmdir(system=self._system, path=remote_cc_dir + "/" + self._build_id, server_path=True)
        if self._code_coverage:
            self._ssh.mkdir(system=self._system, path=remote_cc_dir + "/" + self._build_id, server_path=True)
        self._ssh.scp_send(system=self._system, local=self._report_dir + "/*", remote=self._build_path + "/", server_path=True, critical=True)

    def launch_job(self):
        self._job_id = self._jobm.launch_job(id=self._build_id, path=self._build_path + "/JOB.SB",
                                             system=self._system, platform=self._platform,
                                             server_path=True, key_lock=self._lock, max_jobs=self._max_jobs)
        return self._job_id

    def get_job_id(self):
        return self._job_id

    def check_job_status(self):
        return self._jobm.check_job(job_id=self._job_id, system=self._system, platform=self._platform)

    def check_build_status(self):
        status = True
        #if self._sjobexitmod:
        #    status = status and "COMPLETED" in self._ssh.ssh(
        #        cmd="sjobexitmod -l " + str(self._job_id), server_path=True, output=True, system=self._system, platform=self._platform).strip()
        status = status and "is_present" in self._ssh.ssh(
            cmd="if test -f " + remote_bin_dir + "/alya_" + self._build_id + "; then echo is_present; fi",
            system=self._system, platform=self._platform, server_path=True, output=True).strip()
        return status and "is_present" in self._ssh.ssh(
            cmd="if test -f " + remote_bin_dir + "/alya2pos_" + self._build_id + "; then echo is_present; fi",
            system=self._system, platform=self._platform, server_path=True, output=True).strip()

    def build_report(self):
        self.get_build_output()
        self._report["name"] = self._build_id
        self._report["modules"] = self._modules
        self._report["runnable"] = self._runnable
        self._report["compiler"] = self._compiler
        self._report["version"] = self._version
        self._report["tags"] = self._tags
        self._report["status"] = self.check_build_status()
        self._report["jobId"] = self._job_id
        self._report["time"] = self.compute_time()
        self._report["hostname"] = self.find_hostname()
        save_json(self._report, self._report_dir + "/build.json")

    def compute_time(self):
        if self._sjobexitmod:
            if "TIMEOUT" in self._ssh.ssh(cmd="sjobexitmod -l " + str(self._job_id),
                                          server_path=True, output=True, system=self._system, platform=self._platform).strip():
                return "timeout"
        try:
            t = read_text_file(self._report_dir + "/" + time_file).split("\n")
            start = int(t[0])
            end = int(t[1])
            return duration2str(start, end)
        except:
            return "timeout"

    def find_hostname(self):
        try:
            return read_text_file(self._report_dir + "/" + env_file).strip().replace("HOSTNAME=", "")
        except:
            return "unknown"

    def get_report(self):
        return self._report

    def get_build_output(self):
        self._ssh.scp_get(system=self._system, remote=self._build_path + "/" + build_all_files, local=self._report_dir, server_path=True)
        self._ssh.scp_get(system=self._system, remote=self._build_path + "/" + time_file, local=self._report_dir, server_path=True)
        self._ssh.scp_get(system=self._system, remote=self._build_path + "/" + env_file, local=self._report_dir, server_path=True)

    def get_tags(self):
        return self._tags

    def get_modules(self):
        return self._modules

    def get_pre_modules(self):
        return self._pre_modules

    def get_post_modules(self):
        return self._post_modules

    def get_pre_exec(self):
        return self._pre_exec

    def get_env(self):
        return self._env

    def get_compiler(self):
        return self._compiler

    def get_runnable(self):
        return self._runnable

    def get_version(self):
        return self._version

    def get_system(self):
        return self._system

    def get_platform(self):
        return self._platform

    def get_build_id(self):
        return self._build_id

    def get_build_path(self):
        return self._build_path

    def get_code_coverage(self):
        return self._code_coverage

    def get_exclusive_tests(self):
        return self._exclusive_tests

    def get_merge(self):
        return self._merge

    def get_cc_tool(self):
        return self._cc_tool

    def get_timeoffset(self):
        return self._timeoffset
