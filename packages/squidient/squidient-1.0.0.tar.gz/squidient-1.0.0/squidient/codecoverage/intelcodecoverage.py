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

logger = logging.getLogger(logging_context)


class IntelCodeCoverage(CodeCoverage):

    def __init__(self, systemManager, ssh, config, revision, alya_repository, builds):
        super().__init__(systemManager, ssh, config, revision, alya_repository, builds)

    def process(self):
        print("\tMerging code coverage files...")
        if not self.merge():
            jump()
            print("\tMerging has failed!")
            print_line()
            return False
        print("\tGenerating code coverage html files...")
        if not self.codecov():
            jump()
            print("\tCode coverage has failed!")
            print_line()
            return False
        return True

    def merge(self):
        spi = ""
        dpis = "-a"
        self._module_cmd = "module purge && "
        for module in self._modules:
            self._module_cmd += "module load " + module + " && "
        for b in self._builds:
            if self._builds[b].get_system() == self._system and self._builds[b].get_platform() == self._platform:
                if self._builds[b].get_code_coverage():
                    if self._builds[b].check_build_status():
                        cc_path = remote_cc_dir + "/" + self._builds[b].get_build_id()
                        dpis += " " + self._builds[b].get_build_id() + "/pgopti.dpi"
                        if spi == "":
                            spi = self._builds[b].get_build_id() + "/pgopti.spi"
                        self._ssh.ssh(system=self._system, platform=self._platform, cmd=self._module_cmd + "profmerge",
                                      server_path=True, path=cc_path)
        self._spi = spi
        if spi == "":
            return False
        return self._ssh.ssh(system=self._system, platform=self._platform, cmd=self._module_cmd + "profmerge " + dpis,
                             server_path=True, path=remote_cc_dir)

    def codecov(self):
        return self._ssh.ssh(system=self._system, platform=self._platform,
                             cmd=self._module_cmd + "codecov -srcroot " + self.alya_path() + " -spi " + self._spi,
                             server_path=True, path=remote_cc_dir)

    def get_files(self):
        critical_command("mkdir -p " + cc_report_dir)
        if not self._ssh.rsync_get(system=self._system, platform=self._platform,
                                   remote=remote_cc_dir + "/CODE_COVERAGE.HTML", local=cc_report_dir, delete=True,
                                   server_path=True, critical=True):
            raise Exception
        if not self._ssh.rsync_get(system=self._system, platform=self._platform, remote=remote_cc_dir + "/CodeCoverage",
                                   local=cc_report_dir, delete=True, server_path=True, critical=True):
            raise Exception

    def postprocess(self, _print):
        print("\tSetting up input file list...")
        self.set_html_files()
        print("\tBuilding code coverage summary...")
        self.summary()
        self.details(True, _print=_print)
        self.details(False, _print=_print)

    def set_html_files(self):
        files = command("grep HTML " + cc_report_dir + "/CODE_COVERAGE.HTML | cut -d\"\\\"\" -f2", output=True)
        files = files.split("\n")
        self._summary = cc_report_dir + "/" + files[0]
        self._covered = cc_report_dir + "/" + files[1]
        self._uncovered = cc_report_dir + "/" + files[2]

    def summary(self):
        data = command("grep \"TD ALIGN\" " + self._summary + " | cut -d\">\" -f2 | sed 's/<\/TD//' " +
                       "| sed 's/ //'", output=True)
        data = data.split("\n")
        d = []
        i = 0
        for type in "files", "functions", "blocks":
            c = {}
            c["type"] = type
            c["total"] = int(data[0 + i].replace(",", ""))
            c["covered"] = int(data[1 + i].replace(",", ""))
            c["uncovered"] = int(data[2 + i].replace(",", ""))
            c["coverage"] = float(data[3 + i])
            if type == "blocks":
                self._codecoverage = c["coverage"]
            i += 4
            d.append(c)
        self._report["summary"] = d

    def details(self, covered, _print=True):
        if covered:
            print("Building code coverage details (covered files)...")
            input = self._covered
        else:
            print("Building code coverage details (uncovered files)...")
            input = self._uncovered

        files = command("cat " + input + ' | grep title | grep "\.f90" | ' +
                        "cut -d\">\" -f3 | sed 's/<\/a//' ", output=True)
        files = files.split("\n")
        paths = command("cat " + input + ' | grep title | grep "\.f90" | ' +
                        "cut -d\"\\\"\" -f6", output=True)
        paths = paths.split("\n")
        url = command("cat " + input + ' | grep title | grep "\.f90" | ' +
                      "cut -d\"\\\"\" -f4", output=True)
        url = url.split("\n")
        data = command("grep \"TD ALIGN\" " + input + " | grep -v title | cut -d\">\" -f2 | sed 's/<\/TD//' " +
                       "| sed 's/ //'", output=True)
        data = data.split("\n")
        self._total = len(files) - 1
        for i in range(0, self._total):
            f = {}
            if files[i] == "":
                continue
            f["name"] = files[i]
            if _print:
                print("File: " + f["name"])
            path = paths[i].split("alya/", 1)[1]
            f["path"] = path
            realPath = self.alya_realpath(path)
            f["realPath"] = realPath
            f["url"] = url[i]
            r = [0, 0, 0]
            f["modified"] = self.is_modified(realPath)
            r = self.lines(f["name"], realPath, url[i])
            f["covered"] = covered
            if covered:
                f["functions"] = int(data[0 + (i * 6)].replace(",", ""))
                f["coveredFunctions"] = int(data[1 + (i * 6)].replace(",", ""))
                f["functionCoverage"] = float(data[2 + (i * 6)])
                f["blocks"] = int(data[3 + (i * 6)].replace(",", ""))
                f["coveredBlocks"] = int(data[4 + (i * 6)].replace(",", ""))
                f["blockCoverage"] = float(data[5 + (i * 6)])
                f["newLines"] = r[0]
                f["coveredNewLines"] = r[1]
                f["uncoveredNewLines"] = r[2]
            else:
                f["functions"] = int(data[0 + (i * 2)].replace(",", ""))
                f["coveredFunctions"] = 0
                f["functionCoverage"] = 0
                f["blocks"] = int(data[1 + (i * 2)].replace(",", ""))
                f["coveredBlocks"] = 0
                f["blockCoverage"] = 0
                f["newLines"] = r[0]
                f["coveredNewLines"] = r[1]
                f["uncoveredNewLines"] = r[2]
            self._report["files"].append(f)

    def lines(self, file, path, url):
        return self.lines_git(file, path, url)

    def alya_realpath(self, path):
        self.cd_push_alya()
        realpath = command("realpath " + path, output=True).strip()
        self.cd_pop_alya()
        return realpath

    def is_modified(self, path):
        self.cd_push_alya()
        modified = not (command("git diff --exit-code " + self._cc_revision + " -- " + path))
        self.cd_pop_alya()
        return modified

    def lines_git(self, file, path, url):
        uncovered_new_lines = 0
        covered_new_lines = 0
        try:
            self.cd_push_alya()
            logger.debug("IN ALYA")
            revisions_master = command(
                "git blame " + self._cc_revision + " -- " + path + ' | cut -d" " -f1 | sort | uniq | xargs',
                output=True).strip()
            logger.debug("BLAME OK")
            revisions_master = revisions_master.split(" ")
            logger.debug("SPLIT OK")
            revisions_branch = command("git blame " + path + ' | cut -d" " -f1 | xargs', output=True).strip()
            lines = revisions_branch.split(" ")
            url2 = cc_report_dir + "/CodeCoverage/" + url.replace(".HTML", "_SRC.HTML")
            i = 1
            self.cd_pop_alya()
            for line in lines:
                if line not in revisions_master:
                    color = "green"
                    grep = command("grep -nr \"name=\\\"l" + str(i) + "\\\"\" " + url2 + " | cut -d : -f 1",
                                   output=True).strip()
                    runend = command("sed -n " + grep + "p " + url2 + " | grep \"call runend\"",
                                     output=True).strip() not in ""
                    # block
                    uncovered = command("sed -n " + grep + "p " + url2 + " | grep \"background-color: #ffff99\"",
                                        output=True).strip() not in ""
                    # subroutine
                    if not uncovered:
                        uncovered = command("sed -n " + grep + "p " + url2 + " | grep \"background-color: #ffcccc\"",
                                            output=True).strip() not in ""
                    # partial block
                    if not uncovered:
                        uncovered = command("sed -n " + grep + "p " + url2 + " | grep \"background-color: #fafad2\"",
                                            output=True).strip() not in ""
                    # is covered?
                    if uncovered:
                        uncovered_new_lines += 1
                        color = "red"
                        if runend:
                            color = "blue"
                        self._status = False
                    else:
                        covered_new_lines += 1
                    command("sed -i -e " + grep + "'s/^/<font color=\\\"" + color + "\\\"><strong>/' " + url2)
                    command("sed -i -e " + grep + "'s/$/<\/strong><\/font>/' " + url2)
                i += 1
        except:
            logger.warning("Code coverage: file " + file + " line highlighting failed")
        r = [covered_new_lines + uncovered_new_lines, covered_new_lines, uncovered_new_lines]
        if uncovered_new_lines > 0:
            self._failed += 1
        return r

    def cd_push_alya(self):
        os.chdir(self._current_path + "/" + alya_dir)
        logger.debug(command("pwd -P", output=True))

    def cd_pop_alya(self):
        os.chdir(self._current_path)