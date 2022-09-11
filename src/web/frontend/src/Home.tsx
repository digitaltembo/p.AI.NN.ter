import { CircularProgress } from "@mui/material";
import React from "react";
import styled from "styled-components";
import Prompt from "./Prompt";
import { Image, PromptInfo } from "./types";

const ImagePromptBox = styled.div``;
function Home() {

  const [isGenerating, setIsGenerating] = React.useState(false);
  const shouldBeGenerating = React.useRef<boolean>(false);
  const currentIndex = React.useRef<number>(0);

  const [images, setImages] = React.useState<Image[]>([]);
  const [imagePrompt, setImagePrompt] = React.useState<Image | null>(null)

  const [prompt, setPrompt] = React.useState<PromptInfo>({raw: "", components: [], prompts: [], promptDimensions: []});

  const handleStart = React.useCallback(async (promptInfo: PromptInfo) => {
    setPrompt(promptInfo);
    setIsGenerating(true);
    setImages([]);
    currentIndex.current = 0;
    shouldBeGenerating.current = true;
  }, [prompt]);

  const handleStop = React.useCallback(() => {
    setIsGenerating(false);
    shouldBeGenerating.current = false;
  }, []);

  React.useEffect(() => {
    let stop = false
    const callback = () => {
      console.log("Looking! for", prompt);
      if (shouldBeGenerating.current && prompt.prompts.length && !stop) {
        const currentPrompt = prompt.prompts[currentIndex.current];
        const url = new URL(document.baseURI + "api/transforms/stable-diffusion");
        const params: Record<string, string> = {
            prompt: currentPrompt,
        };
        if (imagePrompt) {
          params["image_prompt"] = encodeURIComponent(imagePrompt.src);
        }
        console.log("Loook", params);
        url.search = new URLSearchParams(params).toString()
        fetch(url.toString(), {method: 'POST'})
            .then((res) => res.json())
            .then((newImage) => {
              setImages((imgs) => [...imgs, newImage]);
              currentIndex.current = (currentIndex.current + 1) % prompt.prompts.length;
              callback();
            });
      }
    };
    callback();
    return () => { stop = false; };
  }, [prompt, imagePrompt]);
  return <>
    <Prompt
      isGenerating={isGenerating}
      onStop={handleStop}
      onStart={handleStart}
      setImagePrompt={setImagePrompt}
    />
    { imagePrompt && 
      <ImagePromptBox>
        <span>Searching for images in the style of:</span>
        <img src={imagePrompt.src} alt={imagePrompt.src} />
      </ImagePromptBox>}
    { images.map((img, i) => <img key={img.src} src={img.src} alt={img.alt} />) }
    { isGenerating &&  <CircularProgress /> }
  </>
}

export default Home;