import os
import sys
from typing import Optional, Union

from diffusers import (StableDiffusionImg2ImgPipeline,
                       StableDiffusionInpaintPipeline, StableDiffusionPipeline)
from PIL import Image
from torch import autocast, float16
from fastapi import APIRouter

from transforms.gfpgan import gfpgan_image
from transforms.real_ersgan import real_ersgan_image
from utils.db import add_image_file, add_prompt
from utils.file_utils import get_png_filename, trim_path
from utils.images import pil2opencv

router = APIRouter()

STABLE_DIFFUSION_MODEL = "CompVis/stable-diffusion-v1-4"


HF_API_TOKEN = os.environ[
    'HF_API_TOKEN'] if 'HF_API_TOKEN' in os.environ else True

pipeline_params = {
    "pretrained_model_name_or_path": STABLE_DIFFUSION_MODEL,
    "torch_dtype": float16,
    "revision": "fp16",
    "use_auth_token": HF_API_TOKEN
}

pipelines = {
  'txt2img': StableDiffusionPipeline,
  'img2img': StableDiffusionImg2ImgPipeline,
  'inpaint': StableDiffusionInpaintPipeline
}

pipes = {}

def get_pipe(pipeline: str):
    """Memoizes the retrieval of a pipeline operating upon the model"""
    global pipelines, pipes
    if pipeline not in pipes:
        pipes[pipeline] = pipelines[pipeline].from_pretrained(**pipeline_params).to("cuda")
    return pipes[pipeline]

def prefetch():
    """Build every pipe necessary for stable diffusion"""
    for key in pipelines.keys():
        get_pipe(pipelines[key])

def load_image(img_prompt: str):
    img = Image.open(img_prompt).convert("RGB")
    width, height = img.size
    if width == height == 512:
        return img
    if width < height:
        return img.resize((512, int(512 * height / width)))
    else:
        return img.resize((int(512 * width / height), 512))


def stable_diffusion(
    prompt: str,
    width: int = 512,
    height: int = 512,
    img_prompt: Optional[str] = None,
    img_mask: Optional[str] = None,
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5,
    eta: float = 0.0,
    strength: float = 0.8,
):
    """Runs [Stable Diffusion](https://github.com/CompVis/stable-diffusion) models to generate an image

    :param prompt: Text prompt to use 
    :type prompt: str
    :param img_prompt: If defined, used as the input image, which Stable Diffusion will attempt to modify in accordance with your prompt'
    :type img_prompt: Optional[str], optional
    :param img_mask: If defined, used as the image mask which should be white for all pixels that you want to change (???)
    :type img_mask: Optional[str], optional
    :param width: Width of output image. Only outputs in multiples of 8, and works best for 512, defaults to 512
    :type width: int, optional
    :param height: Height of output image. Only outputs in multiples of 8, and works best for 512, defaults to 512
    :type height: int, optional
    :param num_inference_steps: The number of denoising steps. More denoising steps usually lead to a higher quality image at the expense of slower inference.
    :type num_inference_steps: int, optional
    :param guidance_scale: Higher guidance scale encourages to generate images that are closely linked to the text prompt, usually at the expense of lower image quality. See https://arxiv.org/pdf/2205.11487.pdf. Defaults to 7.5
    :type guidance_scale: float, optional
    :param eta: Corresponds to parameter eta (η) in the DDIM paper: https://arxiv.org/abs/2010.02502m, defaults to 0.0
    :type eta: float, optional
    :param strength: Value between 0.0-1.0 that controls the amount of noise that is added to the input image. Values that approach 1.0 will be less semantically consistent with the input image, defaults to 0.75
    :type strength: float, optional
    :return: Generated PIL.Image
    :rtype: PIL.Image
    """
    reasonable_size = lambda x: int(x / 8) * 8 if (x > 0 and x < 8192) else 512
    generator_params = {
        "prompt": prompt,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "eta": eta,
        "strength": strength
    }

    if img_prompt is None:
        with autocast("cuda"):
            return get_pipe('txt2img')(
                    width=reasonable_size(width),
                    height=reasonable_size(height),
                    **generator_params).images[0]
    else:
        generator_params["init_image"] = load_image(img_prompt)
        if img_mask is None:
            with autocast("cuda"):
                return get_pipe('img2img')(**generator_params).images[0]
        else:
            generator_params["mask_image"] = Image.open(img_mask).convert(
                "RGB")
            return get_pipe('inpaint')(**generator_params).images[0]

@router.post("/transforms/stable-diffusion")
def create_stable_diffusion(
    prompt: str,
    outfile: Optional[str] = None,
    width: int = 512,
    height: int = 512,
    upscale: Optional[float] = None,
    fix_faces: bool = False,
    img_prompt: Optional[str] = None,
    img_mask: Optional[str] = None,
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5,
    eta: float = 0.0,
    strength: float = 8.0
):
    """Runs [Stable Diffusion](https://github.com/CompVis/stable-diffusion) models to generate and save an image

    :param prompt: Text prompt to use 
    :type prompt: str
    :param outfile: If defined, persist to that path, otherwise create new file path
    :type persist: Optional[str], optional
    :param img_prompt: If defined, used as the input image, which Stable Diffusion will attempt to modify in accordance with your prompt'
    :type img_prompt: Optional[str], optional
    :param img_mask: If defined, used as the image mask which should be white for all pixels that you want to change (???)
    :type img_mask: Optional[str], optional
    :param width: Width of output image. Only outputs in multiples of 8, and works best for 512, defaults to 512
    :type width: int, optional
    :param height: Height of output image. Only outputs in multiples of 8, and works best for 512, defaults to 512
    :type height: int, optional
    :param upscale: If defined, use Real-ERSGAN model for upscaling the output by the factor provided
    :type upscale: float, optional
    :param fix_faces: If set to true, use GFPGAN model for face restoration (otherwise, stable-diffusion struggles a bit)
    :param fix_faces: bool, optional
    :param num_inference_steps: The number of denoising steps. More denoising steps usually lead to a higher quality image at the expense of slower inference.
    :type num_inference_steps: int, optional
    :param guidance_scale: Higher guidance scale encourages to generate images that are closely linked to the text prompt, usually at the expense of lower image quality. See https://arxiv.org/pdf/2205.11487.pdf. Defaults to 7.5
    :type guidance_scale: float, optional
    :param eta: Corresponds to parameter eta (η) in the DDIM paper: https://arxiv.org/abs/2010.02502m, defaults to 0.0
    :type eta: float, optional
    :param strength: Value between 0.0-1.0 that controls the amount of noise that is added to the input image. Values that approach 1.0 will be less semantically consistent with the input image, defaults to 8.0
    :type strength: float, optional
    :return: path to generated image
    :rtype: str
    """
    add_prompt(prompt, img_prompt)
    img = stable_diffusion(
        prompt=prompt,
        width=width,
        height=height,
        img_prompt=img_prompt,
        img_mask=img_mask,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        eta=eta,
        strength=strength,
    )

    if upscale is not None or fix_faces:
      cv_image = pil2opencv(img)
      if fix_faces:
        img = gfpgan_image(cv_image, upscale if upscale is not None else 1.0, only_center_face=False, prealligned=False)
      else:
        img = real_ersgan_image(cv_image, upscale, for_anime=False)

    if outfile is None:
        outfile = get_png_filename(prompt)
    print("Saving Stable Diffusion Image to ", outfile)
    img.save(outfile)

    return add_image_file(trim_path(outfile), prompt, img_prompt, img)
