#!/usr/bin/python3
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

import re
import sys
import socket
from typing import Optional, Sequence, Dict, Any

from .builds.predefinedbuild import *
from .builds.build import *

from pathlib import Path

# NOTE:
# This module is now import-safe: importing it will NOT execute the CLI logic.
# Use main(argv) to run it programmatically.


def line_jump():
    print()


def ask(question, options):
    while True:
        answer = input(question)
        if answer in options:
            return answer


def check_input(question, regex, fail_question, default=""):
    while True:
        answer = input(question)
        if answer == "":
            answer = default
            print("\033[1A" + default)
        if type(regex) is list:
            for r in regex:
                if re.match(r, answer):
                    return answer
        elif isinstance(regex, str):
            if re.match(regex, answer):
                return answer
        fail_answer = ask(fail_question + " do you want to continue?[y/n]",
                          ['y', 'n'])
        if fail_answer == 'y':
            return answer


def basic_input(question, default=""):
    answer = input(question)
    if answer == "":
        answer = default
        print("\033[1A" + default)
    return answer


def clean_value(value):
    if isinstance(value, str):
        value = value.replace(" ", "")
    return value


def save_field(field, value):
    config = open_json(config_file)
    value = clean_value(value)
    config[field] = value
    save_json(config, config_file)


def set_field(field, message, default, com=""):
    value = set_value(message, default, com)
    save_field(field, value)


def set_field_regex(field, message, regex, fail, default="", com=""):
    value = set_value_regex(message, regex, fail, default, com)
    save_field(field, value)


def set_value(message, default, com=""):
    if com == "":
        value = basic_input(message, default)
    else:
        value = com
    line_jump()
    return value


def set_value_regex(message, regex, fail, default="", com=""):
    if com == "":
        value = check_input(message, regex, fail, default)
    else:
        value = com
    line_jump()
    return value


def set_bsc_user(com=""):
    config = open_json(config_file)
    user = set_value_regex("Your Marenostrum 5 user:\n", r"bsc\d\d\d\d\d\d",
                           "This user does not look like a Marenostrum 5 user", "", com)
    config["systems"]["bsc"]["user"] = user
    save_json(config, config_file)


def set_bsc_project(com=""):
    config = open_json(config_file)
    project = set_value_regex("Your Marenostrum 5 project (ex: bsc21):\n", r"\w",
                              "This user does not look like a Marenostrum 5 project", "", com)
    config["systems"]["bsc"]["project"] = project
    save_json(config, config_file)


def set_bsc_accounts():
    config = open_json(config_file)
    project = config["systems"]["bsc"]["project"]
    for platform in config["systems"]["bsc"]["platforms"]:
        config["systems"]["bsc"]["platforms"][platform]["account"] = project
    save_json(config, config_file)


def set_bsc_path(com=""):
    config = open_json(config_file)
    user = config["systems"]["bsc"]["user"]
    project = config["systems"]["bsc"]["project"]
    default = "/gpfs/projects/" + project + "/" + user + "/ts/" + socket.gethostname()
    if com == "default":
        com = default
    config = open_json(config_file)
    config["systems"]["bsc"]["path"] = set_value("Please specify the path in MN4 where squidient will " +
                                                 "be executed:\n", default, com)
    save_json(config, config_file)


def set_alya_git_branch(com=""):
    tag = set_value("Please type the alya git branch\n" +
                    "For example:\n" +
                    "\tmaster\n" +
                    "\tdev\n" +
                    "\tbranch1\n", "master", com)
    config = open_json(config_file)
    config["tag"] = tag
    config["alyaGitRepository"]["branch"] = tag
    save_json(config, config_file)


def set_git_https_user(com=""):
    config = open_json(config_file)
    config["alyaGitRepository"]["user"] = set_value("Please type the alya git repository user (https):\n", "", com)
    save_json(config, config_file)


def set_gitlab_user(com=""):
    config = open_json(config_file)
    config["alyaGitRepository"]["user"] = set_value("Please type your gitlab user\n", "", com)
    save_json(config, config_file)


def set_cc_ref(com=""):
    config = open_json(config_file)
    config["cc"]["reference"] = set_value_regex("Please type the commit used as code coverage reference:\n" +
                                                "For example:\n" +
                                                "\t0f6c3439\n" +
                                                "\t0a604c815ead8bb5ebc5fd944c39ea9c31dbf694\n" +
                                                "\torigin/master\n", [r"\w{8}", r"\w{40}", "origin/master"],
                                                "This does not look like a git commit", "origin/master", com)


def set_builds(com=""):
    predefined_builds = {}
    config = open_json(config_file)
    builds = open_json(build_file)
    selectedBuilds = []
    for build in builds:
        testedBuild = Build(build)
        if testedBuild.get_system() in config["systems"]:
            selectedBuilds.append(build)
    if is_bsc_system():
        predefined_builds = PredefinedBuild("builds").get_pb()

    if com == "":
        print("Available builds:")
        print("----------------")
        if is_bsc_system():
            print("Presets:")
            print("\t- all        \n\t\tall the builds required to validate alya")
            print("\t- gpp        \n\t\tall the marenostrum 5 GPP builds required to validate alya")
            print("\t- amd        \n\t\tall the amd builds required to validate alya")
            print("\t- gnu        \n\t\tall the gnu builds (gpp only)")
            print("\t- oneapi     \n\t\tall the oneapi builds (gpp only)")
            print("\t- benchmarks \n\t\tall the benchmarks builds")
        print("Unitary:")
        for build in selectedBuilds:
            print("\t- " + build)
        line_jump()
        b = input("Choose one or more builds:\n")
    else:
        b = com
    b = b.split(" ")
    if b[0] == '':
        b[0] = "cmake-amd-gnu-10.2.0-i4"
        if b[0] not in selectedBuilds:
            b[0] = selectedBuilds[0]

    config["staging"]["builds"] = []

    for a in predefined_builds:
        if a in b:
            b.extend(predefined_builds[a])
    b = set(b)
    for build in b:
        if build in predefined_builds:
            continue
        if build not in builds:
            print("Error: " + build + " is not a valid option")
        else:
            print("Build: " + build + " added correctly")
            config["staging"]["builds"].append(build)
    line_jump()
    save_json(config, config_file)


def set_cc(com=""):
    config = open_json(config_file)
    ccs = open_json(cc_file)
    try:
        ref = config["cc"]["reference"]
    except:
        ref = None
    if com == "":
        print("Available code coverage configurations:")
        print("----------------")
        for cc in ccs:
            print("\t- " + cc)
        line_jump()
        c = input("Choose a code coverage configuration:\n")
    else:
        c = com
    if c == '':
        c = None
    if c is not None:
        config["cc"] = ccs[c]
        if ref is not None:
            config["cc"]["reference"] = ref
        else:
            config["cc"]["reference"] = "master"
    else:
        config["cc"] = {"tool": "none"}
    save_json(config, config_file)


def set_systems(com=""):
    config = open_json(config_file)
    systems = {}
    if com == "":
        print("Available systems:")
        print("----------------")
        for system in config["systems"]:
            print("\t- " + system)
        line_jump()
        s = input("Choose one or more systems:\n")
    else:
        s = com
    s = s.split(" ")
    if s[0] == '':
        s[0] = "bsc"

    for system in s:
        if system not in config["systems"]:
            print("Error: " + system + " is not a valid option")
        else:
            print("System: " + system + " added correctly")
            systems[system] = config["systems"][system]
    line_jump()
    config["systems"] = systems
    save_json(config, config_file)


def get_systems():
    config = open_json(config_file)
    return config["systems"]


def is_bsc_system():
    config = open_json(config_file)
    return "bsc" in config["systems"]


def has_system(system):
    return system in get_systems()


def set_benchmarks(com=""):
    config = open_json(config_file)
    benchmarks = open_json(benchmark_file)
    benchmark_tests = []
    for benchmark in benchmarks:
        benchmark_tests.append(benchmark)
    config["benchmarks"]["tests"] = benchmark_tests
    save_json(config, config_file)


def set_version():
    config = open_json(config_file)
    config["fileFormat"] = config_file_format()
    save_json(config, config_file)


def generate_json():
    predefined_benchmarks = PredefinedBuild("benchmarks").get_pb()
    predefined_builds = PredefinedBuild("builds").get_pb()
    config = {}
    # systems
    config["systems"] = open_json(system_file)
    # repository
    config["alyaGitRepository"] = {}
    config["alyaGitRepository"]["branch"] = "master"
    config["alyaGitRepository"]["https"] = "https://alya.gitlab.bsc.es/alya/alya.git"
    config["alyaGitRepository"]["ssh"] = "git@alya.gitlab.bsc.es:alya/alya.git"
    config["alyaGitRepository"]["user"] = ""
    # alamak
    config["alamak"] = {}
    config["alamak"]["enable"] = False
    config["alamak"]["branch"] = "main"
    config["alamak"]["revision"] = None
    config["alamak"]["path"] = "alya/extern/alamak"
    # benchmarks
    config["benchmarks"] = {}
    config["benchmarks"]["builds"] = predefined_benchmarks["all"]
    config["benchmarks"]["tests"] = []
    config["benchmarks"]["lowDiskUsage"] = True
    # staging
    config["staging"] = {}
    config["staging"]["builds"] = predefined_builds["fast"]["amd"]
    # various
    config["fileFormat"] = -1
    config["tag"] = "master"
    config["installation"] = False
    config["flex"] = False
    config["clean"] = False
    config["merge"] = True
    config["cleanLog"] = True
    config["cc"] = {}
    config["cc"]["reference"] = "master"
    # db
    config["db"] = {}
    config["db"]["enable"] = False
    config["db"]["user"] = "alya_user"
    config["db"]["host"] = "cardinal.bsc.es"
    config["db"]["database"] = database_name["test"]
    # Gitlab
    config["api"] = ""
    config["scp_legacy"] = False
    save_json(config, config_file)


def gitlab_config(pipeline, directory, alya_ref, alya_branch, flex=False, platform="gpp", hosts=None, install=False,
                  type=None, api=None, reservation=False, project=None, alamak=False, alamak_branch=None,
                  alamak_revision=None):
    if hosts is None:
        hosts = {}

    predefined_benchmarks = PredefinedBuild("benchmarks").get_pb()
    predefined_builds = PredefinedBuild("builds").get_pb()
    _platform = platform
    _hosts = hosts

    print("Generating json")
    generate_json()
    config = open_json(config_file)
    print("Configuring repository")
    if alya_branch == "":
        alya_branch = alya_ref

    # repository
    config["alyaGitRepository"]["branch"] = alya_ref
    config["alyaGitRepository"]["user"] = "alya_CICD"

    # alamak
    config["alamak"]["enable"] = alamak
    config["alamak"]["branch"] = alamak_branch
    config["alamak"]["revision"] = alamak_revision

    # staging
    print("Configuring staging builds")
    config["staging"]["builds"] = predefined_builds["all"]
    if type is not None:
        if type == "fast":
            config["staging"]["builds"] = predefined_builds["fast"][_platform]
        elif type == "gnu":
            config["staging"]["builds"] = []
            for a in predefined_builds["gpp"]:
                if "gnu" in a:
                    config["staging"]["builds"].append(a)
        elif type == "oneapi":
            config["staging"]["builds"] = []
            for a in predefined_builds["gpp"]:
                if "oneapi" in a:
                    config["staging"]["builds"].append(a)
        elif type in predefined_builds:  # mn/mn4, p9, amd, etc.
            config["staging"]["builds"] = predefined_builds[type]
        if type in predefined_benchmarks:
            config["benchmarks"]["builds"] = predefined_benchmarks[type]
        print("Saving...")
        save_json(config, config_file)
        print("Configuring system")
        set_systems("bsc")
        config = open_json(config_file)

    # various
    print("Configuring flex")
    config["flex"] = flex
    print("Configuring clean log")
    config["cleanLog"] = False
    print("Configuring system")
    config["systems"]["bsc"]["user"] = "alya_cicd"
    config["systems"]["bsc"]["project"] = "bsc21"
    if pipeline != "0":
        config["systems"]["bsc"]["path"] = "/gpfs/projects/bsc21/alya_cicd_fs/ts/gitlab/" + directory
        config["tag"] = alya_branch + " - " + pipeline
    else:
        config["systems"]["bsc"]["path"] = "/gpfs/projects/bsc21/alya_cicd/ts/gitlab_local"
        config["tag"] = alya_branch

    try:
        config["systems"]["bsc"]["host"] = _hosts["gpp"]
    except:
        pass

    for system in config["systems"]:
        for host in _hosts:
            if host in config["systems"][system]["platforms"]:
                config["systems"][system]["platforms"][host]["host"] = _hosts[host]

    try:
        config["systems"]["bsc"]["platforms"]["gpp"]["queues"]["benchmarks"] = "gp_bsccase"
    except:
        pass

    print("Configuring db default")
    config["db"]["user"] = "alya_cicd"
    config["db"]["enable"] = True
    config["db"]["database"] = database_name["production"]

    if install:
        print("Configuring installation")
        config["installation"] = True
        config["staging"]["builds"] = predefined_builds["install"]

    if api:
        print("Configuring api")
        config["api"] = api

    print("Saving...")
    save_json(config, config_file)
    print("Configuring bsc accounts")
    set_bsc_accounts()
    print("Configuring code coverage")
    set_cc("gcovr")
    print("Configuring benchmarks")
    set_benchmarks()
    print("Configuring execution type")
    set_mr(type)

    config = open_json(config_file)
    print("Configuring project queues and accounts")
    if project is not None:
        config_project = open_json(project_file)
        if project not in config_project:
            print("Project " + project + " not found")
            exit(1)
        config_project = config_project[project]
        for platform in config_project["systems"]["bsc"]["platforms"]:
            if platform in config["systems"]["bsc"]["platforms"]:
                if "account" in config_project["systems"]["bsc"]["platforms"][platform]:
                    config["systems"]["bsc"]["platforms"][platform]["account"] = (
                        config_project)["systems"]["bsc"]["platforms"][platform]["account"]
                for queue in config_project["systems"]["bsc"]["platforms"][platform]["queues"]:
                    if queue in config["systems"]["bsc"]["platforms"][platform]["queues"]:
                        config["systems"]["bsc"]["platforms"][platform]["queues"][queue] = (
                            config_project)["systems"]["bsc"]["platforms"][platform]["queues"][queue]

        print("Saving...")
        save_json(config, config_file)
    else:
        print("Setting reservation")
        set_reservation(reservation)

    print("Setting version...")
    set_version()


def set_mr(type):
    if type is not None:
        if type == "mr":
            config = open_json(config_file)
            config["db"]["user"] = "alya_user"
            config["db"]["database"] = database_name["test"]
            config["benchmarks"]["tests"] = ["elbow", "sphere-16M"]
            save_json(config, config_file)


def set_reservation(boolean):
    config = open_json(config_file)
    # config["systems"]["bsc"]["platforms"]["gpp"]["reservation"]["enable"] = boolean
    save_json(config, config_file)


def set_alamak(boolean):
    config = open_json(config_file)
    config["alamak"]["enable"] = boolean
    save_json(config, config_file)


def set_alamak_branch(com=""):
    tag = set_value("Please type the alamak git branch\n" +
                    "For example:\n" +
                    "\tmain\n" +
                    "\tdev\n" +
                    "\tbranch1\n", "main", com)
    config = open_json(config_file)
    config["tag"] = tag
    config["alamak"]["branch"] = tag
    save_json(config, config_file)


def ensure_initialized(root: Path = Path.cwd()) -> None:
    marker = root / ".squidient-initialized"
    if not marker.exists():
        raise RuntimeError(
            "This directory is not initialized.\n"
            "Please run `squidient init` first."
        )

def configure_help():
    print("squidient configuration options:")
    print("[argument] between brackets are optional")
    line_jump()
    print("\t-h  | --help                          Show this information")
    print("Global Configuration")
    print("\t-a  | --all                           Configure the main options")
    print("\t-r  | --re                            Reconfigure the main options")
    print("\t-A  | --ALL                           Configure all the options")
    print("\t-s  | --systems          [systems]    Change the set of systems")
    print("\t-b  | --builds           [builds]     Change the set of builds")
    print("\t-p  | --path             [path]       Change the server path")
    print("Alamak")
    print("\t--alamak                              Enable alamak")
    print("Git configuration")
    print("\t-u  | --git-user         [git-user]   Set up the git user (gitlab/https user)")
    print("\t-br | --git-branch       [git-branch] Select alya git branch/commit/tag")
    print("Coverage configuration")
    print("\t-c  | -c                 [tool]       Define code coverage tool")
    print("\t-cc-ref  | --cc-ref      [git-commit] Define code coverage reference commit")
    print("GitLab configuration")
    print("\t--gitlab                              Enable GitLab features")
    print("\t--pipeline:[pipeline]                 Pipeline number")
    print("\t--directory:[directory]               Change directory name")
    print("\t--branch:[reference]                  alya reference")
    print("\t--alya:[reference]                    alya reference (priority inferior to branch)")
    print("\t--flex                                Enable flex queue")
    print("\t--install                             Enable install mode")
    print("\t--platform:[platform]                 Choose platform for fast build")
    print("\t--host:[host:value]                   Associate an host with a value")
    print("\t--type:[type]                         Choose execution type")
    print("\t--api:[api]                           Define GitLab API")
    print("\t--alamak-branch:[branch]              Define which alamak branch to use")
    print("\t--alamak-revision:[revision]          Define which alamak revision to use")
    print("\t--reservation                         Enable reservation")
    line_jump()


def _run_cli(argv: Sequence[str]) -> int:
    # NOTE: This function contains the previous top-level execution logic.

    ensure_initialized()

    if not exist_json(config_file):
        generate_json()

    base_config = open_json(config_file)
    argument = ""

    if base_config["fileFormat"] == -1:
        print("This is your first use of squidient, it requires a full configuration")
        if len(argv) < 1:
            option = "--all"
        elif not is_option(argv[0], "-A", "--ALL") and not is_option(argv[0], "--gitlab", "--gitlab"):
            print("Ignoring arguments\n")
            option = "--all"
        else:
            option = argv[0]
        save_json(base_config, config_file)
    else:
        if len(argv) < 1:
            configure_help()
            return 0
        option = argv[0]
        if len(argv) == 2:
            argument = argv[1]
        else:
            print("----------------------------------------------------")
            print("       WELCOME TO SQUIDIENT CONFIGURATION           ")
            print("----------------------------------------------------")
            line_jump()

    if is_option(option, "--gitlab"):
        print("Gitlab pipeline configuration")
        pipeline = "0"
        directory = "default"
        alya_ref = "master"
        alya_branch = ""
        flex = False
        platform = "gpp"
        hosts = {}
        install = False
        type = None
        api = None
        reservation = False
        project = None
        alamak = False
        alamak_branch = None
        alamak_revision = None

        for arg in argv[0:]:
            if "--pipeline:" in arg:
                pipeline = arg.replace("--pipeline:", "")
                print("\tPipeline " + pipeline)
            if "--directory:" in arg:
                directory = arg.replace("--directory:", "")
                if directory == "":
                    directory = "ts"
                print("\tDirectory " + directory)
            if "--alya:" in arg:
                alya_ref = arg.replace("--alya:", "")
                print("\talya_ref " + alya_ref)
            if "--branch:" in arg:
                alya_branch = arg.replace("--branch:", "")
                print("\talya_branch " + alya_branch)
            if "--flex" in arg:
                flex = True
                print("\tFlex enabled")
            if "--install" in arg:
                install = True
                print("\tInstall enabled")
            if "--platform:" in arg:
                platform = arg.replace("--platform:", "")
                print("\tPlatform " + platform)
            if "--host:" in arg:
                host = arg.split(":")[1]
                value = arg.split(":")[2]
                hosts[host] = value
            if "--type:" in arg:
                type = arg.replace("--type:", "")
                if type == "alamak":
                    alamak = True
                print("\tType " + type)
            if "--api:" in arg:
                api = arg.replace("--api:", "")
                print("\tapi " + api)
            if "--reservation" in arg:
                reservation = True
                print("\tReservation enabled")
            if "--project:" in arg:
                project = arg.replace("--project:", "")
                print("\tProject " + project)
            if "--alamak-branch:" in arg:
                alamak_branch = arg.replace("--alamak-branch:", "")
            if "--alamak-revision:" in arg:
                alamak_revision = arg.replace("--alamak-revision:", "")

        gitlab_config(
            pipeline=pipeline,
            directory=directory,
            alya_ref=alya_ref,
            alya_branch=alya_branch,
            flex=flex,
            platform=platform,
            hosts=hosts,
            install=install,
            type=type,
            api=api,
            reservation=reservation,
            project=project,
            alamak=alamak,
            alamak_branch=alamak_branch,
            alamak_revision=alamak_revision,
        )
        return 0

    elif is_option(option, "-u", "--git-user"):
        set_git_https_user(argument)

    elif is_option(option, "-br", "--git-branch"):
        set_alya_git_branch(argument)

    elif is_option(option, "-c", "--cc"):
        set_cc(argument)

    elif is_option(option, "--cc-ref", "--cc-ref"):
        set_cc_ref(argument)

    elif is_option(option, "-p", "--path"):
        set_bsc_path(argument)
        set_bsc_path(argument)

    elif is_option(option, "-b", "--builds"):
        set_builds(argument)

    elif is_option(option, "-s", "--systems"):
        set_systems(argument)

    elif is_option(option, "-a", "--all"):
        generate_json()
        set_systems()
        if is_bsc_system():
            set_bsc_user()
            set_bsc_project()
            set_bsc_accounts()
            set_bsc_path("default")
        set_alya_git_branch()
        set_builds()
        set_cc()
        set_benchmarks()
        set_version()

    elif is_option(option, "-r", "--re"):
        set_alya_git_branch()
        set_bsc_path("default")
        set_builds()
        set_cc()
        set_benchmarks()
        set_version()

    elif is_option(option, "-A", "--ALL"):
        generate_json()
        set_systems()
        if is_bsc_system():
            set_bsc_user()
            set_bsc_project()
            set_bsc_accounts()
            set_bsc_path()
        set_git_https_user()
        set_alya_git_branch()
        set_cc_ref()
        set_builds()
        set_cc()
        set_benchmarks()
        set_version()

    elif is_option(option, "--alamak", "--alamak"):
        set_alamak(True)
        set_alamak_branch()

    elif is_option(option, "--reservation", "--reservation"):
        set_reservation(True)

    elif is_option(option, "-h", "--help"):
        configure_help()

    else:
        print(option + " is not a valid argument")
        configure_help()

    return 0


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


