export type Image = {
  src: string;
  width: number;
  height: number;
  alt: string;
}

export type FileList = {
  uploads: string[],
  outputs: string[]
};