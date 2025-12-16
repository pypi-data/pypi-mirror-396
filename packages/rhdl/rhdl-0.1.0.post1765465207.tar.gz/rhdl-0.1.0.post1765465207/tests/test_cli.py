from rhdlcli.cli import parse_arguments


def test_parse_arguments_when_no_options():
    args = parse_arguments(["download", "RHEL-9.4"])
    assert args["destination"] == "./RHEL-9.4"
    assert args["tag"] == "milestone"
    assert args["include_and_exclude"] == [
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


def test_parse_arguments_command_argument():
    assert parse_arguments(["download", "RHEL-9.4"])["command"] == "download"


def test_parse_arguments_compose_argument():
    assert parse_arguments(["download", "RHEL-9.4"])["compose"] == "RHEL-9.4"


def test_parse_arguments_destination_argument():
    assert (
        parse_arguments(["download", "RHEL-9.4", "-d", "/tmp/d1"])["destination"]
        == "/tmp/d1"
    )
    assert (
        parse_arguments(["download", "RHEL-9.4", "--destination", "/tmp/d2"])[
            "destination"
        ]
        == "/tmp/d2"
    )


def test_parse_arguments_tag_argument():
    assert (
        parse_arguments(["download", "RHEL-9.4", "-t", "candidate"])["tag"]
        == "candidate"
    )
    assert (
        parse_arguments(["download", "RHEL-9.4", "--tag", "nightly"])["tag"]
        == "nightly"
    )


def test_parse_arguments_include_and_exclude_in_order():
    assert parse_arguments(
        [
            "download",
            "RHEL-9.4",
            "-i",
            "AppStream/x86_64/os/*",
            "--exclude",
            "*/aarch64/*",
            "--include",
            "BaseOS/x86_64/os/*",
            "--exclude",
            "*",
        ]
    )["include_and_exclude"] == [
        {"pattern": "AppStream/x86_64/os/*", "type": "include"},
        {"pattern": "*/aarch64/*", "type": "exclude"},
        {"pattern": "BaseOS/x86_64/os/*", "type": "include"},
        {"pattern": "*", "type": "exclude"},
    ]
