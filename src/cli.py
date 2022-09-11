import argparse

from transforms.gfpgan import create_gfpgan
from transforms.real_ersgan import create_real_ersgan
from transforms.stable_diffusion import create_stable_diffusion
from utils.file_utils import get_png_filename

STABLE_DIFFUSION_ALIASES = ['stable-diffusion', 'generate', 'sd']
REAL_ESRGAN_ALIASES = ['real-esrgan', 'upscale', 're']
GFPGAN_ALIASES = ['gfpgan', 'fix-faces', 'gfp']

def main():
    parser = argparse.ArgumentParser(
        description="Simple CLI for GPU Image Generation")

    parser.add_argument(
        '-i',
        '--img',
        type=str,
        action="store",
        help='Input image, which Stable Diffusion will attempt to modify in accordance with your prompt'
    )
    parser.add_argument(
        '-m',
        '--mask',
        action='store',
        help='Image mask which should be white for all pixels that you want to change (??)'
    )
    parser.add_argument(
        '-s',
        '--size',
        type=str,
        default='512x512',
        help='dimensions of generated image (512x512 is going to be the best by a long shot'
    )
    parser.add_argument(
        '--inference-steps',
        type=int,
        default=50,
        help='Number of inference steps before completion - smaller numbers will be less realist, but faster'
    )
    parser.add_argument(
        "--strength",
        type=float,
        default=0.75,
        help="Value between 0.0-1.0 that controls the amount of noise that is added to the input image. Values that approach 1.0 will be less semantically consistent with the input image"
    )
    parser.add_argument(
        "-g",
        "--guidance",
        type=float,
        default=7.5,
        help="Higher guidance scale encourages to generate images that are closely linked to the text prompt, usually at the expense of lower image quality. See https://arxiv.org/pdf/2205.11487.pdf"
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help='For upscaling,the factor by which it will be upscaled'
    )
    parser.add_argument(
        "--cartoon",
        action='store_true',
        default=False,
        help='For upscaling, uses a model that works better for anime/cartoons'
    )
    parser.add_argument(
        "--only-center-face",
        action='store_true',
        default=False,
        help='For fixing faces, only attempts to fix the central face'
    )
    parser.add_argument(
        "--prealligned-face",
        action='store_true',
        default=False,
        help='For fixing faces, presume the face is prealligned'
    )
    parser.add_argument("-o",
                        "--out",
                        type=str,
                        help="Output to named file")
    parser.add_argument(
        'tool', 
        nargs=1, 
        choices=STABLE_DIFFUSION_ALIASES + REAL_ESRGAN_ALIASES + GFPGAN_ALIASES,
        help="Tool used. stable-diffusion/generate will generate an image from text, real-esrgan/upscale will upscale an image, and gfpgan/fix-faces will restore faces ")

    parser.add_argument('prompt',
                    nargs='+',
                    help='Prompt to convert to an image')

    args = parser.parse_args()

    (width, _, height) = args.size.partition('x')
    width = int(width)
    height = int(height)
    img = None
    outfile = None
    if args.tool[0] in STABLE_DIFFUSION_ALIASES:
        print('Stably diffusing')
        create_stable_diffusion(
            prompt=' '.join(args.prompt),
            outfile=args.out,
            img_prompt=args.img,
            img_mask=args.mask,
            width=width,
            height=height,
            num_inference_steps=args.inference_steps,
            guidance_scale=args.guidance,
            strength=args.strength,
        )

    elif args.tool[0] in REAL_ESRGAN_ALIASES:
        create_real_ersgan(args.prompt[0], args.scale, args.cartoon)
        outfile = get_png_filename('upscale_' + Path(args.prompt[0]).stem)
    elif args.tool[0] in GFPGAN_ALIASES:
        img = gfpgan(args.prompt[0])
        
    else:
        print('Woah now bad tool', args.tool)
        exit(1)
    
    if outfile is not None:
        print('Saving to ', outfile)
        img.save(outfile)
    
if __name__ == "__main__":
    main()
