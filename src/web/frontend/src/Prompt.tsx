import React from 'react';
import styled from 'styled-components';
import { Divider, IconButton, TextField } from '@mui/material';
import {
  AddPhotoAlternate,
  Dangerous,
  ImagesearchRoller,
  Settings,
} from '@mui/icons-material';
import { Image, PromptInfo, PromptComponent } from './types';

const SmallPromptBox = styled.div`
  display: flex;
  width: 100%;
  flex-direction: row;
`;

type PromptCoord = number[];

type Props = {
  isGenerating: boolean;
  onStart: (prompt: PromptInfo) => void;
  onStop: () => void;
  setImagePrompt: (imagePath: Image | null) => void;
};

function getPromptAtCoord(components: PromptComponent[], coord: PromptCoord) {
  const parts = [];
  let coordIndex = 0;
  for (const component of components) {
    if (component.alts.length === 1) {
      parts.push(component.alts[0]);
    } else {
      parts.push(component.alts[coord[coordIndex]]);
      coordIndex += 1;
    }
  }
  return parts.join(' ');
}
function getPromptInfo(components: PromptComponent[]): PromptInfo {
  const raw = components
    .map(({ alts }) =>
      alts.length > 1 ? `(${alts.join(' | ')})` : alts[0] ?? ''
    )
    .join(' ');
  // "Dimensions" here refers to the choices that can be made in the construction of the prompt
  const promptDimensions = [
    1,
    ...components.map(({ alts }) => alts.length).filter((dim) => dim !== 1),
  ];

  // Create a list of coordinates a la [[0,0,0], [0,0,1], [0,1,0], etc...]
  // that represent choices between the alternatives in the prompt components
  // By a) going through the dimensions one by one
  const promptCoords = promptDimensions.reduce<PromptCoord[]>(
    (oldCoords, dimension) =>
      // and taking each newCoord from that dimension, 0...n
      Array(dimension)
        .fill(0)
        .reduce<PromptCoord[]>(
          (newCoords: PromptCoord[], _, newDimensionValue: number) => [
            ...newCoords,
            // and adding it to the end of all the coordinates previously processed
            ...oldCoords.map((oldCoord) => [...oldCoord, newDimensionValue]),
          ],
          []
        ),
    [[]]
  );

  const prompts = promptCoords.map((coord) =>
    getPromptAtCoord(components, coord)
  );
  return { raw, components, promptDimensions, prompts };
}

function Prompt({ isGenerating, onStart, onStop, setImagePrompt }: Props) {
  const [promptComponents, setPromptComponents] = React.useState<
    PromptComponent[]
  >([
    {
      alts: [''],
      active: '',
    },
  ]);

  const [isFocused, setIsFocused] = React.useState(false);
  const handleFocus = React.useCallback(() => {
    setIsFocused(true);
    onStop();
  }, [onStop]);
  const prompt = React.useMemo(
    () => getPromptInfo(promptComponents),
    [promptComponents]
  );

  const handleClick = React.useCallback(() => {
    if (isGenerating) {
      onStop();
    } else {
      setIsFocused(false);
      onStart(prompt);
    }
  }, [onStart, prompt]);

  const handleFileUpload = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        fetch('/api/files/upload', { method: 'POST', body: formData })
          .then((res) => res.json())
          .then((res) => setImagePrompt(res));
      }
    },
    [setImagePrompt]
  );

  const handleTextInput = React.useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setPromptComponents((components) => {
      const lastComponent = components[components.length - 1];
      lastComponent.alts[0] = event.target.value;
      return [...components.slice(0, -1), lastComponent];
    });
  }, []);

  return (
    <>
      <SmallPromptBox>
        <TextField
          sx={{ ml: 1, flex: 1 }}
          placeholder="Prompt Stable Diffusion"
          value={prompt.raw}
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
