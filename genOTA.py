#!/usr/bin/env python
from __future__ import print_function
import hashlib
import glob
import json
import os
import fnmatch
import sys

cwd=os.getcwd()
is_test = os.environ["IS_TEST"].strip()
build_type = os.environ["TG_BUILD_TYPE"].strip()
build_version = os.environ["TG_BUILD_VERSION"].strip()
build_zip_type = os.environ["TG_BUILD_ZIP_TYPE"].strip()

if len(build_version) != 0:
	filename_prefix = build_version

if len(build_type) != 0:
	filename_suffix = build_type.lower()

# If for some reason its an official test build make sure not to alter in official json file
if 'OFFICIAL' in build_type and is_test == 'yes':
	filename_suffix = 'unofficial'

# Explicitly handle filename suffix of community beta builds
if 'COMMUNITY' in build_type and is_test == 'yes':
	filename_suffix = filename_suffix + '_unofficial'

if build_zip_type == 'VANILLA':
	json_file = '/' + filename_prefix + '_vanilla_builds_' + filename_suffix + '.json'
elif build_zip_type == 'GAPPS':
	json_file = '/' + filename_prefix + '_gapps_builds_' + filename_suffix + '.json'
else:
	json_file = '/pie_builds.json'

builds = {}
local_data_keys = []

def get_local_stuff():
	global device
	try:
		with open(cwd + json_file, "r") as jsonFile:
			try:
				local_data = json.load(jsonFile)
			except ValueError:
				print('Local file empty! Initial data', file=sys.stderr)
				return
			if local_data is not None:
				for k in local_data.keys():
					local_data_keys.append(k)
				for local_device in local_data_keys:
					try:
						if device != local_device:
							print('Taking in local info for {}'.format(local_data[local_device][0]["filename"]), file=sys.stderr)
							builds.setdefault(local_device, []).append({
								'maintainer': local_data[local_device][0]["maintainer"],
								'model': local_data[local_device][0]["model"],
								'oem': local_data[local_device][0]["oem"],
								'changelog': local_data[local_device][0]["changelog"],
								'sha256': local_data[local_device][0]["sha256"],
								'size': local_data[local_device][0]["size"],
								'date': local_data[local_device][0]["date"],
								'datetime': local_data[local_device][0]["datetime"],
								'filename': local_data[local_device][0]["filename"],
								'filepath': local_data[local_device][0]["filepath"],
								'version': local_data[local_device][0]["version"],
								'type': local_data[local_device][0]["type"]
							})
					except KeyError:
						print('Key not found!', file=sys.stderr)
	except IOError:
		open(cwd + json_file, "w+")

latest_zip = os.environ["BUILD_ARTIFACT"]
print('Latest zip is ' + latest_zip)
try:
	filename=latest_zip
	if build_zip_type == 'VANILLA' or build_zip_type == 'GAPPS':
		_, version, device, buildtype, builddate, ziptype = os.path.splitext(filename)[0].split('-')
	else:
		_, version, device, buildtype, builddate = os.path.splitext(filename)[0].split('-')
	get_local_stuff()
	print('Generating for new build of {}'.format(filename), file=sys.stderr)
	builds.setdefault(device, []).append({
		'maintainer': os.environ["TG_DEVICE_MAINTAINER"],
		'model': os.environ["TG_DEVICE_MODEL"],
		'oem': os.environ["TG_DEVICE_OEM"],
		'changelog': os.getenv("TG_DEVICE_CHANGELOG"),
		'sha256': os.environ["BUILD_ARTIFACT_SHA256"],
		'size': os.environ["BUILD_ARTIFACT_SIZE"],
		'date': '{}-{}-{}'.format(builddate[0:4], builddate[4:6], builddate[6:8]),
		'datetime': '{}{}{}'.format(builddate[0:4], builddate[4:6], builddate[6:8]),
		'filename': filename,
		'filepath': '/{}/{}/{}'.format('arrow-' + version.split('v')[1], device, filename),
		'version': version,
		'type': buildtype.lower()
	})
except IndexError:
	print('Something went wrong could not find the zip!!', file=sys.stderr)

for device in builds.keys():
    builds[device] = sorted(builds[device], key=lambda x: x['date'])
with open(cwd + json_file, "w") as jsonFile:
	json.dump(builds, jsonFile, sort_keys=True, indent=4)
os.chdir(cwd)
