import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import {Tag} from 'primereact/tag';

import { useState, useEffect } from 'react';


const CustomBodyTemplate = (rowData, column) => {
    return (
      <div style={{ whiteSpace: 'normal', wordWrap: 'break-word' }}>
        {rowData[column.field]}
      </div>
    );
  };

export default function PromptTable(props) {

    const [expandedRows, setExpandedRows] = useState(null);
    const [templates, setTemplates] = useState([]);
    const [best, setBest] = useState([]);

    useEffect(() => {
        const intervalId = setInterval(() => {
          fetch("/templates_and_results")
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error(`Failed to retrieve templates_and_results. Status code: ${response.status}`);
                }
            })
            .then((data) => {
                // set up rows and frozen rows
                // console.log(data);
                const rows = data.filter((item) => item.status !== 'best');
                const frozenRows = data.filter((item) => item.status === 'best');
                setTemplates(rows);
                setBest(frozenRows);
            })
            .catch((error) => {
                console.error("Error:", error);
            });

        }, 5000);
    
        return () => {
          // Clear the interval when the component unmounts
          clearInterval(intervalId);
        };
    }, []);

    const products = [
        {
          template: 'template3 this one is so long and so many words to see if it will actually wrap. i will be very curious to see if it will wrap.',
          results: [
            {
                prompt: 'bunnypromptttt',
                completion: 'this is a bunny rabbit'
            }, 
            {
                prompt: 'catprompttt',
                completion: 'this is a cat'
            }
          ],
          status: 'best',
        },
        {
            template: 'template1 this one is short',
            results: [
              {
                  prompt: 'aoeuaoeu',
                  completion: 'this is a bunny rabbit'
              }, 
              {
                  prompt: '.....',
                  completion: 'this is a cat'
              }
            ],
            status: 'n/a',
          },
      ];
    


    const rowExpansionTemplate = (data) => {
        return (
            <div className="p-3">
                {/* <h5>Orders for {data.name}</h5> */}
                <DataTable value={data.results} showGridlines>
                    <Column field="prompt" header="Prompt" />
                    <Column field="completion" header="Completion" />
                </DataTable>
            </div>
        );
    };

    const getSeverity = (status) => {
        switch (status) {
            case 'n/a':
                return 'info';

            case 'best':
                return 'success';
        }
    };

    const statusBodyTemplate = (rowData) => {
        return <Tag value={rowData.status} severity={getSeverity(rowData.status)} />;
    };


    return (
        <DataTable stripedRows size="small" value={templates} frozenValue={best} scrollable scrollHeight="flex" rowExpansionTemplate={rowExpansionTemplate}
        onRowToggle={(e) => setExpandedRows(e.data)} expandedRows={expandedRows}
         >
            <Column expander={true} />
              {/* {columns.map((column) => (
                <Column
                  key={column.field}
                  field={column.field}
                  header={column.header}
                  body={CustomBodyTemplate}
                />
              ))} */}
              <Column
                  key="status"
                  field="status"
                  header="Status"
                  body={statusBodyTemplate}
                />
              <Column
                  key="template"
                  field="template"
                  header="Prompt Template"
                  body={CustomBodyTemplate}
                />
                {/* <Column field="template" header="Template"></Column> */}
                {/* <Column field="name" header="Name"></Column>
                <Column field="category" header="Category"></Column>
                <Column field="quantity" header="Quantity"></Column> */}
            </DataTable>
      );
}