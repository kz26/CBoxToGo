# CBoxToGo

Command-line tool for downloading series/episodes from China Network Television (CNTV), based on reverse engineering of [CBox](http://cbox.cntv.cn/)

## Requirements

* Python 3.2+
* requests
* ffmpeg, wget in system path

## Usage

```
$ python CBoxToGo.py --help
usage: CBoxToGo.py [-h] [--episodes EPISODES] [--rate-limit RATE_LIMIT]
                   [--video-ids VIDEO_IDS]
                   videoset_id output_dir

Download videos from China Network Television (CNTV)

positional arguments:
  videoset_id           Videoset ID of the show/series
  output_dir            Output directory for downloaded episodes (will be
                        created if it does not exist)

optional arguments:
  -h, --help            show this help message and exit
  --episodes EPISODES, -e EPISODES
                        comma-separated list of episodes and/or episode ranges
                        to download, e.g. 1,2,4-8
  --video-ids VIDEO_IDS, -i VIDEO_IDS
                        comma-separated list of video IDs to download
  --rate-limit RATE_LIMIT, -l RATE_LIMIT
                        download rate limit, passed to wget --limit-rate=
```

## How to find the Videoset ID

1. Browse to [browse to http://serv.cbox.cntv.cn/pages/live/index.shtml](http://serv.cbox.cntv.cn/pages/live/index.shtml).
2. Hover over the series/movie/video you want to watch until the black popup appears.
3. Scroll to the (first) item you want to watch, right click, and use the "Inspect Element" feature of your browser.
4. Look at the `onclick` attribute. The first argument to the `play` function is the **videoset ID**, while the second argument is the **video ID** of that particular video/episode.

If only the videoset ID is provided, CBoxToGo will download all videos within the videoset. In cases where this is not desirable, use the `--episodes` or `--video-ids` options to specify specific videos to download.

## Known issues/limitations

* Unicode characters are not displayed correctly in Windows command prompts.
* CBoxToGo currently uses a regex of the form `第([0-9]+)集` to determine the episode number if the `-e` option is used.
If the episode title does not conform to this format, it will not be downloaded.

## Support

Please use the GitHub Issue Tracker and pull request system to report bugs/issues and submit improvements/changes, respectively.  
