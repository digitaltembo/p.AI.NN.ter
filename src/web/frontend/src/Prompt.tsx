import React from "react";
import { Button, TextField } from "@mui/material";
import ColorLensIcon from '@mui/icons-material/ColorLens';

export type PromptInfo = {
  raw: string;
  prompts: string[];
  promptDimensions: number[];
}

type Props = {
  onFocus: () => void;
  onStart: (prompt: PromptInfo) => void;
};

function Prompt({onFocus, onStart}: Props) {
  const [promptStr, setPromptStr] = React.useState<string>("");

  const [isFocused, setIsFocused] = React.useState(false);
  const handleFocus = React.useCallback(() => {
    setIsFocused(true);
    onFocus();
  }, [onFocus]);
  const prompt = React.useMemo(() => ({
    raw: promptStr,
    prompts: [promptStr],
    promptDimensions: [1],
  }), [promptStr]);

  const handleClick = React.useCallback(() => {
    setIsFocused(false);
    onStart(prompt);
  }, [onStart, prompt]);


  return <>
    <TextField
      value={promptStr}
      onChange={(evt) => setPromptStr(evt.target.value)}
      onFocus={handleFocus}
      onBlur={() => setIsFocused(false)}
      variant="standard" />
    <Button onClick={handleClick} variant="contained" endIcon={<ColorLensIcon />}>Create</Button>
  </>;
}

export default Prompt;