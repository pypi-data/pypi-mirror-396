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


from .codecoverage import *
import lxml.etree
import copy
import os.path

logger = logging.getLogger(logging_context)


def read_base_xml(filename):
    cobertura = lxml.etree.parse(filename)
    return cobertura


def create_package_file(cobertura, package, destination_path):
    filename = "cobertura-{}.xml".format(package.attrib['name'])
    print("\t\tCreating package file {}".format(filename))
    xml_to_write = copy.deepcopy(cobertura)
    packages_node = xml_to_write.find('packages')

    # Delete all the package nodes from the XML
    for package_to_remove in packages_node:
        packages_node.remove(package_to_remove)

    # Now add back the one package we want
    packages_node.append(package)

    package_file = open(filename, 'wb')
    package_file.write(lxml.etree.tostring(xml_to_write))
    package_file.close()


class GcovrCodeCoverage(CodeCoverage):

    def __init__(self, systemManager, ssh, config, revision, alya_repository, builds):
        super().__init__(systemManager, ssh, config, revision, alya_repository, builds)

    def is_cc_runnable(self):
        if self._build in self._builds:
            if self._builds[self._build].get_code_coverage() and self._builds[self._build].check_build_status():
                return True
        return False

    def process(self):
        print("\tGenerating code coverage file...")
        if not self._ssh.ssh(system=self._system, platform=self._platform,
                      cmd=self.gcovr(),
                      server_path=True, path=remote_cc_dir):
            return False
        print("\tGenerating cobertura report...")
        if not self._ssh.ssh(system=self._system, platform=self._platform,
                      cmd=self.cobertura(),
                      server_path=True, path=remote_cc_dir):
            return False
        print("\tGenerating detailed html report...")
        if not self._ssh.ssh(system=self._system, platform=self._platform,
                      cmd=self.html(),
                      server_path=True, path=remote_cc_dir):
            return False
        return True

    def load_modules(self):
        module_cmd = "module purge && module load"
        for module in self._modules:
            module_cmd += " " + module
        return module_cmd

    def gcov_pre(self):
        return "gcovr -r " + self.alya_path() + " " + self._server_path + "/" + self._builds[self._build].get_build_path()

    def gcovr(self):
        return self.load_modules() + " && " + self.gcov_pre() + " -o coverage.txt"

    def cobertura(self):
        return self.load_modules() + " && " + self.gcov_pre() + " -x cobertura.xml"

    def html(self):
        return self.load_modules() + " && " + self.gcov_pre() + " --html-details -p -o coverage.html"

    def get_files(self):
        critical_command("mkdir -p " + cc_report_dir)
        if not self._ssh.rsync_get(system=self._system, platform=self._platform,
                                   remote=remote_cc_dir + "/", local=cc_report_dir + "/", delete=True,
                                   server_path=True, critical=True):
            raise Exception

    def postprocess(self, _print):
        print("\tComputing code coverage")
        self.cc_finding()
        print("\tSplitting cobertura files...")
        self.cobertura_split()

    def cc_finding(self):
        f = open(cc_report_dir + "/coverage.txt", "r")
        lines = f.readlines()
        for line in lines:
            if line.startswith("TOTAL"):
                self._total = int(line.split()[1])
                covered = int(line.split()[2])
                self._failed = self._total-covered
                self._codecoverage = 100.0*float(covered)/float(self._total)

    def cobertura_split(self):
        filename = cc_report_dir + "/cobertura.xml"
        cobertura_xml = read_base_xml(filename)
        command("rm -fr " + xml_report_dir)
        command("mkdir -p " + xml_report_dir)
        current_dir = os.getcwd()
        os.chdir(xml_report_dir)
        for package in cobertura_xml.find('packages'):
            create_package_file(cobertura_xml, package, xml_report_dir)
        os.chdir(current_dir)
