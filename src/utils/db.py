import sqlite3
import os

from PIL import Image
from typing import Optional
from utils.file_utils import DB_PATH, UPLOAD_DIRNAME, OUTPUT_DIRNAME, ROOT_DIR
IMAGE_COLS = ["id", "src", "alt", "width", "height", "isUpload", "time", "referenceImage"]

def init_db():
  with sqlite3.connect(DB_PATH) as cur:
    cur.execute("""CREATE TABLE IF NOT EXISTS images (
      id integer primary key,
      src text,
      alt text,
      width integer,
      height integer,
      is_upload integer,
      time real,
      reference_image integer
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS history (
      id integer primary key,
      prompt text,
      reference_image integer
    )""")

def add_image(path: str, alt: str, width: int, height: int, time: float, reference_image: int = -1):
  
  with sqlite3.connect(DB_PATH) as cur:
    is_upload = 1 if path.startswith(UPLOAD_DIRNAME) else 0
    cur.execute("""INSERT INTO 
      images(src, alt, width, height, is_upload, time, reference_image)
      VALUES (?,?,?,?,?, ?, ?)""", 
      (path, alt, width, height, is_upload, time, reference_image)
    )
  return {
    "src": path,
    "alt": alt,
    "width": width,
    "height": height,
    "isUpload": is_upload,
    "time": time,
    "reference_image": reference_image
  }

def add_image_file(path: str, alt: str = "", reference_image_path: Optional[str] = None, loaded_image: Optional[Image.Image] = None):
  
  if path.startswith(ROOT_DIR):
    path = path[len(ROOT_DIR):]
  full_path = ROOT_DIR + path
  if loaded_image is None:
    loaded_image = Image.open(full_path)
  reference_image = -1
  if reference_image_path is not None:

    with sqlite3.connect(DB_PATH) as cur:
      res = cur.execute("SELECT id FROM images WHERE path = ?", (reference_image_path))
      row = res.fetchone()
      reference_image = row[0] if row is not None else -1
  time = os.path.getmtime(full_path)
  return add_image(path, alt, loaded_image.width, loaded_image.height, time, reference_image)

def add_all_images(dir: str, alt: str):
  """For adding images in bulk to the DB"""
  for root, dirs, files in os.walk(dir):
    for name in files:
      print("Adding ", name)
      add_image_file(os.path.join(root, name), alt)

def get_image_row_dict(row):
  res = {}
  for index, key in enumerate(IMAGE_COLS):
    res[key] = row[index]
  return res

def get_images(is_upload: Optional[bool] = None):
  with sqlite3.connect(DB_PATH) as cur:
    query = "SELECT * from images WHERE is_upload = 1 ORDER BY time DESC"
    if is_upload is not None:
      if is_upload:
        query = "SELECT * from images WHERE is_upload = 1 ORDER BY time DESC"
      else:
        query = "SELECT * from images WHERE is_upload = 0 ORDER BY time DESC"
  
    res = cur.execute(query)
    rows = res.fetchall()
    if rows is None:
      return []
    return [get_image_row_dict(row) for row in rows]

def delete_image(path: str):
  
  if path.startswith(ROOT_DIR):
    path = path[len(ROOT_DIR):]
  full_path = ROOT_DIR + path
  with sqlite3.connect(DB_PATH) as cur:
    cur.execute("DELETE FROM files WHERE path = ?", path)
  print('Deleting file', filepath)
  os.remove(path)

def add_prompt(prompt: str, reference_image_path: Optional[str] = None):

  with sqlite3.connect(DB_PATH) as cur:
    reference_image = -1
    if reference_image_path is not None:
      res = cur.execute("SELECT id FROM images WHERE path = ?", (reference_image_path))
      row = res.fetchone()
      reference_image = row[0] if row is not None else -1
    cur.execute("""INSERT INTO 
      history (prompt, reference_image)
      VALUES (?, ?)
    """, (prompt, reference_image))




