#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def get_component_size(files):
    size = 0
    for file in files:
        size += file["size"]
    return size


def enough_space(download_folder, files):
    component_size = get_component_size(files)
    st = os.statvfs(download_folder)
    free_space = st.f_bavail * st.f_frsize * 0.95
    component_size_gb = component_size / 1024 / 1024 / 1024
    free_space_gb = free_space / 1024 / 1024 / 1024
    print("Component size %d GB" % component_size_gb)
    print("Free space %d GB" % free_space_gb)
    return component_size < free_space


def check_download_folder_has_enough_space(download_folder, files):
    if not enough_space(download_folder, files):
        raise Exception("Not enough space in %s" % download_folder)
