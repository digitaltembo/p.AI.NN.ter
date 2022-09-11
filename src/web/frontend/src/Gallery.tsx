import React from "react";
import toast from "react-hot-toast";
import  ReactGallery, { PhotoClickHandler } from "react-photo-gallery";
import Carousel, { Modal, ModalGateway as BrokenModalGateway } from "react-images";
import { FileList } from "./types";

const ModalGateway = BrokenModalGateway as any;


function Gallery() {
  const [files, setFiles] = React.useState<FileList>({uploads: [], outputs: []});

  const [currentImage, setCurrentImage] = React.useState(0);
  const [viewerIsOpen, setViewerIsOpen] = React.useState(false);

  const openLightbox: PhotoClickHandler = React.useCallback((event, { photo, index }) => {
    setCurrentImage(index);
    setViewerIsOpen(true);
  }, []);

  const closeLightbox = () => {
    setCurrentImage(0);
    setViewerIsOpen(false);
  };


  React.useEffect(() => {
    fetch('/api/files')
      .then((res) => res.json())
      .then(setFiles)
      .catch((err) => toast("Failed to retrieve files"));
  }, []);


  return <>
    <ReactGallery 
      photos={files.outputs.map((src: string) => ({src, width:1, height:1}))}
      onClick={openLightbox}
    />
    <ModalGateway>
      {viewerIsOpen ? (
        <Modal onClose={closeLightbox}>
          <Carousel
            currentIndex={currentImage}
            views={files.outputs.map(source => ({
              source,
            }))}
          />
        </Modal>
      ) : null}
    </ModalGateway>
  </>
}

export default Gallery;