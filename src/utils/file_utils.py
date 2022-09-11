import os
import requests
import shutil

CACHE_DIR = os.getenv('CACHE_DIR', '/cache')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
print("Running at", ROOT_DIR)
OUTPUT_DIRNAME = 'output'
OUTPUT_DIR = os.path.join(ROOT_DIR, OUTPUT_DIRNAME)
UPLOAD_DIRNAME = 'uploads'
UPLOAD_DIR = os.path.join(ROOT_DIR, UPLOAD_DIRNAME)
DB_NAME = 'main.db'
DB_PATH = os.path.join(CACHE_DIR, DB_NAME)

def get_png_filename(name: str, dir: str = OUTPUT_DIR):
    """sanitizes input and returns an absolute path to a unique png filename

    :param name: first attempt at a basename
    :type name: str
    :return: unique filename
    :rtype: str
    """
    basename = '_'.join(name.split(' '))
    same_count = 0

    filename_from_count = lambda count: os.path.join(
        dir, basename + ('' if count == 0 else '_' + str(count)) + '.png')

    while os.path.exists(filename_from_count(same_count)):
        same_count += 1

    return filename_from_count(same_count)

def trim_path(path: str):
  return path[len(ROOT_DIR):]

def cache_remote_file(url: str, filename: str):
  """_summary_

  :param url: URL to fetch from
  :type url: str
  :param filename: path to local
  :type filename: str
  :return: _description_
  :rtype: _type_
  """
  path_to_file = os.path.join(CACHE_DIR, filename)
  print('Caching to', path_to_file)
  if not os.path.exists(path_to_file):
    with requests.get(url, stream=True) as response:
      with open(path_to_file, 'wb') as local_file:
        shutil.copyfileobj(response.raw, local_file)
  
  return path_to_file