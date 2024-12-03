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
from env import VOLUME, HARBORHOST

import time
start_time = time.time()

import os

dfpath = os.path.join(VOLUME, 'digitalforge')
if not os.path.exists(dfpath):
    os.mkdir(dfpath)

try:
    from windbinder.harbor.artifact import get_artifact, get_linux_digest
except ModuleNotFoundError:
    for (dirpath, dirnames, filenames) in os.walk(mypath):
        print("{}  --  {}".format(dirpath,filenames))
    raise ModuleNotFoundError

def check_for_unhandled_config(config):
    if 'entrypoint' in [x.lower() for x in config.keys()]:
        raise NotImplementedError('Cant handle this yet.')

    return True

def store_container_config(data):
    with open(VOLUME+'/digitalforge/path.txt', 'w') as f:
        f.write(data['WorkingDir'])

    with open(VOLUME+'/digitalforge/cmd.txt', 'w') as f:
        f.write(data['Cmd'][0])

    with open(VOLUME+'/digitalforge/args.txt', 'w') as f:
        args_out = '["'+'","'.join(data['Cmd'][1:])+'"]'
        print("Arguments: {}".format(args_out))
        f.write(args_out)

    return True

def main(proj= "python-sample-containers", repo="python-pytest-boolfile"):
    domain = HARBORHOST
    proj_url = "projects"
    repo_url = "repositories"
    artifact_url = "artifacts"

    url = os.path.join(domain, proj_url, proj, repo_url, repo,
                       artifact_url, "sha256:"+digest)

    data = get_artifact(url)
    linux_digest = get_linux_digest(data)

    url2 = os.path.join(domain, proj_url, proj, repo_url, repo,
                       artifact_url, linux_digest)

    data = get_artifact(url2)
    config = get_config(data)
    check_for_unhandled_config(config)
    store_container_config(config)

    return True

if __name__ == "__main__":
    import fire
    fire.Fire(main)
    print("--- %s seconds ---" % (time.time() - start_time))
