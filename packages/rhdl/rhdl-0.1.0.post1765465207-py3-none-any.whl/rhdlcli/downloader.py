#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from urllib.parse import urljoin
from rhdlcli.api import (
    get_component,
    get_files_list,
    download_files,
    HmacSession,
)
from rhdlcli.stats import check_download_folder_has_enough_space
from rhdlcli.files import get_files_to_remove, filter_files
from rhdlcli.fs import mkdir_p


def clean_download_folder(download_folder, files):
    print("Verifying local mirror, this may take some time")

    if not os.path.isdir(download_folder):
        mkdir_p(download_folder)

    for file in get_files_to_remove(download_folder, files):
        print(f"Remove file {file}")
        os.remove(file)


def download_component(options):
    component = get_component(options)
    session = HmacSession(
        base_url=urljoin(
            options["base_url"], f"/api/v1/components/{component['compose_id']}/files/"
        ),
        access_key=options["access_key"],
        secret_key=options["secret_key"],
    )
    files_list = get_files_list(session)
    files = files_list["files"]
    files = filter_files(files, options["include_and_exclude"])
    download_folder = options["destination"]
    clean_download_folder(download_folder, files)
    check_download_folder_has_enough_space(download_folder, files)
    download_files(session, download_folder, files)
