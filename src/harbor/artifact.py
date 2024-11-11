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
from env import *

import requests
from requests.auth import HTTPBasicAuth

def get_artifact(url):
    r = requests.get(url, auth=HTTPBasicAuth(HARBORUSER, HARBORPASS))

    if r.status_code == 200:
        print('Connected at: {}'.format(url))
        data = r.json()
        if not 'errors' in data:
            return data

        if data['errors'][0]['code'] == 'UNAUTHORIZED':
            print(r.request.url)
            print(r.request.body)
            print(r.request.headers)
            raise NotImplementedError('UNAUTHORIZED')
    else:
        raise NotImplementedError('Harbor API Error Response: {}'.format(r.status_code))

def get_linux_digest(data):
    # Get the linux/amd os/arch sha
    plat_digest = str()
    try:
        for arch in data["references"]:
            if arch["platform"]["os"] == "linux" and \
                arch["platform"]["architecture"]=="amd64":

                plat_digest = arch["child_digest"]
                break # Stop looking

    except KeyError:
        print(data)
        raise KeyError('Failed to find an entry.')
    except IndexError:
        print(data)
        raise KeyError('Failed to find an entry.')

    return plat_digest

def get_config(data):
    try:
        config = data["extra_attrs"]["config"]

    except KeyError:
        print(data)
        raise KeyError('Failed to find an entry.')
    except IndexError:
        print(data)
        raise KeyError('Failed to find an entry.')

    return config
