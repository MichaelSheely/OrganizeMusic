# Organize Music Library

A little script I created for a family member to help get a music library in order.

As such it was designed to be fully compatible windows.

Makes use of [eyeD3](https://pypi.org/project/eyeD3/) to read mp3 metadata from file in
a directory and move them all to a new directory.

## Instructions for Use

### Dependencies

Requires python 3 (https://www.python.org/downloads/).

`pip install eyeD3`

### Usage

```shell
python organize_library_v1.0.py --music_library_source C:\Users\me\Documents\MusicSource --music_library_destination C:\Users\me\Documents\MusicSink --logfile C:\Users\me\AppData\Local\Temp\music_transfer_log_file.txt
```

