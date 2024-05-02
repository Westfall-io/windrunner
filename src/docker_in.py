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

import time
start_time = time.time()

import os

if not os.path.exists('/mnt/vol/digitalforge'):
    os.mkdir('/mnt/vol/digitalforge')

import json
import requests
from requests.auth import HTTPBasicAuth

def main(proj= "python-sample-containers", repo="python-pytest-boolfile"):
    domain = "http://harbor-core.harbor/api/v2.0"
    proj_url = "projects"
    repo_url = "repositories"
    artifact_url = "artifacts"

    r = requests.get(
        os.path.join(domain, proj_url, proj, repo_url, repo, artifact_url),
        auth=HTTPBasicAuth('admin', 'Harbor12345'))

    if 'errors' in r.json():
        if r.json()['errors'][0]['code'] == 'UNAUTHORIZED':
            print(r.request.url)
            print(r.request.body)
            print(r.request.headers)
            raise NotImplementedError('UNAUTHORIZED')
    if len(r.json()) == 0:
        print(proj, repo)
        raise NotImplementedError('Failed to get results from harbor api.')

    try:
        data = r.json()[0]["extra_attrs"]["config"]
    except KeyError:
        print(r.json())
        raise KeyError('Failed to find an entry.')
    except IndexError:
        print(r.json())
        raise KeyError('Failed to find an entry.')

    if 'entrypoint' in [x.lower() for x in data.keys()]:
        raise NotImplementedError('Cant handle this yet.')

    with open('/mnt/vol/digitalforge/path.txt', 'w') as f:
        f.write(data['WorkingDir'])

    with open('/mnt/vol/digitalforge/cmd.txt', 'w') as f:
        f.write(data['Cmd'][0])

    with open('/mnt/vol/digitalforge/args.txt', 'w') as f:
        args_out = '["'+'","'.join(data['Cmd'][1:])+'"]'
        print("Arguments: {}".format(args_out))
        f.write(args_out)
    return

if __name__ == "__main__":
    import fire
    fire.Fire(main)
    print("--- %s seconds ---" % (time.time() - start_time))
