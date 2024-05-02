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
VOLDEF = "/mnt/vol"
VOLUME = os.environ.get("VOLUME",VOLDEF)
WINDSTORMAPIHOST = os.environ.get(
    "WINDSTORMAPIHOST",
    "http://windstorm-api-service.windstorm:8000/"
)

import shutil
from datetime import datetime, timedelta

import git
import requests
from jinja2 import Template
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import GOVERNANCE, Tags
from minio.retention import Retention

client = Minio(
        "storage-minio.artifacts:9000",
        access_key="CcgP5DINKOfemEXcjYyL",
        secret_key="YS62HYwroWYozFGoWyeZjYsmGwFLEULu047lquE6",
        secure=False,
    )

def parse_repopath(repopath, ref):
    rp = repopath.split('/')
    path = {
        'repo': rp[1],
        'org': rp[0],
        'ref': ref
    }
    return path

def fix_null_issue(action):
    if action['dependency'] == 'null':
        action['dependency'] = None
    return action

def parse_bucket_name(qualifiedName):
    bucket = qualifiedName.lower().strip().replace('_', '-'). \
        replace("'", "").replace('"', "").replace("\\","").replace("/",""). \
        replace("::", ".")

    if len(bucket) > 63:
        bucket = bucket[:63]
    elif len(bucket) < 3:
        bucket = bucket+'-bucket'

    return bucket

def main(action = {
        "id": 18,
        "declaredName": "collectData",
        "qualifiedName": "Requirements::Valid_Test::collectData",
        "artifact": {
            "id": 3,
            "full_name": "Westfall/fortran_greaterthan",
            "commit_url": "http://artifacts.westfall.io/Westfall/fortran_greaterthan/commit/fa8f69f17ab910a9126d9338f19dc23062887c04",
            "ref": "main",
            "commit": "84455bbbb558579acc17427adf06af4530ba4abb",
            "date": "2023-10-17T17:41:36.606126"
        },
        "container": {
            "id": 4,
            "resource_url": "core.harbor.domain/fortran-containers/fortran-greaterthan:0.1.0",
            "project": "fortran-containers",
            "image": "fortran-greaterthan",
            "tag": "0.1.0",
            "digest": "a5ad39fb0bf5ea8168938c2f21cfcfb2c1addad8ad98b949a1b8a6edc5c76780",
            "date": "2023-10-17T21:29:44.567434"
        },
        "variables": {
            "var1": {
              "value": 10,
              "units": "u.one"
            },
            "var2": {
              "value": 3,
              "units": "u.one"
            }
        },
        'dependency': None
    }, thread_execution_id=0, prev_thread_name=None):
    ## Update status
    print('Updating thread execution {} status'.format(thread_execution_id))
    r = requests.put(
        WINDSTORMAPIHOST+"auth/update_thread/{}".format(
            thread_execution_id
        ), json ={'status':'windrunner_1'}
    )
    if r.status_code != 200:
        print('Failed to update status')
        thread_name = ''
    else:
        thread_name = r.json()['name']

    print('Running workflow prep for action: {}--{}'.format(action['id'],action['qualifiedName']))

    action = fix_null_issue(action)
    if action['dependency'] is not None:
        # This is a dependent action.
        r = requests.get(
            WINDSTORMAPIHOST+"models/threads/thread/{}?validate=false".format(
                action['dependency']
            )
        )

        try:
            action_prev = r.json()['results'][0]
        except:
            try:
                print(r.json())
                raise NotImplementedError('Could not find action to pull output data from.')
            except:
                print(r.request.url)
                print(r.request.body)
                print(r.request.headers)
                raise NotImplementedError('JSON could not be read from server.')

        if prev_thread_name is None or prev_thread_name == '':
            r = requests.get(
                WINDSTORMAPIHOST+"views/thread/{}?size=1&page=1".format(
                    action['dependency']
                )
            )
            if r.status_code == 200:
                prev_thread_name = r.json()["results"][0]["name"]

        bucket = parse_bucket_name(action_prev["qualifiedName"])
        print('Downloading and unzipping prior dependency output.')
        client.fget_object(bucket,"output"+prev_thread_name+".zip", "output"+prev_thread_name+".zip")
        # Overwrite the base image with output from the dependency, we'll
        # overwrite with new input after this step
        shutil.unpack_archive("output"+prev_thread_name+".zip", VOLUME, "zip")

    print('Downloading git repo for input artifacts.')
    path = parse_repopath(action['artifact']['full_name'], action['artifact']['ref'])
    #print(path)
    ipath = os.path.join('http://gitea-http.config-git:3000/',path['org'], path['repo'])

    # Download the git repo for the artifact
    print('Downloading the repo.')
    repo = git.Repo.clone_from(ipath, 'artifact')
    repo.git.checkout(path['ref'])

    # Build the artifact
    ## Convert the dictionary
    variables = action['variables'].copy()
    for var in variables:
        variables[var] = variables[var]['value']

    def digitalforge(string):
        # This function is prep for using units
        return action['variables'][string]['value']

    print('Replacing variables in files with values.')
    for (dir_path, dir_names, file_names) in os.walk('artifact'):
        for name in file_names:
            thisfile = os.path.join(dir_path, name)
            if 'artifact/.git' not in dir_path:
                with open(thisfile,'r') as f:
                        # Skip the .git folder
                        try:
                            template = Template(f.read())
                        except UnicodeDecodeError:
                            print('Warning: Skipping file {}/{} because it was not text-based.'.format(dir_path, name))
                # Save to temp folder for zip and upload to minio
                with open(os.path.join('tmp',dir_path[8:],name), 'w') as f:
                        f.write(template.render(digitalforge=digitalforge,**variables))
                # Overwrite anything in the current folder with the artifact
                with open(os.path.join(VOLUME,dir_path[8:],name), 'w') as f:
                        f.write(template.render(digitalforge=digitalforge,**variables))

    # Load the input file into an minio bucket
    # Make 'asiatrip' bucket if not exist.
    retention_date = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0,
    ) + timedelta(days=7)
    tags = Tags(for_object=True)
    tags["type"] = "input"

    print('Uploading to Minio')
    try:
        bucket = parse_bucket_name(action["qualifiedName"])
        found = client.bucket_exists(bucket)
        if not found:
            client.make_bucket(bucket, object_lock=True)
            print("Bucket made!")
        else:
            print("Bucket already exists!")

        shutil.make_archive('input'+thread_name, 'zip', 'tmp')
        client.fput_object(
            bucket, 'input'+thread_name+'.zip', 'input'+thread_name+'.zip',
            tags=tags,
            retention=Retention(GOVERNANCE, retention_date)
        )

        # Check if we can download the file
        #objects = client.list_objects(bucket)
        #for item in client.list_objects(bucket,recursive=True):
        #    client.fget_object(bucket,item.object_name,'inputdl.zip')

    except S3Error as exc:
        print("error occurred.", exc)

    print('Initializing git repo.')
    # Git init the directory
    repo2 = git.Repo.init(VOLUME)
    repo2.git.add(all=True)
    # Commit everything here
    repo2.index.commit(":robot: Setting base files.")

    print('Complete.')

    print('Updating thread execution {} status'.format(thread_execution_id))
    r = requests.put(
        WINDSTORMAPIHOST+"auth/update_thread/{}".format(
            thread_execution_id
        ), json ={'status':'windrunner_2'}
    )
    if r.status_code != 200:
        print('Failed to update status')
    return

if __name__ == "__main__":
    os.mkdir('tmp')
    # This part is a workaround until volume is attached.
    if not os.path.exists(VOLUME):
        raise NotImplementedError('Volume is not attached.')

    import fire
    fire.Fire(main)
    print("--- %s seconds ---" % (time.time() - start_time))
