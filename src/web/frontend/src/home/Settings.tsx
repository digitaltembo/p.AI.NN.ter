import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  TextField,
  DialogActions,
  Button,
  FormControlLabel,
  Checkbox,
  Slider,
  Box,
} from '@mui/material';
import React from 'react';
import { PromptContext } from '../PromptContext';
import { StableDiffusionParameters } from '../types';

const MAX_IMAGE_SIZE = 1000;

type Props = {
  open: boolean;
  onClose: () => void;
};

type Size = {
  width: string;
  height: string;
};

function getSizing(
  width: number,
  height: number,
  upscale?: number
): Partial<StableDiffusionParameters> {
  if (upscale == null) {
    return { width, height, upscale: undefined };
  } else if (width > height) {
    return {
      width: (width / height) * 512,
      height: 512,
      upscale: Math.max(height / 512, 1),
    };
  } else {
    return {
      width: 512,
      height: (height / width) * 512,
      upscale: Math.max(width / 512, 1),
    };
  }
}

function Settings({ open, onClose }: Props) {
  const { parameters, setParameters } = React.useContext(PromptContext);
  const toggleFixFaces = React.useCallback(() => {
    setParameters((params) => ({ ...params, fixFaces: !params.fixFaces }));
  }, [setParameters]);

  const [size, setSize] = React.useState<Size>({ width: '512', height: '512' });

  const setWidth = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setSize((s) => ({ ...s, width: event.target.value }));
      const newWidth = parseInt(event.target.value);

      if (!Number.isNaN(newWidth)) {
        setParameters((params) => ({
          ...params,
          ...getSizing(newWidth, params.height ?? 512, params.upscale),
        }));
      }
    },
    [setParameters]
  );

  const setHeight = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setSize((s) => ({ ...s, height: event.target.value }));

      const newHeight = parseInt(event.target.value);
      if (!Number.isNaN(newHeight)) {
        setParameters((params) => ({
          ...params,
          ...getSizing(params.width ?? 512, newHeight, params.upscale),
        }));
      }
    },
    [setParameters]
  );

  const toggleUpscale = React.useCallback(() => {
    setParameters((params) => ({
      ...params,
      ...getSizing(
        params.width ?? 512,
        params.height ?? 512,
        params.upscale == null ? 1 : undefined
      ),
    }));
  }, [setParameters]);

  const irregularSize = React.useMemo(
    () =>
      parameters.upscale != null ||
      (parameters.width && parameters.width > MAX_IMAGE_SIZE) ||
      (parameters.height && parameters.height > MAX_IMAGE_SIZE) ||
      (parameters.width &&
        parameters.height &&
        parameters.width !== 512 &&
        parameters.height !== 512),
    [parameters.width, parameters.height, parameters.upscale]
  );

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Stable Diffusion Settings</DialogTitle>
      <DialogContent>
        <DialogContentText>
          The defaults should work fairly well, but in case you want to tweak
          any of the parameters
        </DialogContentText>
        <TextField label="Width" value={size.width} onChange={setWidth} />
        <TextField label="Height" value={size.height} onChange={setHeight} />
        
        <FormControlLabel
          control={
            <Checkbox checked={parameters.fixFaces} onClick={toggleFixFaces} />
          }
          label="Automatically Fix Faces with GFPGAN"
        />
        {irregularSize && (
          <FormControlLabel
            control={
              <Checkbox
                checked={parameters.upscale != null}
                onClick={toggleUpscale}
              />
            }
            label="Use Real-ERSGAN to acheive desired image size"
          />
        )}
        <p>Will generate a {parameters.width ?? 512}x{parameters.height ?? 512} image</p>

        <Box>
          Number of Inference Steps
          <Slider
            defaultValue={50}
            aria-label="Number of Inference Steps"
            valueLabelDisplay="auto"
          />
        </Box>
        <Box>
          Guidance Scale
          <Slider
            defaultValue={50}
            aria-label="Guidance Scale"
            valueLabelDisplay="auto"
          />
        </Box>
        <Box>
          η
          <Slider defaultValue={50} aria-label="eta" valueLabelDisplay="auto" />
        </Box>
        <Box>
          Strength
          <Slider
            defaultValue={50}
            aria-label="strength"
            valueLabelDisplay="auto"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}

export default Settings;
