#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License'); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os
import setuptools

from rhdlcli import version

root_dir = os.path.dirname(os.path.abspath(__file__))
requirements = open(os.path.join(root_dir, "requirements.txt")).read()
install_requires = [r.split("==")[0] for r in requirements.split("\n")]

# read any possible post-release info e.g. git commit etc
try:
    with open(os.path.join(root_dir, "SNAPSHOT"), encoding="utf-8") as fp:
        post = "." + fp.read().strip()
except IOError:
    post = ""

setuptools.setup(
    name="rhdl",
    version=f"{version.__version__}{post}",
    packages=["rhdlcli"],
    author="Distributed CI team",
    author_email="distributed-ci@redhat.com",
    description="RHDL CLI module",
    install_requires=install_requires,
    url="https://doc.rhdl.distributed-ci.io/",
    license="Apache v2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ],
    entry_points={"console_scripts": ["rhdl = rhdlcli.main:main"]},
)
