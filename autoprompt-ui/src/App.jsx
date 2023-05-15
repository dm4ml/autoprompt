import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

//theme
import "primereact/resources/themes/soho-dark/theme.css";     
    
//core
import "primereact/resources/primereact.min.css"; 
import 'primeicons/primeicons.css';

import React from 'react'; 

import Header from './header';
import { Splitter, SplitterPanel } from 'primereact/splitter';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import ChatHistory from './chat';

// Components:
// * Card for initial form (with button)
// * Card for incremental updates
// * Displays of prompts

const CustomBodyTemplate = (rowData, column) => {
  return (
    <div style={{ whiteSpace: 'normal', wordWrap: 'break-word' }}>
      {rowData[column.field]}
    </div>
  );
};

function App() {
  const [count, setCount] = useState(0)

  const products = [
    {
      template: 'template1',
    },
    {
      template: 'template2',
    },
    {
      template: 'template3',
    },
    {
      template: 'template1',
    },
    {
      template: 'template2',
    },
    {
      template: 'template3',
    },
    {
      template: 'template1',
    },
    {
      template: 'template2',
    },
    {
      template: 'template3',
    },
    {
      template: 'template1',
    },
    {
      template: 'template2',
    },
    {
      template: 'template3 this one is so long and so many words to see if it will actually wrap. i will be very curious to see if it will wrap.',
    },
  ];

  const columns = [
    { field: 'template', header: 'Prompt Template' },
    // ... other columns
  ];

  return (
    <div style={{ width: '100%' }}>
      <Header />
      <div style={{ display: 'flex', flexDirection: 'column', height: `calc(100vh - 100px)` }}>
      <Splitter style={{ flex: 1, marginTop: '5px' }}>
          <SplitterPanel className="flex align-items-center justify-content-center" style={{height: `calc(100vh - 80px)`}}>
            <DataTable stripedRows size="small" value={products} scrollable scrollHeight="flex" >
              {columns.map((column) => (
                <Column
                  key={column.field}
                  field={column.field}
                  header={column.header}
                  body={CustomBodyTemplate}
                />
              ))}
                {/* <Column field="template" header="Template"></Column> */}
                {/* <Column field="name" header="Name"></Column>
                <Column field="category" header="Category"></Column>
                <Column field="quantity" header="Quantity"></Column> */}
            </DataTable>
          </SplitterPanel>
          <SplitterPanel className="flex align-items-center justify-content-center" style={{height: `calc(100vh - 80px)`}}>
            <ChatHistory />
          </SplitterPanel>
      </Splitter>
      </div>
    </div>
  )
}

export default App
