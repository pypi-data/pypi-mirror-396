#!/usr/bin/env python
# coding: utf8
# Copyright 2022 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
asgard module init file
"""
from importlib.metadata import version
from os import environ

# Get asgard package version (installed from setuptools_scm)
try:
    __version__ = version("asgard_eopf")
except ModuleNotFoundError:
    __version__ = "unknown"  # pragma: no cover
finally:
    del version

# Activate the schemas validation
ASGARD_VALIDATE_SCHEMAS = bool("ASGARD_DEBUG" in environ)
