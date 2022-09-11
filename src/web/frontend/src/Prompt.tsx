import React from "react";
import styled from "styled-components";
import { Button, Divider, IconButton, InputBase, Paper, TextField } from "@mui/material";
import { AddPhotoAlternate, Dangerous, ImagesearchRoller, Settings } from "@mui/icons-material";

const SmallPromptBox = styled.div`
  display: flex;
  width: 100%;
  flex-direction: row;
`;

export type PromptInfo = {
  raw: string;
  prompts: string[];
  promptDimensions: number[];
}

type Props = {
  isGenerating: boolean;
  onStart: (prompt: PromptInfo) => void;
  onStop: () => void;
};

function Prompt({isGenerating, onStart, onStop}: Props) {
  const [promptStr, setPromptStr] = React.useState<string>("");

  const [isFocused, setIsFocused] = React.useState(false);
  const handleFocus = React.useCallback(() => {
    setIsFocused(true);
    onStop();
  }, [onStop]);
  const prompt = React.useMemo(() => ({
    raw: promptStr,
    prompts: [promptStr],
    promptDimensions: [1],
  }), [promptStr]);

  const handleClick = React.useCallback(() => {
    if (isGenerating) {
      onStop();
    } else {
      setIsFocused(false);
      onStart(prompt);
    }
  }, [onStart, prompt]);


  return <>
    <SmallPromptBox>

      <TextField
        sx={{ ml: 1, flex: 1 }}
        placeholder="Prompt Stable Diffusion"
        value={promptStr}
        onChange={(evt) => setPromptStr(evt.target.value)}
        onFocus={handleFocus}
        onBlur={() => setIsFocused(false)}
        variant="standard"
      />
      <IconButton 
        type="button"
        sx={{ p: '10px' }}
        aria-label="search"
        onClick={handleClick}
        color={isGenerating ? "error" : "primary" }
      >
        {isGenerating ? <Dangerous /> : <ImagesearchRoller /> }
      </IconButton>
      <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />

      <IconButton sx={{ p: '10px' }} aria-label="directions">
        <AddPhotoAlternate />
      </IconButton>
    <IconButton sx={{ p: '10px' }} aria-label="directions">
        <Settings />
      </IconButton>

    </SmallPromptBox>
  </>;
}

export default Prompt;