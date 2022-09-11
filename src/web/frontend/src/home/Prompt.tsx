import React from 'react';
import styled from 'styled-components';
import { Divider, IconButton, TextField } from '@mui/material';
import {
  AddPhotoAlternate,
  Dangerous,
  ImagesearchRoller,
  Settings,
} from '@mui/icons-material';
import { PromptContext } from '../PromptContext';

const SmallPromptBox = styled.div`
  display: flex;
  width: 100%;
  flex-direction: row;
`;

type Props = {
  isGenerating: boolean;
  onStart: () => void;
  onStop: () => void;
};

function Prompt({ isGenerating, onStart, onStop }: Props) {
  const { setParameters, setPromptComponents, promptInfo } = React.useContext(PromptContext);

  const [isFocused, setIsFocused] = React.useState(false);
  const handleFocus = React.useCallback(() => {
    setIsFocused(true);
    onStop();
  }, [onStop]);

  const handleClick = React.useCallback(() => {
    if (isGenerating) {
      onStop();
    } else {
      setIsFocused(false);
      onStart();
    }
  }, [isGenerating, onStart, onStop]);

  const handleFileUpload = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        fetch('/api/files/upload', { method: 'POST', body: formData })
          .then((res) => res.json())
          .then((res) => setParameters((params) => ({...params, imagePrompt: res})));
      }
    },
    [setParameters]
  );

  const handleTextInput = React.useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setPromptComponents((components) => {
      const lastComponent = components[components.length - 1];
      lastComponent.alts[0] = event.target.value;
      return [...components.slice(0, -1), lastComponent];
    });
  }, [setPromptComponents]);

  return (
    <>
      <SmallPromptBox>
        <TextField
          sx={{ ml: 1, flex: 1 }}
          placeholder="Prompt Stable Diffusion"
          value={promptInfo.raw}
          onChange={handleTextInput}
          onFocus={handleFocus}
          onBlur={() => setIsFocused(false)}
          variant="standard"
        />
        <IconButton
          type="button"
          sx={{ p: '10px' }}
          aria-label="search"
          onClick={handleClick}
          color={isGenerating ? 'error' : 'primary'}
        >
          {isGenerating ? <Dangerous /> : <ImagesearchRoller />}
        </IconButton>
        <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />

        <IconButton
          sx={{ p: '10px' }}
          aria-label="directions"
          component="label"
        >
          <input
            hidden
            accept="image/*"
            type="file"
            onChange={handleFileUpload}
          />
          <AddPhotoAlternate />
        </IconButton>
        <IconButton sx={{ p: '10px' }} aria-label="directions">
          <Settings />
        </IconButton>
      </SmallPromptBox>
    </>
  );
}

export default Prompt;
