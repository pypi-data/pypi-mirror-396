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



import mariasql
from ..utils.utils import *
from ..utils.message import *
import getpass
import json

logger = logging.getLogger(logging_context)


def db_string(string):
    return "'" + string.replace("\\\"", "") + "'"


class MonitorDB:

    def __init__(self, config, password=None, enable=True):
        self._enable = enable
        self._db_config = config["db"]
        self._user = self._db_config["user"]
        self._host = self._db_config["host"]
        self._database = self._db_config["database"]
        self._password = password
        self._session_id = 0
        self._builds = {}
        self._benchmarks = {}
        self._db = None

    def set_password(self):
        if not self._enable:
            return
        if self._password is None:
            self._password = getpass.getpass(prompt="Enter your password for the Benchmark MariaDB database (user: " + self._user + "):")

    def connect(self):
        if not self._enable:
            return
        #jump()
        #print("Connecting to the database")
        logger.debug("Connecting to the database")
        self.set_password()
        try:
            self._db = mariasql.MariaSQL(host=self._host, user=self._user, password=self._password, db=self._database)
        except:
            raise Exception("Cannot connect to the database !")
        #self._db.use(self._database)

    def disconnect(self):
        logger.debug("Disonnecting from the database")
        try:
            self._db.query("exit")
        except:
            logger.debug("Cannot disconnect from the database")

    def initialize_tables(self):
        if not self._enable:
            return
        #session table
        jump()
        self.connect()
        print("Initializing DB tables...")
        logger.debug("Initializing DB tables")
        logger.debug("Create DB session table")
        query = self._db.query("CREATE TABLE IF NOT EXISTS session (" +
                               "id SERIAL PRIMARY KEY, " +
                               "application VARCHAR(255) NOT NULL, " +
                               "sha CHAR(40) NOT NULL, " +
                               "short_sha VARCHAR(10) NOT NULL, " +
                               "start_date DATETIME NOT NULL, " +
                               "end_date DATETIME" +
                               ");")
        #build table
        logger.debug("Create DB build table")
        query = self._db.query("CREATE TABLE IF NOT EXISTS build (" +
                               "id SERIAL PRIMARY KEY, " +
                               "name VARCHAR(255) NOT NULL, " +
                               "compiler VARCHAR(255) NOT NULL, " +
                               "version VARCHAR(255) NOT NULL, " +
                               "system VARCHAR(255) NOT NULL, " +
                               "platform VARCHAR(255) NOT NULL, " +
                               "build JSON, " +
                               "configuration JSON" +
                               ");")
        #benchmark table
        logger.debug("Create DB benchmark table")
        query = self._db.query("CREATE TABLE IF NOT EXISTS benchmark (" +
                               "id SERIAL PRIMARY KEY, " +
                               "name VARCHAR(255) NOT NULL, " +
                               "elements BIGINT UNSIGNED, " +
                               "nodes BIGINT UNSIGNED" +
                               ");")
        #xp table
        logger.debug("Create DB xp table")
        query = self._db.query("CREATE TABLE IF NOT EXISTS xp (" +
                               "id SERIAL PRIMARY KEY, " +
                               "session BIGINT UNSIGNED NOT NULL, " +
                               "benchmark BIGINT UNSIGNED NOT NULL, " +
                               "build BIGINT UNSIGNED NOT NULL, " +
                               "job_id BIGINT UNSIGNED NOT NULL, " +
                               "start_date DATETIME NOT NULL, " +
                               "end_date DATETIME NOT NULL, " +
                               "mpi BIGINT UNSIGNED NOT NULL, " +
                               "openmp BIGINT UNSIGNED NOT NULL, " +
                               "env JSON" +
                               ");")
        #measure table
        logger.debug("Create DB measure table")
        query = self._db.query("CREATE TABLE IF NOT EXISTS measure (" +
                               "id SERIAL PRIMARY KEY, " +
                               "xp BIGINT UNSIGNED NOT NULL, " +
                               "code VARCHAR(255) NOT NULL, " +
                               "module CHAR(6) NOT NULL, " +
                               "function VARCHAR(255) NOT NULL, " +
                               "type VARCHAR(255) NOT NULL, " +
                               "parent_module CHAR(6) NOT NULL, " +
                               "parent_function VARCHAR(255) NOT NULL, " +
                               "parent_type VARCHAR(255) NOT NULL, " +
                               "category VARCHAR(255) NOT NULL, " +
                               "unit VARCHAR(25) NOT NULL, " +
                               "value DOUBLE NOT NULL" +
                               ");")
        # counter table
        logger.debug("Create DB counter table")
        query = self._db.query("CREATE TABLE IF NOT EXISTS counter (" +
                               "id SERIAL PRIMARY KEY, " +
                               "xp BIGINT UNSIGNED NOT NULL, " +
                               "type VARCHAR(255) NOT NULL, " +
                               "name VARCHAR(255) NOT NULL, " +
                               "date DATETIME NOT NULL, " +
                               "unit VARCHAR(25) NOT NULL," +
                               "value BIGINT UNSIGNED NOT NULL" +
                               ");")
        self.disconnect()

    def start_session(self, application, sha, short_sha):
        if not self._enable:
            return
        jump()
        self.connect()
        print("Starting DB session...")
        logger.debug("Starting DB session")
        query = ("INSERT INTO session(application, sha, short_sha, start_date)" + " VALUES (" + db_string(application) +
                 ", " + db_string(sha) + ", " + db_string(short_sha) + ", now());")
        logger.debug("Query: " + query)
        self._db.query(query)
        query = self._db.query("SELECT LAST_INSERT_ID();")
        self._session_id = query[0]["LAST_INSERT_ID()"]
        self.disconnect()

    def end_session(self):
        if not self._enable:
            return
        jump()
        self.connect()
        print("Ending DB session...")
        logger.debug("Ending DB session")
        query = "UPDATE session SET end_date = now() WHERE id = " + str(self._session_id) + ";"
        logger.debug("Query: " + query)
        self._db.query(query)
        self.disconnect()

    def add_build(self, name, compiler, version, system, platform, build, configuration):
        if not self._enable:
            return
        self.connect()
        logger.debug("Adding DB build")
        json_build = json.dumps(build, sort_keys=True)
        json_configuration = json.dumps(configuration, sort_keys=True)
        logger.debug("Looking for existing DB build")
        query = ("SELECT id from build WHERE " +
                 "name = " + db_string(name) + " AND " +
                 "compiler = " + db_string(compiler) + " AND " +
                 "version = " + db_string(version) + " AND " +
                 "system = " + db_string(system) + " AND " +
                 "platform = " + db_string(platform) + " AND " +
                 "build = " + db_string(json_build) + " AND " +
                 "configuration = " + db_string(json_configuration)
                 )
        logger.debug("Query: " + query)
        query = self._db.query(query)
        for q in query:
            self._builds[name] = q["id"]
            logger.debug("DB build found")
            self.disconnect()
            return
        logger.debug("Inserting new DB build")
        query = ("INSERT INTO build(name, compiler, version, system, platform, build, configuration)" + " VALUES (" +
                 db_string(name) + ", " +
                 db_string(compiler) + ", " +
                 db_string(version) + ", " +
                 db_string(system) + ", " +
                 db_string(platform) + ", " +
                 db_string(json_build) + ", " +
                 db_string(json_configuration) +
                 ");")
        logger.debug("Query: " + query)
        self._db.query(query)
        query = self._db.query("SELECT LAST_INSERT_ID();")
        self._builds[name] = query[0]["LAST_INSERT_ID()"]
        self.disconnect()

    def add_benchmark(self, name, elements, nodes):
        if not self._enable:
            return
        self.connect()
        logger.debug("Adding DB benchmark")
        logger.debug("Looking for existing DB benchmark")
        query = ("SELECT id from benchmark WHERE " +
                 "name = " + db_string(name) + " AND " +
                 "elements = " + db_string(str(elements)) + " AND " +
                 "nodes = " + db_string(str(nodes))
                 )
        logger.debug("Query: " + query)
        query = self._db.query(query)
        for q in query:
            #The benchmark is already existing
            self._benchmarks[name] = q["id"]
            logger.debug("DB benchmark found")
            self.disconnect()
            return
        logger.debug("Inserting new DB benchmark")
        query = ("INSERT INTO benchmark(name, elements, nodes)" +
                 " VALUES (" + db_string(name) + ", " +
                 db_string(str(elements)) + ", " +
                 db_string(str(nodes)) +
                 ");")
        logger.debug("Query: " + query)
        self._db.query(query)
        query = self._db.query("SELECT LAST_INSERT_ID();")
        self._benchmarks[name] = query[0]["LAST_INSERT_ID()"]
        self.disconnect()

    def add_xp(self, benchmark, build, job_id, start_date, end_date, mpi, openmp, env):
        if not self._enable:
            return -1
        self.connect()
        json_env = json.dumps(env, sort_keys=True)
        logger.debug("Adding DB xp")
        query = ("INSERT INTO xp(session, benchmark, build, job_id, start_date, end_date, mpi, openmp, env)" +
                 " VALUES (" + str(self._session_id) + ", " +
                 str(self._benchmarks[benchmark]) + ", " +
                 str(self._builds[build]) + ", " +
                 str(job_id) + ", " +
                 db_string(str(timestamp2datetime(start_date))) + ", " +
                 db_string(str(timestamp2datetime(end_date))) + ", " +
                 str(mpi) + ", " +
                 str(openmp) + ", " +
                 db_string(json_env) +
                 ");")
        logger.debug("Query: " + query)
        self._db.query(query)
        query = self._db.query("SELECT LAST_INSERT_ID();")
        self.disconnect()
        return query[0]["LAST_INSERT_ID()"]

    def add_measure(self, xp_id, coupling, code, row):
        if not self._enable:
            return
        self.connect()
        try:
            module = row["module"]
            if len(module) > 6:
                module = module[0:6]
            function = row["function"]
            type = row["type"]
            parent_module = row["parent_module"]
            if len(parent_module) > 6:
                parent_module = parent_module[0:6]
            parent_function = row["parent_function"]
            parent_type = row["parent_type"]
            category = row["category"]
            value = row["value"]
            unit = row["unit"]
        except:
            self.disconnect()
            return
        logger.debug("Adding DB measure")
        c = code
        if not coupling:
            c = ""
        query = self._db.query("INSERT INTO measure(xp, code, module, function, type, parent_module, parent_function, parent_type, category, unit, value)" +
                               " VALUES (" + str(xp_id) + ", " +
                               db_string(c) + ", " +
                               db_string(module) + ", " +
                               db_string(function) + ", " +
                               db_string(type) + ", " +
                               db_string(parent_module) + ", " +
                               db_string(parent_function) + ", " +
                               db_string(parent_type) + ", " +
                               db_string(category) + ", " +
                               db_string(str(unit)) + ", " +
                               str(value) +
                               ");")
        self.disconnect()

    def add_counter(self, xp_id, type, counter):
        if not self._enable:
            return
        self.connect()
        try:
            name = counter["name"]
            date = counter["date"]
            value = counter["value"]
            unit = counter["unit"]
        except:
            self.disconnect()
            return
        logger.debug("Adding DB counter")
        query = self._db.query("INSERT INTO counter(xp, type, name, date, unit, value)" +
                               " VALUES (" + str(xp_id) + ", " +
                               db_string(type) + ", " +
                               db_string(name) + ", " +
                               db_string(str(timestamp2datetime(date))) + ", " +
                               db_string(str(unit)) + ", " +
                               str(value) +
                               ");")
        self.disconnect()
