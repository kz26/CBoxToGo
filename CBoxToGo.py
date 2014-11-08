#!/usr/bin/env python
# -*- coding: utf-8 -*-

#     Copyright (C) 2014 Kevin Zhang

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import re
import subprocess
import sys
from urllib.parse import urlparse
import requests

_VERSION = '1.0.1'

if __name__ == '__main__':
	def csl(s):
		raw_vals = s.split(',')
		vals = set()
		for rv in raw_vals:
			rv = rv.strip()
			if rv.isdigit():
				vals.add(int(rv))
			else:
				m = re.match(r'([0-9]+)-([0-9]+)$', rv)
				if m:
					start = int(m.group(1))
					end = int(m.group(2))
					for i in range(start, end + 1):
						vals.add(i)
		return vals

	def wget_rate(s):
		if re.match(r'[0-9]+[km]?$', s, re.IGNORECASE):
			return s
		else:
			raise argparse.ArgumentTypeError("%s is not a valid wget rate limit" % (s))

	parser = argparse.ArgumentParser(description='Download shows/series from China Network Television (CNTV)',
		epilog="version %s" % (_VERSION))
	parser.add_argument('-s', type=csl, help='comma-separated list of episodes and/or ranges to download, e.g. 1,2,4-8')
	parser.add_argument('-l', type=wget_rate, help='download rate limit, passed to wget --limit-rate=')
	parser.add_argument('videoset_id', help='Videoset ID of the show/series (vsetid attributes in playlist.json)')
	parser.add_argument('output_dir', help='Output directory for downloaded episodes (will be created if it does not exist)')

	args = parser.parse_args()

	if not os.path.exists(args.output_dir):
		os.makedirs(args.output_dir, exist_ok=True)
	os.chdir(args.output_dir)

	r = requests.get('http://api.cntv.cn/video/videolistById/', params={
			'vsid': args.videoset_id,
			'serviceId': 'cboxclient',
			'em': 1
		}, headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; Tablet PC 2.0)'}
	)
	data = r.json()
	if args.s:
		el = []
		for e in data['video']:
			m = re.search(r'第([0-9]+)集', e['t'])
			if m and int(m.group(1)) in args.s:
				el.append(e)
	else:
		el = data['video']
	videoset = data['videoset']['0']
	sys.stderr.write("Downloaded episode list for %s.\n" % (videoset['name']))
	for e in el:
		sys.stderr.write("Downloading %s...\n" % (e['t']))
		r = requests.get('http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do', params={
				'pid': e['vid']
			}, headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; Tablet PC 2.0)'}
		)
		data = r.json()
		for c in data['video']['chapters']:
			c['fn'] = urlparse(c['url']).path.split('/')[-1]
			wget_cmd = ['wget', '-nv', '--show-progress']
			if args.l:
				wget_cmd.append("--limit-rate=%s" % (args.l))
			wget_cmd.extend(['-U', 'Get_File_Size_Session', '-O', c['fn'], c['url']])
			subprocess.Popen(wget_cmd).wait()
		sys.stderr.write("%s: concatenating %s pieces...\n" % (e['t'], len(data['video']['chapters'])))
		concat_fn = "concat_%s.txt" % (e['order'])
		with open(concat_fn, 'w') as f:
			for c in data['video']['chapters']:
				f.write("file '%s'\n" % (c['fn']))
		subprocess.Popen(('ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-i', concat_fn, '-c', 'copy', e['t'] + '.mp4')).wait()
		for c in data['video']['chapters']:
			os.remove(c['fn'])
		os.remove(concat_fn)
		sys.stderr.write("%s: done.\n" % (e['t']))





