import React from 'react';
import styled from "styled-components";
import {
  BrowserRouter,
  Routes,
  Route,
  Link as RouterLink,
} from "react-router-dom";
import { Link } from "@mui/material";

import GalleryPage from "./photos/GalleryPage";
import Home from './home/Home';
import { PromptContextProvider } from './PromptContext';

const Header = styled.nav`
  display: flex;
  width: 100%;    
  flex-direction: row;
  justify-content: space-evenly;
`;
function App() {

  return (
    <BrowserRouter>
      <Header>
        <Link component={RouterLink} to="/" color="inherit" variant="h3">p.ai.nn.ter</Link>
        <Link component={RouterLink} to="/gallery" color="inherit" variant="h3">gallery</Link>
      </Header>
      <PromptContextProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/gallery" element={<GalleryPage />} />
        </Routes>
      </PromptContextProvider>
    </BrowserRouter>
  );
}

export default App;
