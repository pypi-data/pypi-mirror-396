import errno
import os


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        elif exc.errno in [errno.EPERM, errno.EACCES]:
            print(f"Permission error on {path}")
        else:
            raise


def create_parent_dir(path):
    mkdir_p(os.path.dirname(path))


def get_config_path(env_variables):
    path = env_variables.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return os.path.join(path, "rhdl")
