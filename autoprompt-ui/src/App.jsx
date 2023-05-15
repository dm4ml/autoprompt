import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

//theme
// import "primereact/resources/themes/mdc-dark-deeppurple/theme.css";    
// import "primereact/resources/themes/lara-dark-teal/theme.css"; 
import "primereact/resources/themes/vela-blue/theme.css";
    
//core
import "primereact/resources/primereact.min.css"; 
import 'primeicons/primeicons.css';

import React from 'react'; 

import Header from './header';
import { Splitter, SplitterPanel } from 'primereact/splitter';
import { Message } from 'primereact/message';
import ChatHistory from './chat';
import PromptTable from './table';

// Components:
// * Card for initial form (with button)
// * Card for incremental updates
// * Displays of prompts

function App() {

  return (
    <div style={{ width: '100%' }}>
      <Header />
      <div style={{ display: 'flex', flexDirection: 'column', height: `calc(100vh - 100px)` }}>
      <Splitter style={{ flex: 1, marginTop: '5px' }}>
          <SplitterPanel size={60} className="flex align-items-center justify-content-center" style={{height: `calc(100vh - 80px)`}}>
            <Message severity="info" text="Prompt templates, including the best template, update every 5 iterations of 'refine.' This allows for parallel exploration from a single template." style={{width: '100%', textAlign: "left", justifyContent: "left"}}/>
            <PromptTable />
          </SplitterPanel>
          <SplitterPanel size={40} className="flex align-items-center justify-content-center" style={{height: `calc(100vh - 80px)`}}>
            <ChatHistory />
          </SplitterPanel>
      </Splitter>
      </div>
    </div>
  )
}

export default App
