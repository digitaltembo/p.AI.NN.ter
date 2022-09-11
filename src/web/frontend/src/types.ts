export type ImageInfo = {
  id: number;
  isUpload: number;
  referenceImage: number;
  src: string;
  time: number;
  alt: string;
  width: number;
  height: number;
}

export type FileList = {
  uploads: ImageInfo[],
  outputs: ImageInfo[]
};

export type PromptComponent = {
  label?: string;
  alts: string[];
  active: string;
}
export type PromptInfo = {
  raw: string;
  components: PromptComponent[];
  prompts: string[];
  promptDimensions: number[];
};

export type StableDiffusionParameters = {
  // Width and Height should probably not deviate too much from 512, which is the size of image
  // that stable diffusion was trained at
  // Different aspect ratios should likely be represented by having one of the image sizes be 512
  // and further changes in size should be defined in the upscale parameter, which will upscale 
  // vai Real-ERSGAN
  width?: number;
  height?: number;
  upscale?: number;
  // If set to true, will run GFPGAN to try and fix the faces
  fixFaces?: boolean;
  // Image and mask to use in stable diffusion
  promptImage?: ImageInfo;
  promptMask?: ImageInfo;
  // Probably around 50 is Good Enough
  numInferenceSteps?: number;
  // Probably around 7.5 is Good Enough
  guidanceScale?: number;
  // Probably should be 0, although TODO: read about this https://arxiv.org/abs/2010.02502m
  eta?: number;
  // Strength by which the prompt image is considered, should be around 0.8
  strength?: number;
}