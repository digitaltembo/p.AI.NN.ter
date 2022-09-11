import os
import shutil
from typing import List
from pathlib import Path

from fastapi import APIRouter, FastAPI, File, UploadFile
from utils.db import get_images, delete_image, add_image_file
from utils.file_utils import ROOT_DIR, OUTPUT_DIR, UPLOAD_DIR, get_png_filename, trim_path

router = APIRouter()

def file_and_time(root: str, filename: str):
  filepath = os.path.join(root, filename)
  return [trim_path(filepath), os.path.getmtime(filepath)]

def get_files_in_dir(dir: str):
  all_files: List[str] = []
  for root, dirs, files in os.walk(dir):
    for name in files:
        all_files.append(file_and_time(root, name))
  all_files.sort(key=lambda f: -f[1])
  return [file[0] for file in all_files]

@router.get("/files")
def list_files():
  return {
    "uploads": get_images(True),
    "outputs": get_images(False)
  }

@router.post("/files/upload")
def upload_file(file: UploadFile):
  print("Got file", file)
  basename = Path(file.filename).stem
  upload_dest = get_png_filename(basename, UPLOAD_DIR)
  ret = None
  try:
    with open(upload_dest, "wb") as buffer:
      print("Saving image", upload_dest)
      shutil.copyfileobj(file.file, buffer)
    ret = add_image_file(upload_dest, "Uploaded Image")
  finally:
    file.file.close()
  return ret

@router.delete("/files/delete")
def delete_file(file: str):

  filepath = ROOT_DIR + file
  if os.path.abspath(filepath).startswith(os.path.abspath(ROOT_DIR)):
    delete_image(file)

