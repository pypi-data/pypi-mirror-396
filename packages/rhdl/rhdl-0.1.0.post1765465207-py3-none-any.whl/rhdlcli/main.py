#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import os
import sys

from rhdlcli.cli import parse_arguments
from rhdlcli.downloader import download_component
from rhdlcli.options import build_options, login
from rhdlcli.validator import (
    exit_if_arguments_invalid,
    exit_if_credentials_invalid,
)


def catch_all_and_print(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyboardInterrupt:
            print("Keyboard interrupt exiting...")
            sys.exit(130)
        except Exception as e:
            print(e)
            sys.exit(1)

    return inner


@catch_all_and_print
def main():
    arguments = parse_arguments(sys.argv[1:])
    exit_if_arguments_invalid(arguments)
    cwd = os.path.realpath(os.getcwd())
    env_variables = dict(os.environ)
    options = build_options(cwd, arguments, env_variables)
    if options["command"] == "login":
        login(options)
        return
    exit_if_credentials_invalid(options)
    download_component(options)


if __name__ == "__main__":
    main()
