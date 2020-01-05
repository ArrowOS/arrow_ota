#!/usr/bin/env python
from __future__ import print_function
import hashlib
import glob
import json
import os
import fnmatch
import sys

cwd=os.getcwd()
out_dir = os.environ["OUT"]
build_zip_type = os.environ["TG_ZIP_TYPE"]
zip_pattern = "*OFFICIAL*.zip"

if build_zip_type == 'VANILLA':
	json_file = '/builds.json'
elif build_zip_type == 'GAPPS':
	json_file = '/gapps_builds.json'

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

os.chdir(out_dir)
out_list = sorted(glob.glob(zip_pattern))
print('Found zips:', file=sys.stderr)
print(out_list)
latest_zip = max(out_list, key=os.path.getctime)
print('Latest zip found is ' + latest_zip, file=sys.stderr)
if fnmatch.fnmatch(latest_zip, zip_pattern):
	try:
		filename=latest_zip
		_, version, device, buildtype, builddate, ziptype = os.path.splitext(filename)[0].split('-')
		get_local_stuff()
		print('Generating for new build of {}'.format(filename), file=sys.stderr)
		builds.setdefault(device, []).append({
			'sha256': hashlib.sha256(open(filename).read()).hexdigest(),
			'size': os.path.getsize(filename),
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