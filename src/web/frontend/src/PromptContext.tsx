import React from 'react';
import {
  ImageInfo,
  PromptComponent,
  PromptInfo,
  StableDiffusionParameters,
} from './types';

type PromptCoord = number[];
type PromptContextTypr = {
  promptInfo: PromptInfo;
  setPromptInfo: (newPromptInfo: PromptInfo) => void;
  setPromptComponents: (
    transform: (input: PromptComponent[]) => PromptComponent[]
  ) => void;
  parameters: StableDiffusionParameters;
  setParameters: (
    either:
      | StableDiffusionParameters
      | ((input: StableDiffusionParameters) => StableDiffusionParameters)
  ) => void;

  getNextStableDiffusion: () => Promise<ImageInfo>;
};

export const DEFAULT_PROMPT_CONTEXT: PromptContextTypr = {
  promptInfo: {
    raw: '',
    components: [
      {
        alts: [''],
        active: '',
      },
    ],
    prompts: [],
    promptDimensions: [1],
  },
  setPromptInfo: () => {},
  setPromptComponents: () => {},
  parameters: {},
  setParameters: () => {},
  getNextStableDiffusion: () => Promise.reject(new Error('unimplemented')),
};

export const PromptContext = React.createContext<PromptContextTypr>(
  DEFAULT_PROMPT_CONTEXT
);

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

const OPTIONAL_PARAMS: {[key: string]: (p: StableDiffusionParameters) => string | number | boolean | undefined} = {
  "image_prompt": (p) => p.promptImage?.src,
  "width": (p) => p.width,
  "height": (p) => p.height,
  "fix_faces": (p) => p.fixFaces,
  "upscale": (p) => p.upscale,
};

export function PromptContextProvider({
  children,
}: React.PropsWithChildren<{}>) {
  const [promptInfo, setPromptInfo] = React.useState<PromptInfo>(
    DEFAULT_PROMPT_CONTEXT.promptInfo
  );
  const [parameters, setParameters] = React.useState<StableDiffusionParameters>(
    {}
  );

  const promptIndex = React.useRef(0);

  const handleNewPrompt = React.useCallback((newPrompt: PromptInfo) => {
    promptIndex.current = 0;
    setPromptInfo(newPrompt);
  }, []);

  const getNextStableDiffusion = React.useCallback(() => {
    console.log("starting stable diffusion?");
    const currentPrompt = promptInfo.prompts[promptIndex.current];
    const url = new URL(document.baseURI + 'api/transforms/stable-diffusion');
    const params: Record<string, string> = {
      prompt: currentPrompt,
    };
    for (const key of Object.keys(OPTIONAL_PARAMS)) {
      const val = OPTIONAL_PARAMS[key](parameters);
      if (val !== undefined) {
        params[key] = encodeURIComponent(val);
      }
    }
    url.search = new URLSearchParams(params).toString();
    return fetch(url.toString(), { method: 'POST' })
      .then((res) => res.json())
      .then((res) => res as ImageInfo);
  }, [promptInfo, parameters]);

  const setPromptComponents = React.useCallback(
    (transform: (input: PromptComponent[]) => PromptComponent[]) => {
      promptIndex.current = 0;
      setPromptInfo(({ components }) => getPromptInfo(transform(components)));
    },
    []
  );

  const value = React.useMemo(
    () => ({
      promptInfo,
      setPromptInfo: handleNewPrompt,
      setPromptComponents,
      parameters,
      setParameters,
      getNextStableDiffusion,
    }),
    [
      promptInfo,
      parameters,
      getNextStableDiffusion,
      handleNewPrompt,
      setPromptComponents,
    ]
  );

  return (
    <PromptContext.Provider value={value}>{children}</PromptContext.Provider>
  );
}
