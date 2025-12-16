import json
from mock import ANY

from rhdlcli.cli import parse_arguments
from rhdlcli.options import build_options


def test_build_options():
    arguments = parse_arguments(
        ["download", "RHEL-9.4", "-d", "/tmp/repo", "-t", "nightly"]
    )
    cwd = "/tmp"
    env_variables = {"RHDL_API_URL": "", "RHDL_ACCESS_KEY": "", "RHDL_SECRET_KEY": ""}
    options = build_options(cwd, arguments, env_variables)
    assert options == {
        "command": "download",
        "compose": "RHEL-9.4",
        "destination": "/tmp/repo",
        "app_config_path": ANY,
        "base_url": "",
        "access_key": "",
        "secret_key": "",
        "tag": "nightly",
        "include_and_exclude": [
            {"pattern": ".composeinfo", "type": "include"},
            {"pattern": "metadata/*", "type": "include"},
            {"pattern": "*/aarch64/*", "type": "exclude"},
            {"pattern": "*/ppc64le/*", "type": "exclude"},
            {"pattern": "*/s390x/*", "type": "exclude"},
            {"pattern": "*/source/*", "type": "exclude"},
            {"pattern": "*/x86_64/debug/*", "type": "exclude"},
            {"pattern": "*/x86_64/images/*", "type": "exclude"},
            {"pattern": "*/x86_64/iso/*", "type": "exclude"},
        ],
    }


def test_build_options_transform_relative_folder_into_absolute_folder():
    arguments = parse_arguments(
        ["download", "RHEL-9.4", "-d", "../home/rhdl", "-t", "nightly"]
    )
    cwd = "/tmp"
    env_variables = {"RHDL_API_URL": "", "RHDL_ACCESS_KEY": "", "RHDL_SECRET_KEY": ""}
    assert build_options(cwd, arguments, env_variables)["destination"] == "/home/rhdl"


def test_build_options_read_XDG_CONFIG_HOME_env_variable_for_app_config_path():
    arguments = parse_arguments(["login"])
    cwd = "/tmp"
    env_variables = {"RHDL_API_URL": "", "RHDL_ACCESS_KEY": "", "RHDL_SECRET_KEY": ""}
    assert build_options(cwd, arguments, env_variables)["app_config_path"].endswith(
        ".config/rhdl"
    )

    env_variables.update({"XDG_CONFIG_HOME": "/opt/home"})
    assert build_options(cwd, arguments, env_variables)["app_config_path"].endswith(
        "/opt/home/rhdl"
    )


def _write_credentials(tmp_path, credentials):
    rhdl_config_path = tmp_path / "rhdl"
    rhdl_config_path.mkdir()
    credentials_file = rhdl_config_path / "credentials.json"
    credentials_file.write_text(
        json.dumps(credentials),
        encoding="utf-8",
    )


def test_build_options_read_app_config_file_if_present(tmp_path):
    _write_credentials(
        tmp_path,
        {
            "base_url": "http://localhost:5000",
            "access_key": "access_key",
            "secret_key": "secret_key",
        },
    )
    arguments = parse_arguments(["download", "RHEL-9.4"])
    cwd = "/tmp"
    env_variables = {"XDG_CONFIG_HOME": str(tmp_path)}
    options = build_options(cwd, arguments, env_variables)
    assert options["base_url"] == "http://localhost:5000"
    assert options["access_key"] == "access_key"
    assert options["secret_key"] == "secret_key"


def test_build_options_read_env_variables_over_app_config_file_if_both_present(
    tmp_path,
):
    _write_credentials(
        tmp_path,
        {
            "base_url": "https://api.distributed-ci.io",
            "access_key": "fa5e535359de33d035bd3f340ea960",
            "secret_key": "8f1bd6fa31d115692cda5ecf3f92d7",
        },
    )
    arguments = parse_arguments(["download", "RHEL-9.4"])
    cwd = "/tmp"
    env_variables = {
        "XDG_CONFIG_HOME": str(tmp_path),
        "RHDL_API_URL": "http://localhost:5000",
        "RHDL_ACCESS_KEY": "access_key",
        "RHDL_SECRET_KEY": "secret_key",
    }
    options = build_options(cwd, arguments, env_variables)
    assert options["base_url"] == "http://localhost:5000"
    assert options["access_key"] == "access_key"
    assert options["secret_key"] == "secret_key"
