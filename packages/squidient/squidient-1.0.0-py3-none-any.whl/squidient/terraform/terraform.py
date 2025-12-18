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


from datetime import datetime
from sysconfig import get_platform

from ..definitions import config_file, terraform_dir
from ..utils.utils import open_json, command, critical_command, save_json, open_critical_json
from ..utils.message import *
from ..builds.build import *

import json
import re


def compute_systems():
    build_list = open_critical_json(config_file)["staging"]["builds"]
    systems = {}
    for build in build_list:
        b = Build(build)
        system = b.get_system()
        platform = b.get_platform()
        if system not in systems:
            systems[system] = []
        if platform not in systems[system]:
            systems[system].append(platform)
    return systems


class Terraform:

    def __init__(self):
        self._systems = open_json(config_file)["systems"]
        subsystems = compute_systems()
        jump()
        print_line()
        self._wait_cloud_init = {}
        self._configurations = {}
        self._errors = {}
        self._ready_platforms = {}
        self._last_checked_platforms = {}
        print("Looking for terraform configurations")
        for system in subsystems:
            self._configurations[system] = {}
            self._ready_platforms[system] = {}
            self._last_checked_platforms[system] = {}
            if "wait_cloud_init" in self._systems[system]:
               # print("\nSystem " + system + " will wait for , plaform - " + platform)
                self._wait_cloud_init[system] = self._systems[system]["wait_cloud_init"]
            for platform in subsystems[system]:
                if "terraform" in self._systems[system]["platforms"][platform]:
                    if "enable" in self._systems[system]["platforms"][platform]["terraform"]:
                        if self._systems[system]["platforms"][platform]["terraform"]["enable"]:
                            print("\nTerraform configuration enabled: system - " + system + ", platform - " + platform)
                            self._configurations[system][platform] = {}
                            self._ready_platforms[system][platform] = -2
                            self._last_checked_platforms[system][platform] = None
                            self._configurations[system][platform]["directory"] = terraform_dir + "/" + system + "/" + platform
                            self._configurations[system][platform]["sshKeyDirectory"] = self._configurations[system][platform]["directory"] + "/.ssh"
                            if "sshKeyName" in self._systems[system]["platforms"][platform]["terraform"]:
                                self._configurations[system][platform]["sshKeyName"] = self._systems[system]["platforms"][platform]["terraform"]["sshKeyName"]

    def create(self):
        print("Create platforms with Terraform")
        print("\tGenerate SSH keys")
        self.generate_ssh_key()
        try:
            print("\tTerraform init")
            self.terraform_init()
            if self.terraform_error_check():
                raise RuntimeError
            print("\tTerraform apply")
            self.terraform_apply()
            if self.terraform_error_check():
                raise RuntimeError
            print("\tUpdate the configuration file with the credentials and the host ip")
            self.update_systems()
        except:
            self.destroy()
            raise RuntimeError

    def destroy(self):
        print("Destroy platforms with Terraform")
        print("\tTerraform destroy")
        self.terraform_destroy()

    def generate_ssh_key(self):
        for system in self._configurations:
            for platform in self._configurations[system]:
                ssh_key_name = self._configurations[system][platform]["sshKeyName"]
                ssh_dir = self._configurations[system][platform]["sshKeyDirectory"]
                private_key_path = os.path.join(ssh_dir, ssh_key_name)
                public_key_path = private_key_path + ".pub"
                if not os.path.isdir(ssh_dir):
                    print("\t\tGenerate SSH directory for system - " + system + ", platform - " + platform)
                    logger.info(f"Creating SSH directory: {ssh_dir}")
                    os.makedirs(ssh_dir, exist_ok=True)
                if os.path.isfile(private_key_path) and os.path.isfile(public_key_path):
                    print("\t\tKeypair already exists...")
                    logger.info(f"SSH keypair already exists: {private_key_path} / {public_key_path}")
                    return private_key_path, public_key_path
                if os.path.isfile(private_key_path) or os.path.isfile(public_key_path):
                    print("\t\tIncomplete SSH keypair detected, cleaning old keys...")
                    logger.warning("Incomplete SSH keypair detected → cleaning old keys.")
                    try:
                        if os.path.isfile(private_key_path):
                            os.remove(private_key_path)
                        if os.path.isfile(public_key_path):
                            os.remove(public_key_path)
                    except Exception as e:
                        logger.error(f"Failed to remove old SSH keys: {e}")
                        raise
                print("\t\tGenerate new SSH keys for system - " + system + ", platform - " + platform)
                logger.info(f"Generating new SSH keypair for Terraform: {private_key_path}")
                cmd = f"ssh-keygen -t rsa -b 4096 -m PEM -N '' -f {private_key_path}"
                critical_command(cmd)

    def terraform_cmd(self, cmd, arg):
        self._errors[cmd] = {}
        for system in self._configurations:
            self._errors[cmd][system] = {}
            for platform in self._configurations[system]:
                directory = self._configurations[system][platform]["directory"]
                print("\tStage " + cmd + " for system - " + system + ", platform - " + platform)
                self._errors[cmd][system][platform] = command("terraform -chdir=" + directory + " " + cmd + " " + arg, output=False)

    def terraform_init(self):
        self.terraform_cmd("init", "")

    def terraform_apply(self):
        self.terraform_cmd("apply", "-auto-approve")

    def terraform_destroy(self):
        self.terraform_cmd("destroy", "-auto-approve")

    def terraform_get_ips(self, system, platform):
        directory = self._configurations[system][platform]["directory"]
        ins = command("terraform -chdir=" + directory + " show -json | jq -r '.values.root_module.resources[] "
                                                  "| select(.type==\"aws_instance\") | \"\(.name)=\(.values.public_ip)\"'", output=True).split('\n')
        instances = {}
        for i in ins:
            try:
                instances[i.split("=")[0]] = i.split("=")[1]
            except:
                pass
        return instances

    def terraform_error_check(self):
        error = False
        for cmd in self._errors:
            for system in self._errors[cmd]:
                for platform in self._errors[cmd][system]:
                    if not self._errors[cmd][system][platform]:
                        print("The stage " + cmd + " of " + " system - " + system + ", platform - " + platform + " has failed")
                        error = True
        return error

    def update_systems(self):
        for system in self._configurations:
            for platform in self._configurations[system]:
                directory = self._configurations[system][platform]["directory"]
                info = get_aws_ssh_info(directory)
                self._systems[system]["platforms"][platform]["user"] = info["user"]
                self._systems[system]["platforms"][platform]["host"] = info["host"]
                self._systems[system]["platforms"][platform]["sshKey"] = self._configurations[system][platform]["sshKeyDirectory"] + "/" + self._configurations[system][platform]["sshKeyName"]
                self._systems[system]["platforms"][platform]["instances"] = self.terraform_get_ips(system, platform)
                config = open_json(config_file)
                config["systems"] = self._systems
                save_json(config, config_file)

    def is_platform_ready(self, ssh, system, platform):
        if system in self._configurations:
            if platform in self._configurations[system]:
                code = cloud_init_status(ssh, system, platform)
                code = code.strip().lower()
                # 0 = DONE, 1 = NOT READY, 2 = ERROR
                if "status: not started" in code:
                    logger.debug("Cloud-init has not started yet.")
                    return 1
                elif "status: running" in code:
                    logger.debug("Cloud-init is still running.")
                    return 1
                elif "status: done" in code:
                    logger.debug("Cloud-init is complete.")
                    return 0
                elif "status: error" in code:
                    logger.error("Cloud-init encountered an error.")
                    return -1
                elif "status: disabled" in code:
                    logger.debug("Cloud-init is disabled on this system.")
                    return -1  # or 1, depending on your policy
                else:
                    logger.error(f"Unknown cloud-init status: {code}")
                    return -1
        return 0

    def wait_cloud_init(self, ssh, system):
        if system in self._wait_cloud_init:
            while not self.get_platform_state(ssh, system, self._wait_cloud_init[system]):
                time.sleep(60)

    def get_platform_state(self, ssh, system, platform):
        if system not in self._ready_platforms:
            return True
        if platform not in self._ready_platforms[system]:
            return True
        if self._ready_platforms[system][platform] == 0:
            return True
        current_time = datetime.now()
        if self._last_checked_platforms[system][platform] is None or (current_time - self._last_checked_platforms[system][platform]).total_seconds() > 60:
            self._last_checked_platforms[system][platform] = current_time
            code = self.is_platform_ready(ssh, system, platform)
            if code < 0:
                fetch_log(ssh, system, platform)
                raise Exception
            if code == 0:
                self._ready_platforms[system][platform] = 0
                return True
            if code == 1:
                if self._ready_platforms[system][platform] == -2:
                    msg = (f"System '{system}' - platform '{platform}' is not ready yet...")
                    print(msg)
                self._ready_platforms[system][platform] = -1
                return False
        return False


def fetch_log(ssh, system, platform):
    log_dir = "log/" + system + "/" + platform
    os.makedirs(log_dir, exist_ok=True)
    ssh.scp_get(system, "/var/log/cloud-init-output.log", log_dir, platform)


def cloud_init_status(ssh, system, platform):
    cmd = "sudo cloud-init status"
    return ssh.ssh(cmd, system, platform, output=True).strip().lower()


def terraform_output_json(tf_dir):
    """
        Run `terraform output -json` in the given directory and return
        the parsed JSON object.

        Parameters
        ----------
        tf_dir : str
            Path to the directory containing the Terraform configuration.

        Returns
        -------
        dict
            Parsed JSON outputs from Terraform.

        Raises
        ------
        RuntimeError
            If the terraform command fails or the JSON cannot be parsed.
    """
    line = "terraform -chdir={} output -json".format(tf_dir)
    out = command(line, output=True, silent=True)
    if out is False or out is None:
        logger.error("Failed to execute Terraform output in '{}'".format(tf_dir))
        raise RuntimeError("terraform output -json failed in '{}'".format(tf_dir))
    try:
        data = json.loads(out)
    except Exception as e:
        logger.error("Failed to parse JSON from terraform output in '{}': {}".format(tf_dir, e))
        raise
    logger.debug("Terraform outputs successfully retrieved from '{}'".format(tf_dir))
    return data


def _parse_ssh_from_command(cmd_str):
    """
        Given a ssh command string (e.g. 'ssh -i key fedora@1.2.3.4'),
        try to extract the 'user' and 'host' parts.

        Returns
        -------
        (user, host) or (None, None)
    """
    match = re.search(r"(\S+)@(\S+)", cmd_str)
    if match:
        return match.group(1), match.group(2)
    return None, None


def get_aws_ssh_info(tf_dir, default_user="fedora"):
    """
    Infer SSH information (user, host, ssh) for an AWS node from
    Terraform outputs, knowing only the directory containing the .tf files.

    Strategy:
      1. If an output named 'ssh_command' exists, parse it to extract user/host.
      2. Otherwise, search for an output whose name contains 'public_ip'
         or ends with '_ip' or 'ip', and use its value as the host.
         Prefer outputs whose name suggests they are the head node
         (e.g. contain 'head') over others (e.g. 'compute').
      3. Always return `host` as a string, even if Terraform outputs a list.
      4. Use `default_user` if user cannot be inferred.

    Parameters
    ----------
    tf_dir : str
        Path to the directory containing the Terraform configuration.
    default_user : str, optional
        Default SSH user if none is inferred (default: "fedora").

    Returns
    -------
    dict
        {
            "user": <user>,
            "host": <host>,       # always a string
            "ssh":  "<user>@<host>"
        }

    Raises
    ------
    RuntimeError
        If a suitable host cannot be determined from Terraform outputs.
    """
    outputs = terraform_output_json(tf_dir)

    user = None
    host = None

    # 1) Prefer an explicit 'ssh_command' output, if present
    if "ssh_command" in outputs:
        obj = outputs["ssh_command"]
        if isinstance(obj, dict) and "value" in obj:
            val = obj["value"]

            # Terraform sometimes wraps outputs in lists
            if isinstance(val, list) and val:
                logger.debug("ssh_command output is a list; using first element: %s", val[0])
                val = val[0]

            if isinstance(val, str):
                u, h = _parse_ssh_from_command(val)
                if u is not None and h is not None:
                    user, host = u, h
                    logger.debug("SSH info inferred from ssh_command: %s@%s", user, host)

    # 2) Fallback: search for any output that looks like an IP/public IP
    if host is None:
        candidates = []

        for key, obj in outputs.items():
            if not isinstance(obj, dict) or "value" not in obj:
                continue

            val = obj["value"]

            # Accept either strings or non-empty lists
            ip_value = None
            if isinstance(val, str):
                ip_value = val.strip()
            elif isinstance(val, list) and val:
                logger.debug("IP output '%s' is a list; using first element: %s", key, val[0])
                ip_value = str(val[0]).strip()

            if ip_value is None:
                continue

            lname = key.lower()
            if "public_ip" in lname or lname.endswith("_ip") or lname == "ip":
                candidates.append((key, ip_value))

        if candidates:
            # On préfère explicitement les outputs faisant référence au head
            head_candidates = [
                (k, v) for (k, v) in candidates
                if "head" in k.lower()
            ]
            if head_candidates:
                key, val = head_candidates[0]
                logger.debug(
                    "Host inferred from head-specific Terraform output '%s': %s",
                    key,
                    val,
                )
            else:
                # Sinon on prend le premier comme avant (comportement de repli)
                key, val = candidates[0]
                logger.debug(
                    "Host inferred from Terraform output '%s' (no head-specific candidate found): %s",
                    key,
                    val,
                )

            host = val

    # Si toujours rien, on abandonne
    if host is None:
        logger.error("Unable to determine SSH host from Terraform outputs in '%s'", tf_dir)
        logger.error("Hint: define an output named 'ssh_command' or 'head_public_ip'.")
        raise RuntimeError("Could not infer AWS SSH host")

    # 3) Final normalization: ensure host is ALWAYS a string
    if isinstance(host, list):
        if not host:
            logger.error("Terraform output returned an empty list for host.")
            raise RuntimeError("Host list is empty")
        logger.debug("Final host normalization from list to string: %s", host[0])
        host = host[0]

    host = str(host).strip()

    # Set default user if none inferred
    if user is None:
        user = default_user
        logger.debug("Using default SSH user '%s' for host '%s'", user, host)

    ssh_str = f"{user}@{host}"
    logger.debug("AWS SSH info resolved: user='%s', host='%s', ssh='%s'", user, host, ssh_str)

    return {
        "user": user,
        "host": host,
        "ssh": ssh_str,
    }



