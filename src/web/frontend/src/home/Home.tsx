import { CircularProgress } from "@mui/material";
import React from "react";
import styled from "styled-components";
import { PromptContext } from "../PromptContext";

import { ImageInfo } from "../types";
import Prompt from "./Prompt";

const ImagePromptBox = styled.div``;
function Home() {
  const {getNextStableDiffusion, parameters} = React.useContext(PromptContext);

  const [isGenerating, setIsGenerating] = React.useState(false);
  const shouldBeGenerating = React.useRef<boolean>(false);
  const [images, setImages] = React.useState<ImageInfo[]>([]);

  const handleStart = React.useCallback(async () => {
    setIsGenerating(true);
    setImages([]);
    shouldBeGenerating.current = true;
  }, []);

  const handleStop = React.useCallback(() => {
    setIsGenerating(false);
    shouldBeGenerating.current = false;
  }, []);

  React.useEffect(() => {
    let stop = false
    const callback = () => {
      if (shouldBeGenerating.current && !stop) {
        getNextStableDiffusion().then((newImage) => {
          setImages((imgs) => [...imgs, newImage]);
          callback();
        })
      }
    };
    callback();
    return () => { stop = false; };
  }, [getNextStableDiffusion]);

  return <>
    <Prompt
      isGenerating={isGenerating}
      onStop={handleStop}
      onStart={handleStart}
    />
    { parameters.promptImage && 
      <ImagePromptBox>
        <span>Searching for images in the style of:</span>
        <img src={parameters.promptImage.src} alt={parameters.promptImage.src} />
      </ImagePromptBox>}
    { images.map((img, i) => <img key={img.src} src={img.src} alt={img.alt} />) }
    { isGenerating &&  <CircularProgress /> }
  </>
}

export default Home;