import { SplitButton } from 'primereact/splitbutton';
import { Toolbar } from 'primereact/toolbar';
import { Button } from 'primereact/button';
import { Chip } from 'primereact/chip';

import "primereact/resources/primereact.min.css"; 
import 'primeicons/primeicons.css';

import React from 'react';
import { useEffect, useState } from 'react';
import { Menubar } from 'primereact/menubar';

const Header = React.forwardRef((props, ref) => {

    const [cost, setCost] = useState(0.0);

    useEffect(() => {
        const intervalId = setInterval(() => {
          fetch("/cost")
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error(`Failed to retrieve cost. Status code: ${response.status}`);
                }
            })
            .then((cost) => {
                setCost(cost);
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

    const costStr = `Cost incurred: $${cost.toFixed(5)}`;
    const costContent = (
        <React.Fragment>
            <Chip label={costStr} style={{fontWeight: 'bold', border: 'solid 2px', backgroundColor: 'var(--red-700)'}} />
        </React.Fragment>
    );


    return (
        <div style={{ width: '100%' }}>
            <Toolbar end={costContent} style={{padding: '0.4em'}}/>
        </div>
    );
});

export default Header;