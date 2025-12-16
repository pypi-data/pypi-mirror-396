#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


def credentials_are_defined(options):
    required_keys = ["base_url", "access_key", "secret_key"]
    return all(key in options and options[key] is not None for key in required_keys)


def exit_if_credentials_invalid(options):
    if not credentials_are_defined(options):
        print("Credentials are invalid. Run `rhdl login` or set env variables.")
        sys.exit(1)


def arguments_are_valid(arguments):
    command = arguments["command"]
    AVAILABLE_COMMANDS = ["download", "login"]
    if arguments["command"] not in AVAILABLE_COMMANDS:
        print(
            f"Invalid command {command}. Available commands are: {','.join(AVAILABLE_COMMANDS)}"
        )
        return False
    return True


def exit_if_arguments_invalid(arguments):
    if not arguments_are_valid(arguments):
        sys.exit(1)
