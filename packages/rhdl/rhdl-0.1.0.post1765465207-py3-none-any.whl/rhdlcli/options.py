import getpass
import json
import os
import pathlib

from rhdlcli.fs import get_config_path

CREDENTIAL_FILE_NAME = "credentials.json"


def read_credentials_file(app_config_path):
    credential_file_path = os.path.join(app_config_path, CREDENTIAL_FILE_NAME)
    if not os.path.isfile(credential_file_path):

        return {}
    with open(credential_file_path) as f:
        return json.load(f)


def build_options(cwd, arguments, env_variables):
    options = {}
    options.update(arguments)
    app_config_path = get_config_path(env_variables)
    credentials = read_credentials_file(app_config_path)
    options.update(
        {
            "app_config_path": app_config_path,
            "base_url": env_variables.get("RHDL_API_URL", credentials.get("base_url")),
            "access_key": env_variables.get(
                "RHDL_ACCESS_KEY", credentials.get("access_key")
            ),
            "secret_key": env_variables.get(
                "RHDL_SECRET_KEY", credentials.get("secret_key")
            ),
            "destination": os.fspath(
                pathlib.Path(cwd, options["destination"]).resolve()
            ),
        }
    )
    return options


def login(options):
    app_config_path = options["app_config_path"]
    if not os.path.exists(app_config_path):
        os.makedirs(app_config_path)

    access_key = input("RHDL Access Key: ")
    secret_key = getpass.getpass("RHDL Secret Key: ")
    default_base_url = "https://api.rhdl.distributed-ci.io"
    base_url = input(f"RHDL server host ({default_base_url}):") or default_base_url
    credentials = {
        "base_url": base_url,
        "access_key": access_key,
        "secret_key": secret_key,
    }

    file_path = os.path.join(app_config_path, CREDENTIAL_FILE_NAME)
    with open(file_path, "w") as f:
        json.dump(credentials, f)
        print(f"Credential saved in {file_path}")
