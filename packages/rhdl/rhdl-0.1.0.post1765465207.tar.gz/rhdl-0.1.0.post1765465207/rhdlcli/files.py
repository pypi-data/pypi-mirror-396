#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fnmatch
import hashlib
import os


def _sha256_hexdigest_file(filepath):
    m = hashlib.sha256()
    with open(filepath, mode="rb") as fd:
        for data in fd:
            m.update(data)
    return m.hexdigest()


def _file_clean(file_path, sha256):
    return _sha256_hexdigest_file(file_path) == sha256


def get_files_to_remove(download_folder, files):
    files_list_paths = {}
    for file in files:
        file_path = os.path.join(download_folder, file["path"], file["name"])
        files_list_paths[file_path] = file
    files_to_remove = []
    for root, dirs, files in os.walk(download_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.islink(file_path):
                continue
            if file_path not in files_list_paths or not _file_clean(
                file_path, files_list_paths[file_path]["sha256"]
            ):
                files_to_remove.append(file_path)
    return files_to_remove


def filter_files(files, include_and_exclude):
    new_files = []
    for file in files:
        relative_path = os.path.join(file["path"], file["name"])
        matching_pattern = False
        for ie in include_and_exclude:
            if fnmatch.fnmatch(relative_path, ie["pattern"]):
                matching_pattern = True
                if ie["type"] == "include":
                    new_files.append(file)
                break
        if not matching_pattern:
            new_files.append(file)

    return new_files
