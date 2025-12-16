#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from rhdlcli.version import __version__

EXAMPLES = """
examples:
  # Login to RHDL
  rhdl login

  # download lastest RHEL-10 compose in <cwd>/RHEL-10 folder
  rhdl download RHEL-10

  # download latest RHEL-10 in /tmp/repo folder
  rhdl download RHEL-10 --destination /tmp/repo
"""

COPYRIGHT = """
copyright:
  Copyright © 2024 Red Hat.
  Licensed under the Apache License, Version 2.0
"""


def clean_with_default_values(parsed_arguments):
    DEFAULT_INCLUDE_EXCLUDE_LIST = [
        {"pattern": ".composeinfo", "type": "include"},
        {"pattern": "metadata/*", "type": "include"},
        {"pattern": "*/aarch64/*", "type": "exclude"},
        {"pattern": "*/ppc64le/*", "type": "exclude"},
        {"pattern": "*/s390x/*", "type": "exclude"},
        {"pattern": "*/source/*", "type": "exclude"},
        {"pattern": "*/x86_64/debug/*", "type": "exclude"},
        {"pattern": "*/x86_64/images/*", "type": "exclude"},
        {"pattern": "*/x86_64/iso/*", "type": "exclude"},
    ]
    if "include_and_exclude" not in parsed_arguments:
        setattr(parsed_arguments, "include_and_exclude", DEFAULT_INCLUDE_EXCLUDE_LIST)
    del parsed_arguments.include
    del parsed_arguments.exclude
    if parsed_arguments.destination is None:
        setattr(parsed_arguments, "destination", f"./{parsed_arguments.compose}")
    return vars(parsed_arguments)


class IncludeExcludeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if "include_and_exclude" not in namespace:
            setattr(namespace, "include_and_exclude", [])
        previous = namespace.include_and_exclude
        previous.append({"pattern": values, "type": self.dest})
        setattr(namespace, "include_and_exclude", previous)


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(
        usage="rhdl COMMAND [OPTIONS]",
        description="Download the latest RHEL compose easily.",
        epilog=EXAMPLES + COPYRIGHT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "command",
        metavar="COMMAND",
        nargs="?",
        help="Available commands: download, login",
    )
    parser.add_argument(
        "compose", metavar="COMPOSE", nargs="?", help="Compose ID or NAME"
    )
    parser.add_argument(
        "-d",
        "--destination",
        metavar="DESTINATION",
        help="Destination folder where rhdl will download the compose",
    )
    parser.add_argument(
        "-i",
        "--include",
        action=IncludeExcludeAction,
        metavar="INCLUDE",
        dest="include",
        help="List the file paths that will be downloaded. Wildcard `*` autorized.",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action=IncludeExcludeAction,
        metavar="EXCLUDE",
        dest="exclude",
        help="List file paths that will be excluded. Wildcard `*` autorized.",
    )
    parser.add_argument(
        "-t",
        "--tag",
        metavar="TAG",
        default="milestone",
        help="Filter RHEL compose with a tag (i.e. nightly, candidate, ga)",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parsed_arguments = parser.parse_args(arguments)
    return clean_with_default_values(parsed_arguments)
