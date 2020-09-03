#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
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

import json
import sys
import argparse


class ConfigReader:
    def __init__(self, config_file: str = "config.json") -> None:

        required = [
            "incoming_path",
            "archive_path",
            "backup_name",
        ]

        # Get the CLI options as dict, ignore argparse namespace
        argparse_dict = vars(self.getargs())
        json_dict = self.load_json(argparse_dict["config_file"])

        # json_dict.update(argparse_dict)

        # Update CLI values if passed
        for key in argparse_dict.keys():
            if argparse_dict[key]:
                json_dict[key] = argparse_dict[key]

        self.conf = json_dict

        # Make sure we got everything
        for option in required:
            if not self.conf.get(option):
                print(f"FATAL: configuration option {option} is not in config file or arguments.")
                sys.exit(0)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        attrs = str([(x, self.__dict__[x]) for x in self.__dict__])
        return "<ConfigReader: %s>" % attrs

    def load_json(self, config_file: str) -> dict:
        try:
            with open(config_file) as _:
                try:
                    return json.load(_)
                except json.JSONDecodeError:
                    print(f"{config_file} could not be loaded, not a valid JSON document.")
                    return None
        except FileNotFoundError:
            print(f"JSON config file {config_file} could not be loaded....")
            sys.exit(0)

    def getargs(self):

        parser = argparse.ArgumentParser(description="Stats summarizer")

        parser.add_argument("-v", "--verbose", action="store_true", help="Show what is being done.")
        parser.add_argument(
            "-c",
            "--config_file",
            type=str,
            help="JSON config file.",
            default="config.json",
            required=False,
        )

        # these will overrides for the values that may be in the config file
        parser.add_argument("-i", "--incoming_path", type=str, help="Search here for data file.")
        parser.add_argument("-a", "--archive_path", type=str, help="Save original data file here.")
        parser.add_argument("-n", "--backup_name", type=str, help="Name of the backup files.")
        args = parser.parse_args()
        return args


def main():

    conf = ConfigReader()
    print(conf)


if __name__ == "__main__":
    main()
