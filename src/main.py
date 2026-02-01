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
"""Windrunner entrypoint and helper routines.

This module provides a small CLI entrypoint (via `fire`) that
fetches artifact metadata from a Harbor registry, resolves the
platform-specific artifact digest, retrieves the image configuration
and stores a few pieces of runtime configuration onto disk under the
configured `VOLUME` mount.

High level flow:
    - Build artifact API URLs using `HARBORHOST`, project, repository
        and tag.
    - Fetch artifact metadata and resolve the linux manifest digest.
    - Fetch the configuration blob for the linux digest and extract
        `Cmd`, `WorkingDir` and other basic container configuration.
    - Persist those pieces to files under `<VOLUME>/digitalforge`.

The small helper functions in this module validate and write the
retrieved configuration.
"""
from env import VOLUME, HARBORHOST

import time
start_time = time.time()

import os

dfpath = os.path.join(VOLUME, 'digitalforge')
if not os.path.exists(dfpath):
    os.mkdir(dfpath)

from windbinder.harbor.artifact import get_artifact, get_linux_digest, get_config

def check_for_unhandled_config(config):
    """Check configuration for fields this tool cannot handle.

    Currently the code does not support images that specify an
    `Entrypoint` (case-insensitive). If an `Entrypoint` key appears
    in the configuration dict a `NotImplementedError` is raised so the
    caller can handle that case explicitly.

    Args:
        config (dict): parsed image configuration blob from Harbor.

    Returns:
        True if configuration is acceptable.

    Raises:
        NotImplementedError: when an unsupported config key is found.
    """

    if 'entrypoint' in [x.lower() for x in config.keys()]:
        raise NotImplementedError('Cant handle this yet.')

    return True

def store_container_config(data):
    """Persist selected container configuration values to disk.

    The function extracts `WorkingDir` and the command (`Cmd`) from
    the image configuration blob and writes them to files under the
    configured `VOLUME` mount. The first element of `Cmd` is written
    to `cmd.txt` and any remaining elements are formatted as a JSON
    array and written to `args.txt`.

    Args:
        data (dict): image configuration dictionary containing keys
            such as `WorkingDir` and `Cmd`.

    Returns:
        True on success.
    """

    with open(VOLUME+'/digitalforge/path.txt', 'w') as f:
        f.write(data['WorkingDir'])

    with open(VOLUME+'/digitalforge/cmd.txt', 'w') as f:
        f.write(data['Cmd'][0])

    with open(VOLUME+'/digitalforge/args.txt', 'w') as f:
        args_out = '["'+'","'.join(data['Cmd'][1:])+'"]'
        print("Arguments: {}".format(args_out))
        f.write(args_out)

    return True

def main(proj= "python-sample-containers", repo="python-pytest-boolfile",
         tag="latest"):
    """Main entrypoint: fetch artifact metadata and store config.

    This function constructs Harbor API URLs for the provided
    `proj`, `repo` and `tag`, retrieves the artifact metadata, resolves
    the linux-platform digest, fetches the configuration blob for that
    digest, validates the configuration and stores a few fields to
    disk using `store_container_config`.

    Args:
        proj (str): Harbor project name.
        repo (str): repository name within the project.
        tag (str): artifact tag to resolve.

    Returns:
        True on success.
    """
    domain = HARBORHOST
    proj_url = "projects"
    repo_url = "repositories"
    artifact_url = "artifacts"

    url = os.path.join(domain, proj_url, proj, repo_url, repo,
                       artifact_url, tag)

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
