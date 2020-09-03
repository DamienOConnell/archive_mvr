#!/usr/bin/env python3

from config_reader import ConfigReader
from pprint import pprint
import re
import os
import time
import sys
import shutil
from syslog_simple import app_logger

"""
WorkInc Fortigate firewall can push backups to a TFTP target.

This script:

- Read config variables, default config file is 'config.json'
- Takes the mtime of the file, converts to a timestamp to use as a timestamp.
  e.g. '2020-08-11'
- Reads the backup to establish the name of the firewall that wrote the backup.
- Move the backup file to an archive location. Naming format:

        <archive_location>/<hostname>/<hostname>_<timestamp>.conf
    e.g.:
        /home/rancid/data/firewall-1/firewall1_2020-08-22.conf


Copyright 2020 Damien O'Connell

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from this
   software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


def get_hostname(backup_file: str, search: str):

    with open(backup_file, "r") as infile:
        for line in infile:
            line = line.rstrip()
            match = re.search(search, line)

            if match:
                hostname = line[match.end() :]
                hostname = hostname.strip('"')
                return hostname
    return None


def main():
    conf = ConfigReader().conf
    if conf.get("log_host") and conf.get("log_port"):
        logger = app_logger(conf["log_host"], conf["log_port"])
    else:
        logger = app_logger()
    logger.info("Logging initialized.")

    search = "set hostname"
    backup_file = conf["incoming_path"] + conf["backup_name"]

    # make sure there is a backup to work on
    if not os.path.exists(backup_file):
        logger.critical("Cannot find backup_file in backup file, aborting")
        print("No backup to check, aborting")
        sys.exit(-1)

    timestamp = time.strftime("_%Y-%m-%d_%H-%m", time.gmtime(os.path.getmtime(backup_file)))

    hostname = get_hostname(backup_file, search)
    if not hostname:
        logger.critical("Cannot find hostname in backup file, aborting")
        print("Cannot find hostname in backup file, aborting")
        sys.exit(-1)
    print(f"found hostname {hostname}")
    target_dir = conf["archive_path"] + hostname + "/"
    target_file = hostname + timestamp + ".conf"

    print(f"Archive will be written to {target_dir}{target_file}")
    logger.info(f"Archive will be written to {target_dir}{target_file}")

    if not os.path.exists(target_dir):
        try:
            os.mkdir(target_dir)
        except PermissionError:
            print("Access denied, creating target directory {target_dir}")
            sys.exit(-1)

    try:
        shutil.move(backup_file, target_dir + target_file)
    except Exception:
        print(f"Error moving archive to directory {target_dir}")
        sys.exit(-1)


if __name__ == "__main__":
    main()
