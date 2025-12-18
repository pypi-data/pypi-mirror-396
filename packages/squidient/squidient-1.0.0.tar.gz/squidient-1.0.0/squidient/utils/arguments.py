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



from .utils import *


class Arguments:

    def __init__(self):
        self._test_directories = []
        self._test_list = []
        self._test_directory_flag = False
        self._test_list_flag = False
        self._start_flag = False
        self._finish_flag = False
        self._check_flag = False
        self._gitlab_flag = False
        self._gitlab_pipeline_flag = False
        self._gitlab_pipeline = []
        self._gitlab_token_flag = False
        self._gitlab_token = []
        self._db_password = ""
        self._db_password_flag = False
        self._generic_arg = []
        self._alamak_user_flag = False
        self._alamak_user = ""
        self._alamak_token_flag = False
        self._alamak_token = ""

    def parse(self, args):
        self.reset_test_flags()
        if args is not None:
            for arg in args:
                if is_option(arg, "-dp", "--db_password"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._db_password_flag = True
                    continue
                if is_option(arg, "-g", "--gitlab"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._gitlab_flag = True
                    continue
                if is_option(arg, "-p", "--pipeline"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._gitlab_pipeline_flag = True
                    continue
                if is_option(arg, "-k", "--token"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._gitlab_token_flag = True
                    continue
                if is_option(arg, "-s", "--start"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._start_flag = True
                    continue
                if is_option(arg, "-c", "--check"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._check_flag = True
                    continue
                if is_option(arg, "-f", "--finish"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._finish_flag = True
                    continue
                if is_option(arg, "-d", "--dirs"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._test_directory_flag = True
                    continue
                if is_option(arg, "-t", "--tests"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._test_list_flag = True
                    continue
                if is_option(arg, "--alamak-user"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._alamak_user_flag = True
                    continue
                if is_option(arg, "--alamak-token"):
                    self.reset_db_flags()
                    self.reset_test_flags()
                    self.reset_sync_flags()
                    self.reset_alamak_flags()
                    self._alamak_token_flag = True
                    continue
                if self._db_password_flag:
                    self._db_password = arg
                    continue
                if self._test_directory_flag:
                    self._test_directories.append(arg)
                    continue
                if self._test_list_flag:
                    self._test_list.append(arg)
                    continue
                if self._gitlab_pipeline_flag:
                    self._gitlab_pipeline.append(arg)
                    continue
                if self._gitlab_token_flag:
                    self._gitlab_token.append(arg)
                    continue
                if self._alamak_user_flag:
                    self._alamak_user = arg
                    continue
                if self._alamak_token_flag:
                    self._alamak_token = arg
                else:
                    self._generic_arg.append(arg)

    def reset_db_flags(self):
        self._db_password_flag = False

    def reset_test_flags(self):
        self._test_directory_flag = False
        self._test_list_flag = False

    def reset_sync_flags(self):
        self._start_flag = False
        self._finish_flag = False
        self._check_flag = False
        self._gitlab_pipeline_flag = False
        self._gitlab_token_flag = False

    def reset_alamak_flags(self):
        self._alamak_user_flag = False
        self._alamak_token_flag = False

    def get_test_directories(self):
        return self._test_directories

    def get_test_list(self):
        return self._test_list

    def get_start(self):
        return self._start_flag

    def get_check(self):
        return self._check_flag

    def get_finish(self):
        return self._finish_flag

    def get_gitlab(self):
        return self._gitlab_flag

    def get_gitlab_pipeline(self):
        return self._gitlab_pipeline

    def get_gitlab_token(self):
        return self._gitlab_token

    def get_db_password(self):
        return self._db_password

    def get_generic_arg(self):
        return self._generic_arg

    def get_alamak_user(self):
        return self._alamak_user

    def get_alamak_token(self):
        return self._alamak_token


