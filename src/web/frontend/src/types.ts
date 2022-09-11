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