#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import sys
import time

from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from urllib.parse import urljoin
from rhdlcli.fs import create_parent_dir
from rhdllib.auth import HmacAuthBase

FIVE_SECONDS = 5
TEN_SECONDS = 10
# We'll allow 5 seconds to connect & 10 seconds to get an answer
REQUESTS_TIMEOUT = (FIVE_SECONDS, TEN_SECONDS)


class HmacSession(requests.Session):
    def __init__(self, base_url, access_key, secret_key):
        self.base_url = base_url
        self.access_key = access_key
        self.secret_key = secret_key
        super(HmacSession, self).__init__()

    def request(self, method, url, *args, allow_redirects=True, **kwargs):
        url = urljoin(self.base_url, url)
        auth = HmacAuthBase(
            self.access_key, self.secret_key, service="api", region="us-east-1"
        )
        response = super(HmacSession, self).request(
            method, url, auth=auth, allow_redirects=False, *args, **kwargs
        )
        if response.status_code == 302 and allow_redirects:
            redirect_url = response.headers.get("Location")
            return super(HmacSession, self).request(
                method, redirect_url, *args, **kwargs
            )
        return response


def retry(tries=3, delay=2, multiplier=2):
    def decorated_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            _tries = tries
            _delay = delay
            while _tries:
                try:
                    return f(*args, **kwargs)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print("%s, retrying in %d seconds..." % (str(e), _delay))
                    time.sleep(_delay)
                    _tries -= 1
                    if not _tries:
                        raise
                    _delay *= multiplier
            return f(*args, **kwargs)

        return f_retry

    return decorated_retry


def get_component(options):
    session = HmacSession(
        base_url=options["base_url"],
        access_key=options["access_key"],
        secret_key=options["secret_key"],
    )
    compose = options["compose"]
    r = session.get(
        f"/api/v1/components?compose_id_startswith={compose}&state=active&sort=-released_at"
    )
    r.raise_for_status()
    components = r.json()["components"]
    if len(components) <= 0:
        print(f"No component found with compose id starting with {compose}")
        sys.exit(1)
    return components[0]


@retry()
def get_files_list(session):
    print("Download file list, it may take a few seconds")
    r = session.get("rhdl_files_list.json")
    r.raise_for_status()
    return r.json()


@retry()
def download_file(session, download_folder, file, i, nb_files):
    start_time = time.monotonic()
    relative_file_path = os.path.join(file["path"], file["name"])
    destination = os.path.join(download_folder, relative_file_path)
    if os.path.exists(destination):
        print(f"({i + 1}/{nb_files}): < Skipping {destination} file already exists")
        return
    print(f"({i + 1}/{nb_files}): < Getting {destination}")
    create_parent_dir(destination)
    r = session.get(relative_file_path)
    r.raise_for_status()
    with open(destination, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
    download_speed = round(file["size"] / (time.monotonic() - start_time) / 1024, 2)
    print(f"({i + 1}/{nb_files}): > Done {destination} - {download_speed} KB/s")
    return file


def download_files(session, download_folder, files):
    nb_files = len(files)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for file in executor.map(
            download_file,
            *zip(
                *[
                    (session, download_folder, file, i, nb_files)
                    for i, file in enumerate(files)
                ]
            ),
        ):
            pass
