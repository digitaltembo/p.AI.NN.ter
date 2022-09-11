export type Image = {
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
  uploads: Image[],
  outputs: Image[]
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