from rhdlcli.cli import parse_arguments
from rhdlcli.validator import (
    arguments_are_valid,
    credentials_are_defined,
)


def test_should_not_raise_an_exception_settings_are_valid():
    assert arguments_are_valid(parse_arguments(["download", "RHEL-9.4"]))


def test_arguments_are_valid_with_bad_command():
    assert arguments_are_valid(parse_arguments(["send", "RHEL-9.4"])) is False


def test_credentials_are_defined():
    assert credentials_are_defined(options={}) is False
    assert (
        credentials_are_defined(
            options={
                "base_url": None,
                "access_key": "access_key",
                "secret_key": "secret_key",
            }
        )
        is False
    )
    assert credentials_are_defined(
        options={
            "base_url": "http://localhost:5000",
            "access_key": "access_key",
            "secret_key": "secret_key",
        }
    )


def test_arguments_are_valid_with_login_command():
    assert arguments_are_valid(parse_arguments(["login"]))
