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
import re


class Compare:

    # _____________________________________
    def __init__(self, base, test, method, tolerance, rows=None, cols=None):
        logger.debug("Comparing files base: " + base + " and test: " + test)
        self._base = base
        self._test = test
        self._method = method
        self._tolerance = tolerance
        self._status = True
        self._error = "OK"
        if method not in ['absolute', 'relative', 'power', 'diff']:
            raise Exception('Unknown tolerance method: {}'.format(method))
        elif method in ['absolute','relative']:
            try:
                self._tolerance = float(self._tolerance)
            except:
                logger.warning("Tolerance parameter is not a float")
                self._status = False
                self._error = "parameter"
        elif method == 'power':
            try:
                self._tolerance = int(self._tolerance)
            except:
                logger.warning("Tolerance parameter is not an integer")
                self._status = False
                self._error = "parameter"
        self._baseContent = []
        self._testContent = []
        self._maxPower = 0
        self._maxAbs = 0
        self._maxRel = 0
        self._currentPower = 0
        self._currentAbs = 0
        self._currentRel = 0
        self._differences = 0
        self._total = -1
        self._rows = rows
        self._cols = cols

    def compare(self):
        if self._status:
            if self._method in "diff":
                self._status = command("diff " + self._base + " " + self._test)
                if not self._status:
                    self._error = "diff"
            elif self._method in ["power", "absolute", "relative"]:
                if self._read():
                    if not command("diff " + self._base + " " + self._test):
                        self.compare_all()
        return self.get_res()

    def get_res(self):
        res = {}
        res["maxPower"] = self._maxPower
        res["maxAbs"] = self._maxAbs
        res["maxRel"] = self._maxRel
        res["differences"] = self._differences
        res["total"] = self._total
        res["status"] = self._status
        res["error"] = self._error
        return res

    # _____________________________________
    def _read(self):
        """
            Read the input files for comparison and take only
            the data to compare
        """

        logger.debug("Reading base: " + self._base)
        with open(self._base) as f:
            for line in f:
                if line[0] == '#':
                    continue
                values = re.findall("-?\d\.\d\d\d\d\d\d\d\dE[+-]\d\d\d", line)
                if values != []:
                    self._baseContent.append(values)

        logger.debug("Reading test: " + self._test)
        with open(self._test) as f:
            for line in f:
                if line[0] == '#':
                    continue
                values = re.findall("-?\d\.\d\d\d\d\d\d\d\dE[+-]\d\d\d", line)
                if values != []:
                    self._testContent.append(values)

        if self._rows is None:
            logger.debug("Computing rows")
            rows = range(len(self._baseContent))
            logger.debug("There are " + str(len(self._baseContent)) + " rows")
            if len(self._baseContent) == 0:
                logger.warning("Base does not have rows!")
                self._status = False
                self._error = "empty base"

        else:
            logger.debug("Getting rows from json")
            rows = self._rows
        cols = {}
        self._total = 0
        for r in rows:
            if int(r) > len(self._baseContent) - 1:
                logger.warning("Row out of range: " + str(r))
                self._status = False
                self._error = "lines"
                return False
            if self._cols is None:
                cols[r] = range(len(self._baseContent[r]))
                self._total += len(cols[r])
            else:
                cols[r] = self._cols
                to_remove = []
                for c in cols[r]:
                    if int(c) > len(self._baseContent[r]) - 1:
                        logger.warning("Column out of range :" + str(c) + ", line :" + str(r))
                        to_remove.append(c)
                for t in to_remove:
                    cols[r].remove(t)
                self._total += len(cols[r])
        if self._rows is None and self._cols is None:
            if len(self._baseContent) == len(self._testContent):
                for base, test in zip(self._baseContent, self._testContent):
                    if len(base) != len(test):
                        logger.warning("Files do not have the same number of columns")
                        self._status = False
                        self._error = "columns"
                        return False
            else:
                logger.warning("Files do not have the same number of lines")
                self._status = False
                self._error = "lines"
                return False
        self._rows = rows
        self._cols = cols
        return self._status

    # _____________________________________
    def compare_all(self):
        """
            Compare all the values base vs test.
        """
        # Comparison
        for i in self._rows:
            for j in self._cols[i]:
                if not (self._compare(self._baseContent[i][j],
                                      self._testContent[i][j])):
                    self._differences = self._differences + 1
        # Result
        if self._differences > 0:
            self._status = False
            self._error = "tolerance"

    # _____________________________________
    def _compare(self, val1, val2):
        """
            Args:
                val1 (str): String value 1 to compare with value 2
                val2 (str): String value 2 to compare with value 1

        """
        self._computeCurrentAndMaxValues(val1, val2)
        if self._method == "absolute":
            return self._currentAbs <= self._tolerance
        elif self._method == "relative":
            return self._currentRel <= self._tolerance
        elif self._method == "power":
            if self._currentPower == 0:
                return True
            elif self._tolerance == 0:
                return False
            else:
                return self._currentPower >= self._tolerance

    # _____________________________________
    def _computeCurrentAndMaxValues(self, val1, val2):
            #Absolute difference
            diff = abs(float(val1) - float(val2))
            self._currentAbs = diff

            #Power
            exp1 = float("1.0" + val1[-5:])
            fval1 = float(val1) / exp1
            fval2 = float(val2) / exp1
            if diff == 0:
                self._currentPower = 0
            else:
                diff = abs(fval1 - fval2)
                for tol in range(8, 0, -1):
                    if diff <= 10 ** (-tol):
                        self._currentPower = tol
                        break

            #Relative difference
            denom = float(val1)
            if denom == 0.0:
                denom = float(val2)
                if denom == 0.0:
                    self._currentRel = 0
                    self._updateMax()
                    return
            diff = (abs(float(val1) - float(val2)) / abs(denom))
            self._currentRel = diff
            self._updateMax()

    # _____________________________________
    def _updateMax(self):
        if self._currentPower > 0 and ((self._currentPower < self._maxPower) or (self._maxPower == 0)):
            self._maxPower = self._currentPower
        if self._currentAbs > self._maxAbs:
            self._maxAbs = self._currentAbs
        if self._currentRel > self._maxRel:
            self._maxRel = self._currentRel
