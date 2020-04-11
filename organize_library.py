import argparse
import eyed3
import os
import shutil

def initialize_argument_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
          description=('Organize the music library contained in music_library_source, '
            'extracting metadata from each music file found and copying them to the '
            'appropriate subdirectory within music_library_destination with the file '
            'pattern `Artist/Album/Song Title`.'))
  parser.add_argument('--music_library_source', metavar='path',
                      type=str, action='store', required=True,
                      help='Path to the current music library (unorganized).')
  parser.add_argument('--music_library_destination', metavar='path',
                      type=str, action='store', required=True,
                      help='Path to an empty directory where the organized '
                           'music library should be created.')
  parser.add_argument('--logfile', action='store', type=str)
  return parser


class LogWriter(object):
  def __init__(self, log_file_path):
    self.log_fd = None
    if log_file_path:
      print('Logging to {}.'.format(log_file_path))
      self.log_fd = open(log_file_path, 'w+')

  def __del__(self):
    if self.log_fd:
      self.log_fd.close()

  def Log(self, s):
    if self.log_fd:
      self.log_fd.write(s)
      self.log_fd.write('\n')


class SongData(object):
  def __init__(self):
    self.track_name = None
    self.track_number = None
    self.album_name = None
    self.artist_name = None
    self.file_path = None
  def __repr__(self):
    return 'Song: {}, album: {}, artist: {}, stored at path: {}'.format(
      self.track_name, self.album_name, self.artist_name, self.file_path)
  def IntendedPath(self, parent_directory):
    intended_filename = '{} {}.mp3'.format(self.track_number, self.track_name)
    return os.path.join(parent_directory, self.artist_name,
        self.album_name, intended_filename)
  def SameTrack(self, other):
    return (self.track_name == other.track_name and
            self.album_name == other.album_name and
            self.artist_name == other.artist_name and
            self.track_number == other.track_number)
  def __eq__(self, other):
    return self.SameTrack(other) and self.file_path == other.file_path

  def __lt__(self, other):
    return self.Tuple() < other.Tuple()

  def Tuple(self):
    def E(v):
      if not v: return ''
      return v
    return (E(self.artist_name), E(self.album_name), E(self.track_number), E(self.track_name), E(self.file_path))


def SongDataFromMp3(mp3_file_path, logger):
  audiofile = eyed3.load(mp3_file_path)
  if audiofile:
    song_data = SongData()
    song_data.track_name = audiofile.tag.title
    # eyed3 gives us a tuple for track_num where the first element is
    # the number of this track and the second element is the total
    # number of tracks. The latter is (empirically) unreliable, thus
    # we simply extract the track number.
    song_data.track_number = audiofile.tag.track_num[0]
    song_data.album_name = audiofile.tag.album
    song_data.artist_name = audiofile.tag.artist
    song_data.file_path = mp3_file_path
    return song_data
  else:
    logger.Log('Failed to extract mp3 metadata for file at path {} '
               'please handle manually.'.format(mp3_file_path))
    return False


def extract_song_data_if_mp3(file_path, logger):
  if file_path.endswith('.mp3'):
    song_data = SongDataFromMp3(file_path, logger)
    if song_data:
      return [song_data]
  else:
    logger.Log('skipping non-mp3 file {}.'.format(file_path))
  return []


def collect_all_songs_from_library(library_source, logger):
  """Recursively visits all subdirectories of the path library_source
     and extracts SongData from each mp3 found.  Any non-mp3 non-directory
     files found will be logged, as will info about missing metadata."""
  song_data_collected = []
  for elem in os.listdir(library_source):
    file_path = os.path.join(library_source, elem)
    if os.path.isfile(file_path):
      song_data_collected.extend(extract_song_data_if_mp3(file_path, logger))
    else:
      songs_from_subdir = collect_all_songs_from_library(file_path, logger)
      song_data_collected.extend(songs_from_subdir)
  return song_data_collected


def write_songs_to_new_dir(song_data, destination_path, logger):
  song_data.sort()
  for song in song_data:
    src_file = song.file_path
    dst_file = song.IntendedPath(destination_path)
    if os.path.exists(dst_file):
      logger.Log('Duplicate detected! Skipping copy of {} to {} since destination '
                 'file already exists.'.format(src_file, dst_file))
    else:
      try:
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copyfile(src_file, dst_file)
      except NotADirectoryError as err:
        # see details at https://stackoverflow.com/a/1976050/6472082.
        logger.Log('Failed to copy {} to {} due to error {} (Possibly caused by '
                   'characters in path which are not legal windows file names. '
                   'If so, please manually pick an appropriate name for this file.)'.format(
                     src_file, dst_file, err))
  logger.Log('Copy complete, terminating.')
  print('Organized music files have been copied to {}'.format(destination_path))


def main():
  args = initialize_argument_parser().parse_args()
  print('Preparing to organize files from {}.'.format(args.music_library_source))
  if not os.path.exists(args.music_library_source):
    print('FATAL_ERROR: music library source directory does not exist.')
    return
  if os.path.exists(args.music_library_destination):
    print('FATAL_ERROR: music library destination directory alread exists, please pick an empty one.')
    return
  logger = LogWriter(args.logfile)
  logger.Log('Begining iteration through music files.')
  extracted_songs_with_metadata = collect_all_songs_from_library(args.music_library_source, logger)
  logger.Log('Successfully extracted {} songs from library source.'.format(len(extracted_songs_with_metadata)))
  write_songs_to_new_dir(extracted_songs_with_metadata, args.music_library_destination, logger)

if __name__ == "__main__":
  main()
