# Copyright (c) 2023-2024 Westfall Inc.
#
# This file is part of Windrunner.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, and can be found in the file NOTICE inside this
# git repository.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

"""Environment configuration for Windrunner.

This module centralizes environment-derived configuration values used
by the Windrunner tooling. It reads a small set of environment
variables and provides sensible defaults when those variables are
not present. The values defined here are imported elsewhere in the
project (for example `main.py`) to construct paths and to contact
the Harbor API.

Constants:
	VOLDEF: default mount path used when `VOLUME` is not set.
	VOLUME: runtime volume path (from `VOLUME` env var or `VOLDEF`).
	HARBORHOST: base URL for the Harbor API.
	HARBORUSER: default Harbor username.
	HARBORPASS: default Harbor password.
"""

## WINDRUNNER CONFIGURATION VALUES
VOLDEF = "/mnt/vol"
VOLUME = os.environ.get("VOLUME",VOLDEF)

## HARBOR CONFIGURATION VALUES
HARBORHOST = os.environ.get("HARBORHOST","http://harbor-core.harbor/api/v2.0")
HARBORUSER = os.environ.get("HARBORUSER",'admin')
HARBORPASS = os.environ.get("HARBORPASS",'Harbor12345')
