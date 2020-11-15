#!/usr/bin/env python3
from __future__ import print_function
import hashlib
import glob
import json
import os
import fnmatch
import sys

builds = {}
build_info = {}
cwd = os.getcwd()
is_test = os.environ["IS_TEST"]
filename = os.environ["BUILD_ARTIFACT"]
_, version, device, buildtype, builddate, ziptype = os.path.splitext(filename)[
    0].split('-')
buildtype = 'community_nightly' if is_test and buildtype == 'community' else buildtype
json_file = '/arrow_ota.json'


def updateDeviceInfo():
    if device not in builds.keys():
        builds.setdefault(device, []).append({
            'maintainer': os.environ["TG_DEVICE_MAINTAINER"],
            'model': os.environ["TG_DEVICE_MODEL"],
            'oem': os.environ["TG_DEVICE_OEM"],
            'changelog': os.getenv("TG_DEVICE_CHANGELOG")
        })
    else:
        builds[device][0].update({
            'maintainer': os.environ["TG_DEVICE_MAINTAINER"],
            'model': os.environ["TG_DEVICE_MODEL"],
            'oem': os.environ["TG_DEVICE_OEM"],
            'changelog': os.getenv("TG_DEVICE_CHANGELOG")
        })

    build_info.update({version: list([{buildtype: list([{ziptype: list([{
        'sha256': os.environ["BUILD_ARTIFACT_SHA256"],
        'size': os.environ["BUILD_ARTIFACT_SIZE"],
        'date': '{}-{}-{}'.format(builddate[0:4], builddate[4:6], builddate[6:8]),
        'datetime': '{}{}{}'.format(builddate[0:4], builddate[4:6], builddate[6:8]),
        'filename': filename,
        'filepath': '/{}/{}/{}'.format('arrow-' + version.split('v')[1], device, filename),
        'version': version,
        'type': buildtype.lower()
    }])}])}])})

    if version not in builds[device][0].keys():
        builds[device][0].update(build_info)

    if buildtype in builds[device][0][version][0].keys():
        builds[device][0][version][0][buildtype][0].update(
            build_info[version][0][buildtype][0])
    else:
        builds[device][0][version][0].update(build_info[version][0])


print('Generating for new build of {}'.format(filename), file=sys.stderr)
try:
    with open(cwd + json_file, "r") as jsonFile:
        builds = json.load(jsonFile)
        updateDeviceInfo()
except FileNotFoundError:
    open(cwd + json_file, "w+")
    updateDeviceInfo()


with open(cwd + json_file, "w") as jsonFile:
    json.dump(builds, jsonFile, sort_keys=True, indent=2)
os.chdir(cwd)
