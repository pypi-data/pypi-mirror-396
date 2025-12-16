import os

from rhdlcli.files import get_files_to_remove, filter_files
from rhdlcli.cli import parse_arguments
from rhdlcli.options import build_options


def test_get_files_to_remove():
    files = [
        {
            "name": "b",
            "path": "",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "size": 0,
        },
        {
            "name": "c",
            "path": "subfolder",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "size": 0,
        },
    ]
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "data", "repo")
    files_to_remove = [os.path.join(path, "a")]
    assert get_files_to_remove(path, files) == files_to_remove


def test_get_files_to_remove_add_files_with_different_sha():
    files = [
        {
            "name": "a",
            "path": "",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "size": 0,
        },
        {
            "name": "b",
            "path": "",
            "sha256": "7848a92f625831b29caa0c74770603b78f8f6877541f803c33aa3741f946712d",
            "size": 7123,
        },
        {
            "name": "c",
            "path": "subfolder",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "size": 0,
        },
    ]
    test_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(test_dir, "data", "repo")
    files_to_remove = [os.path.join(path, "b")]
    assert get_files_to_remove(path, files) == files_to_remove


def _get_options(args):
    return build_options(
        "/tmp",
        parse_arguments(args),
        {
            "RHDL_API_URL": "",
            "RHDL_ACCESS_KEY": "",
            "RHDL_SECRET_KEY": "",
        },
    )


def test_default_filter_files():
    files = [
        {
            "path": "",
            "sha256": "954719cab91afac5bc142656afff86e6d8e87570b035cbce65dbbb84892a40d3",
            "name": ".composeinfo",
            "size": 14496,
        },
        {
            "path": "AppStream/x86_64/debug/tree/Packages",
            "sha256": "6f48f0d285918e502035da74decf447c6bb29898206406a4ed6a92ece94d276a",
            "name": "PackageKit-command-not-found-debuginfo-1.1.12-2.el8.x86_64.rpm",
            "size": 45052,
        },
        {
            "path": "AppStream/x86_64/os/Packages",
            "sha256": "8fe293470f677bfc6eb04204c47b5e1a0e5d15431ef7ed9dbb269aaea386ed9f",
            "name": "PackageKit-command-not-found-1.1.12-2.el8.x86_64.rpm",
            "size": 28616,
        },
        {
            "path": "BaseOS/x86_64/os/Packages",
            "sha256": "7949b18b6d359b435686f2f5781928675ec8b2872b96f0abf6ba10747f794694",
            "name": "avahi-libs-0.7-19.el8.i686.rpm",
            "size": 68920,
        },
        {
            "path": "BaseOS/x86_64/iso",
            "sha256": "06fd27c0279d5b42078f7de66d056c7875d025d1eb89a29dd2777240459c1026",
            "name": "RHEL-8.4.0-20201020.n.2-BaseOS-x86_64-boot.iso",
            "size": 731906048,
        },
        {
            "path": "AppStream/s390x/os/Packages",
            "sha256": "6f48f0d285918e502035da74decf447c6bb29898206406a4ed6a92ece94d276a",
            "name": "PackageKit-command-not-found-debuginfo-1.1.12-2.el8.s390x.rpm",
            "size": 29562,
        },
        {
            "path": "AppStream/x86_64/os",
            "sha256": "6f48f0d285918e502035da74decf447c6bb29898206406a4ed6a92ece94d276a",
            "name": ".treeinfo",
            "size": 29562,
        },
    ]
    options = _get_options(["download", "RHEL-8"])
    assert filter_files(files, options["include_and_exclude"]) == [
        {
            "path": "",
            "sha256": "954719cab91afac5bc142656afff86e6d8e87570b035cbce65dbbb84892a40d3",
            "name": ".composeinfo",
            "size": 14496,
        },
        {
            "path": "AppStream/x86_64/os/Packages",
            "sha256": "8fe293470f677bfc6eb04204c47b5e1a0e5d15431ef7ed9dbb269aaea386ed9f",
            "name": "PackageKit-command-not-found-1.1.12-2.el8.x86_64.rpm",
            "size": 28616,
        },
        {
            "path": "BaseOS/x86_64/os/Packages",
            "sha256": "7949b18b6d359b435686f2f5781928675ec8b2872b96f0abf6ba10747f794694",
            "name": "avahi-libs-0.7-19.el8.i686.rpm",
            "size": 68920,
        },
        {
            "path": "AppStream/x86_64/os",
            "sha256": "6f48f0d285918e502035da74decf447c6bb29898206406a4ed6a92ece94d276a",
            "name": ".treeinfo",
            "size": 29562,
        },
    ]


def test_filter_files():
    files = [
        {
            "path": "AppStream/x86_64/debug/tree/Packages",
            "sha256": "6f48f0d285918e502035da74decf447c6bb29898206406a4ed6a92ece94d276a",
            "name": "PackageKit-command-not-found-debuginfo-1.1.12-2.el8.x86_64.rpm",
            "size": 45052,
        },
        {
            "path": "AppStream/x86_64/os/Packages",
            "sha256": "8fe293470f677bfc6eb04204c47b5e1a0e5d15431ef7ed9dbb269aaea386ed9f",
            "name": "PackageKit-command-not-found-1.1.12-2.el8.x86_64.rpm",
            "size": 28616,
        },
    ]
    options = _get_options(
        [
            "download",
            "RHEL-8",
            "--include",
            "AppStream/x86_64/os/*",
            "--exclude",
            "*",
        ]
    )
    assert filter_files(files, options["include_and_exclude"]) == [
        {
            "path": "AppStream/x86_64/os/Packages",
            "sha256": "8fe293470f677bfc6eb04204c47b5e1a0e5d15431ef7ed9dbb269aaea386ed9f",
            "name": "PackageKit-command-not-found-1.1.12-2.el8.x86_64.rpm",
            "size": 28616,
        },
    ]


def test_filter_files_with_wildcard():
    files = [
        {
            "path": "",
            "sha256": "954719cab91afac5bc142656afff86e6d8e87570b035cbce65dbbb84892a40d3",
            "name": ".composeinfo",
            "size": 14496,
        },
        {
            "path": "AppStream/x86_64/debug/tree/Packages",
            "sha256": "6f48f0d285918e502035da74decf447c6bb29898206406a4ed6a92ece94d276a",
            "name": "PackageKit-command-not-found-debuginfo-1.1.12-2.el8.x86_64.rpm",
            "size": 45052,
        },
        {
            "path": "BaseOS/source/tree/Packages",
            "sha256": "6f48f0d285918e502035da74decf447c6bb29898206406a4ed6a92ece94d276a",
            "name": "kernel-4.18.0-477.10.1.el8_8.src.rpm",
            "size": 145052,
        },
        {
            "path": "AppStream/x86_64/os/Packages",
            "sha256": "8fe293470f677bfc6eb04204c47b5e1a0e5d15431ef7ed9dbb269aaea386ed9f",
            "name": "PackageKit-command-not-found-1.1.12-2.el8.x86_64.rpm",
            "size": 28616,
        },
        {
            "path": "BaseOS/x86_64/os/Packages",
            "sha256": "7949b18b6d359b435686f2f5781928675ec8b2872b96f0abf6ba10747f794694",
            "name": "avahi-libs-0.7-19.el8.i686.rpm",
            "size": 68920,
        },
        {
            "path": "AppStream/s390x/os/Packages",
            "sha256": "6f48f0d285918e502035da74decf447c6bb29898206406a4ed6a92ece94d276a",
            "name": "PackageKit-command-not-found-debuginfo-1.1.12-2.el8.s390x.rpm",
            "size": 29562,
        },
    ]
    options = _get_options(
        ["download", "RHEL-8", "--include", ".composeinfo", "--exclude", "*"]
    )
    assert filter_files(files, options["include_and_exclude"]) == [
        {
            "path": "",
            "sha256": "954719cab91afac5bc142656afff86e6d8e87570b035cbce65dbbb84892a40d3",
            "name": ".composeinfo",
            "size": 14496,
        }
    ]
