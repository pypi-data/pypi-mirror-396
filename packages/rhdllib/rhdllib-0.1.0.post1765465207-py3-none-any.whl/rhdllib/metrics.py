# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Facility module to setup statsd metrics client
"""

import inspect
import os

import statsd


class Client(statsd.StatsClient):

    def __init__(
        self,
        host: str = os.getenv("STATSD_HOST", "localhost"),
        port: int = int(os.getenv("STATSD_PORT", "8125")),
        prefix: str = "",
    ) -> None:

        _prefix = prefix or "rhdl"
        if prefix == "":
            # try to figure out stack to guess prefix, otherwise keep default
            try:
                _frm = inspect.stack()[1]
                _mod = inspect.getmodule(_frm[0])
                _prefix = _mod.__name__
            except Exception:
                pass

        super().__init__(host=host, port=port, prefix=_prefix.lower())
