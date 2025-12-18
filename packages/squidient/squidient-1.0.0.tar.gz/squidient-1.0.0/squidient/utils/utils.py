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



# -*- coding: utf-8 -*-
import json
import subprocess as subp
import signal
from .log import *
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from shutil import copyfile

logger = logging.getLogger(logging_context)
jtitle = "alyacicd-"


def exist_json(name):
    """
       Test if Json file exist
    """
    return os.path.isfile(name)


def open_critical_json(name):
    """
        Open a Json file.
    """
    try:
        with open(name) as json_data:
            d = json.load(json_data)
    except IOError:
        logger.error("Could not open the JSON config file: "+name)
        raise
    except ValueError:
        logger.error("File format Error in the JSON config file: "+name)
        raise
    except Exception:
        logger.error("Error while opening the JSON file: "+name)
        raise
    else:
        logger.debug("JSON "+name+" file loaded")
        return d


def open_json(name):
    """
        Open a Json file.
    """
    try:
        with open(name) as json_data:
            d = json.load(json_data)
    except IOError:
        logger.warning("Could not open the JSON config file: "+name)
        return False
    except ValueError:
        logger.warning("File format Error in the JSON config file: "+name)
        return False
    except Exception:
        logger.warning("Error while opening the JSON file: "+name)
        return False
    else:
        logger.debug("JSON "+name+" file loaded")
        return d


def save_json(d, name):
    """
        Save a json file
    """
    if(type(d) != type({})):
        logger.error("Date type is not a dict")
        raise TypeError("First parameter data type expected: dict " +
                        "but find: "+type(d))
    try:
        with open(name, 'w') as fp:
            json.dump(d, fp, indent=4, sort_keys=True)
    except IOError:
        logger.error("Could not open the JSON config file: "+name)
        raise
    except Exception:
        logger.error("Error while opening the JSON file: "+name)
        raise
    else:
        return 1


def command(line, stdout=False, output=False, timeout=1200, silent=False):
    """
        Execute a shell command
    """
    if not silent:
        logger.debug("Executing command: "+line)
    else:
        logger.debug("Executing silent command")
    if(output):
        stdout = True

    if not(stdout):
        line += ""

    if(output):
        line += ""
        output = ""
        try:
            p = subp.Popen(line,
                           stdout=subp.PIPE,
                           stderr=subp.STDOUT,
                           shell=True)

            output, err = p.communicate(timeout=timeout)
        except subp.TimeoutExpired:
            if not silent:
                logger.warning("Timed out! command: " + line)
            else:
                logger.warning("Timed out! silent command")
            os.kill(p.pid, signal.SIGTERM)
            output, err = p.communicate()
            return output.decode('utf-8')+"\nEXECUTION TIME OUT"
        else:
            if p.returncode != 0:
                if not silent:
                    logger.error("Failed to execute the command: "+line)
                else:
                    logger.error("Failed to execute silent command")
            return output.decode('utf-8')

    try:
        p = subp.Popen(line, stdout=subp.PIPE, shell=True, stderr=subp.PIPE)
        output, err = p.communicate(timeout=timeout)
    except subp.TimeoutExpired:
        if not silent:
            logger.warning("Timed out! command: "+line)
        else:
            logger.warning("Timed out! silent command")
        os.kill(p.pid, signal.SIGTERM)
        return False
    else:
        if p.returncode != 0:
            if not silent:
                logger.error("Failed to execute the command: "+line)
            else:
                logger.error("Failed to execute silent command")
            return False
    return True


def async_command(line, critical=False):
    """
        Execute a shell command
    """
    if not critical:
        line += " || :"
    logger.debug("Executing asynchronous command: "+line)
    try:
        process = subp.Popen(line, stdout=subp.PIPE, shell=True, stderr=subp.PIPE)
    except:
        return None
    return process


def async_wait(process):
    output, err = process.communicate()
    if process.returncode != 0:
        logger.error("Failed to execute the async command")
        return False
    return True


def async_poll(process):
    if process.poll() is not None:
        return True
    else:
        return False


def critical_command(line, silent=False):
    """
        Execute a shell command
    """
    if not silent:
        logger.debug("Executing command: "+line)
    else:
        logger.debug("Executing silent command")
    err = subp.call([line+" > /dev/null 2>&1 "], shell=True)
    if err:
        if not silent:
            logger.error("Failed to execute the command: "+line)
            silent_line_mngt = line
        else:
            logger.error("Failed to execute silent command")
            silent_line_mngt = "silent command"
        raise RuntimeError("An error has been detected during the " +
                           "execution of: " + silent_line_mngt)
    return True


def read_text_file(file):
    f = open(file, 'r', errors="replace")
    data = f.read()
    f.close()
    return data


def write_text_file(file, data):
    f = open(file, 'w')
    f.write(data)
    f.close()


def send_email(html, fr, to, tag, copy=None):
    # Create message container - the correct MIME type is multipart/alternative
    msg = MIMEMultipart('alternative')
    if tag == "":
        msg['Subject'] = "[AlyaTestSuite] Report Test Email"
    else:
        msg['Subject'] = "[AlyaTestSuite][" + tag + "] Report Test Email"
    msg['From'] = fr
    to_list = [to, 'damien.dosimont@bsc.es']
    msg['To'] = ", ".join(to_list)
    if copy is not None:
        msg['CC'] = copy
    part2 = MIMEText(html, 'html', "utf-8")
    msg.attach(part2)
    s = smtplib.SMTP_SSL('mail.bsc.es', port=465)
    s.sendmail(fr, to_list, msg.as_string())
    s.quit()


def copy_json(source, destination):
    """
       Copy a Json file
    """
    copyfile(source, destination)


def config_file_format():
    data = open_json("version/version.json")
    return data["fileFormat"]


def json2js(variable, json):
    js = json.replace(".json", ".js")
    command("echo \"" + variable + "=\" >" + js)
    command("cat " + json + ">>" + js)


def is_option(value, short, long=""):
    return value == short or (long != "" and value == long)


def percent_encoding(str):
    str2 = str.replace('!', '%21')
    str2 = str2.replace('#', '%23')
    str2 = str2.replace('$', '%24')
    str2 = str2.replace('&', '%26')
    str2 = str2.replace("'", '%27')
    str2 = str2.replace('(', '%28')
    str2 = str2.replace(')', '%29')
    str2 = str2.replace('*', '%2A')
    str2 = str2.replace('+', '%2B')
    str2 = str2.replace(',', '%2C')
    str2 = str2.replace('/', '%2F')
    str2 = str2.replace(':', '%3A')
    str2 = str2.replace(';', '%3B')
    str2 = str2.replace('=', '%3D')
    str2 = str2.replace('?', '%3F')
    str2 = str2.replace('@', '%40')
    str2 = str2.replace('[', '%5B')
    str2 = str2.replace(']', '%5D')
    return str2


def duration2str(start, end):
    duration = int(end - start)
    return secondstotime(duration)


def sum(time1, time2):
    seconds1 = timetosecond(time1)
    seconds2 = timetosecond(time2)
    return secondstotime(seconds1 + seconds2)


def timetosecond(time):
    h, m, s = time.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def secondstotime(seconds):
    h = int(seconds/3600)
    m = int(seconds/60) - (h * 60)
    s = seconds - (m * 60) - (h * 3600)
    if h < 10:
        h = "0" + str(h)
    else:
        h = str(h)
    if m < 10:
        m = "0" + str(m)
    else:
        m = str(m)
    if s < 10:
        s = "0" + str(s)
    else:
        s = str(s)
    return h + ":" + m + ":" + s


def timestamp2datetime(timestamp):
    return datetime.fromtimestamp(timestamp)


def infinitewtime():
    return (datetime(year=datetime.now().year+1000, month=1, day=1) - datetime.now()).total_seconds()/3600


def largewtime():
    return (datetime(year=datetime.now().year+100, month=1, day=1) - datetime.now()).total_seconds()/3600


def wtime(time):
    return max((time - datetime.now()).total_seconds() / 3600, 0)