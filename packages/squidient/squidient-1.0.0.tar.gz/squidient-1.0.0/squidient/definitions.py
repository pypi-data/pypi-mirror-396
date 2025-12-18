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


test_default_timeout = "00:01:00"
test_max_timeout = "00:05:00"
merged_max_timeout = "02:00:00"
queue_max_timeout = "02:00:00"
max_waiting_time = 2  # 2 hours
queue_test_sleep_before_get_launch_time = 30  # seconds
test_max_retry = 3
report_dir = "reports"
build_report_dir = report_dir + "/builds"
benchmark_build_report_dir = report_dir + "/benchmark_builds"
benchmark_test_report_dir = report_dir + "/benchmark_tests"
test_report_dir = report_dir + "/tests"
cc_report_dir = report_dir + "/cc"
xml_report_dir = report_dir + "/xml"
queue_report_dir = report_dir + "/queues"
terraform_dir = "terraform"
mpio2txt_bin = "mpio2txt"
actualize_time = 60
enable_svn = False
max_async_threads = 8
max_jobs_staging = 100
max_jobs_monitor = 50
max_jobs_debug = 10
check_jobs_every_normal = 30
check_jobs_every_debug = 10
config_file = "configuration.json"
build_file = "builds/builds.json"
cc_file = "builds/cc.json"
predefined_build_file = "builds/predefined.json"
system_file = "configurations/systems.json"
project_file = "configurations/projects.json"
test_file = "configurations/tests.json"
benchmark_file = "benchmarks/benchmarks.json"
squidient_reports = "/gpfs/projects/bsc21/squidient/reports"
watchdog_max_failures = 3
lock_file = "loc.k"
alya_dir = "alya"
alya_config_dir = "alya-config"
remote_bin_dir = "alya-bin"
remote_build_dir = "alya-builds"
remote_test_dir = "alya-tests"
benchmark_dir = "alya-benchmarks"
remote_cc_dir = "alya-cc"
remote_queue_dir = "alya-queues"
remote_ts_dir = "alya-testsuite"
cmake_link_dir = "ALYA_CMAKE_INSTALL_DIR"
max_advised_builds = 2
database_name = {"test": "rooster_test", "production": "rooster"}