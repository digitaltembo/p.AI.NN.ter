from typing import Optional

import cv2
from PIL import Image
from pathlib import Path
from fastapi import APIRouter

from transforms.real_ersgan import get_upsampler
from utils.db import add_image_file
from utils.GFPGANer import GFPGANer
from utils.file_utils import cache_remote_file, get_png_filename, trim_path
from utils.images import opencv2pil

router = APIRouter()

MODEL_URL = 'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth'
MODEL_NAME = 'GFPGANv1.3.pth'

cached_restorers = {}
def get_restorer(scale: float):
  global cached_restorers

  if scale not in cached_restorers:
    path_to_model = cache_remote_file(MODEL_URL, MODEL_NAME)
    cached_restorers[scale] = GFPGANer(
      model_path=path_to_model,
      upscale=scale, # can do upscaling at the same time? should we do that here
      arch='clean', # used for the GFPGANv1.3 model
      channel_multiplier = 2, # used for the GFPGANv1.3 model
      bg_upsampler = None if scale == 1 else get_upsampler(for_anime=False) # gfpgan doesn't work well for cartoons anyways
    )
  return cached_restorers[scale]

def prefetch():
  get_restorer(1.0)

def gfpgan_image(
  input_image,
  scale: float = 1.0,
  only_center_face: Optional[bool] = False,
  prealligned: Optional[bool] = False,
):
  """Uses [GFPGANv1.3 Model](https://github.com/TencentARC/GFPGAN) to restore faces in photos

  :param input_image: CV2 Image Mat to restore
  :type input_image: CV2 Image Mat
  :param scale: Factor by which to upsample, using Real-ERSGAN for background and GFPGAN for facial upscaling
  :type scale: number
  :param only_center_face: If true, only restores the central face founde, defaults to false
  :type only_center_face: Optional[bool], optional
  :param prealligned: If true, treats the image as having a correct allignment, defaults to false
  :type prealligned: Optional[bool], optional
  :return: Restored Image
  :rtype: PIL.Image
  """
  restorer = get_restorer(scale)
  cropped_faces, restored_faces, restored_img = restorer.enhance(
            img, has_aligned=prealligned, only_center_face=only_center_face, paste_back=True)
  # ignore cropped_faces and restored_faces return values

  return opencv2pil(restored_image)

def gfpgan_file(
  input_image: str,
  scale: float = 1.0,
  only_center_face: Optional[bool] = False,
  prealligned: Optional[bool] = False,
):
  """Uses [GFPGANv1.3 Model](https://github.com/TencentARC/GFPGAN) to restore faces in photos

  :param input_image: Path to image to restore
  :type input_image: str
  :param scale: Factor by which to upsample, using Real-ERSGAN for background and GFPGAN for facial upscaling
  :type scale: number
  :param only_center_face: If true, only restores the central face founde, defaults to false
  :type only_center_face: Optional[bool], optional
  :param prealligned: If true, treats the image as having a correct allignment, defaults to false
  :type prealligned: Optional[bool], optional
  :return: Restored Image
  :rtype: PIL.Image
  """
  img = cv2.imread(input_image, cv2.IMREAD_COLOR)
  return gfpgan_image(img, only_center_face, prealligned)


@router.post("/transforms/gfpgan")
def create_gfpgan(
  input_image: str,
  scale: float = 1.0,
  outfile: Optional[str] = None,
  only_center_face: Optional[bool] = False,
  prealligned: Optional[bool] = False,
):
  """Uses [GFPGANv1.3 Model](https://github.com/TencentARC/GFPGAN) to restore faces in photos

  :param input_image: Path to image to restore
  :type input_image: str
  :param scale: Factor by which to upsample, using Real-ERSGAN for background and GFPGAN for facial upscaling
  :type scale: number
  :param outfile: If defined, persist to that path, otherwise create new file path
  :type persist: Optional[str], optional
  :param only_center_face: If true, only restores the central face founde, defaults to false
  :type only_center_face: Optional[bool], optional
  :param prealligned: If true, treats the image as having a correct allignment, defaults to false
  :type prealligned: Optional[bool], optional
  :return: Restored Image
  :rtype: PIL.Image
  """
  img = gfpgan_file(input_image=input_image, only_center_face=only_center_face, prealligned=prealligned)
  if outfile is None:
    outfile = get_png_filename('face_' + Path(args.prompt[0]).stem)
  print('Saving face fix to ', outfile)
  img.save(outfile)

  return add_image_file(
    trim_path(outfile),
    "GFPGAN Face Restoration of " + input_image,
    input_image,
    img
  )
