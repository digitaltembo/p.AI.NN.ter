import os
from typing import Optional

import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
from PIL import Image
from pathlib import Path
from fastapi import APIRouter

from utils.db import add_image_file
from utils.file_utils import cache_remote_file, get_png_filename, trim_path

router = APIRouter()

# Should be tuned for the GPU memory, determines the biggest chunk of an image that will be worked upon at once
IMAGE_TILE_SIZE = int(os.getenv('UPSCALE_TILE_SIZE', '300'))
# In order to reduce border artifacts, there should be overlap between image tiles, determined based on this input
IMAGE_TILE_BORDER = int(os.getenv('UPSCALE_TILE_BORDER', '20'))

HALF_PRECISION = bool(os.getenv('USE_HALF_PRECISION', ''))


SIMPLE_MODEL_URL = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
ANIME_MODEL_URL = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth'

SIMPLE_MODEL_NAME = 'RealESRGAN_x4plus.pth'
ANIME_MODEL_NAME = 'realesr-animevideov3.pth'

cached_simple = None
cached_anime = None
def get_upsampler(for_anime: bool = False):
  global cached_simple, cached_anime
  basic_params = {
    "tile": IMAGE_TILE_SIZE,
    "tile_pad": IMAGE_TILE_BORDER,
    "half": HALF_PRECISION,
    "scale": 4,
  }
  if for_anime:
    if cached_anime is None:
      path_to_model = cache_remote_file(ANIME_MODEL_URL, ANIME_MODEL_NAME)
      cached_anime = RealESRGANer(
        model_path = path_to_model,
        model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4, act_type='prelu'),
        **basic_params
      )
    return cached_anime
  else:
    if cached_simple is None:
      path_to_model = cache_remote_file(SIMPLE_MODEL_URL, SIMPLE_MODEL_NAME)
      cached_simple = RealESRGANer(
        model_path = path_to_model,
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4),
        **basic_params
      )
    return cached_simple

def prefetch():
  """Build every pipe necessary for real ersgan"""
  get_upsampler(false)
  get_upsampler(true)

def real_ersgan_image(
  input_image,
  scale: int = 2.0,
  for_anime: Optional[bool] = False,
):
  """Uses [Real-ERSGAN](https://github.com/xinntao/Real-ESRGAN) model for image upscaling

  :param input_image: CV2 Image Mat to upscale
  :type input_image: Cv2 Image Mat
  :param scale: factor by which to upscale
  :type scale: int
  :param for_anime: If true, uses a different model optemized for cartoons/anime, defaults to False
  :type for_anime: Optional[bool], optional
  :return: Upscaled image
  :rtype: PIL.Image
  """
  upsampler = get_upsampler(for_anime)
  output, _ = upsampler.enhance(input_image, outscale = scale)
  output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
  return Image.fromarray(output)


def real_ersgan_file(
  input_image: str,
  scale: int = 2.0,
  for_anime: Optional[bool] = False,
):
  """Uses [Real-ERSGAN](https://github.com/xinntao/Real-ESRGAN) model for image upscaling

  :param input_image: Path to image to upscale
  :type input_image: str
  :param scale: factor by which to upscale
  :type scale: int
  :param for_anime: If true, uses a different model optemized for cartoons/anime, defaults to False
  :type for_anime: Optional[bool], optional
  :return: Upscaled image
  :rtype: PIL.Image
  """
  img = cv2.imread(input_image, cv2.IMREAD_COLOR)
  return real_ersgan_image(img, scale, for_anime)

@router.post("/transforms/real-ersgan")
def create_real_ersgan(
  input_image: str,
  scale: int = 2.0,
  outfile: Optional[str] = None,
  for_anime: Optional[bool] = False,
):
  """Uses [Real-ERSGAN](https://github.com/xinntao/Real-ESRGAN) model for image upscaling

  :param input_image: Path to image to upscale
  :type input_image: str
  :param scale: factor by which to upscale
  :type scale: int
  :param outfile: If defined, persist to that path, otherwise create new file path
  :type persist: Optional[str], optional
  :param for_anime: If true, uses a different model optemized for cartoons/anime, defaults to False
  :type for_anime: Optional[bool], optional
  :return: Path to persisted image
  :rtype: str
  """

  img = real_ersgan(input_image=input_image, scale=scale, for_anime=for_anime)
  if outfile is None:
    outfile = get_png_filename('upscale_' + Path(input_image).stem)
  print("Saving upscaled image to ", outfile)
  img.save(outfile)

  return add_image_file(
    trim_path(outfile),
    "Real-ERSGAN Upscaling of " + input_image,
    input_image,
    img
  )