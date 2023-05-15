import React, { useState, useRef, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { ScrollPanel } from 'primereact/scrollpanel';
import { Message } from 'primereact/message';
import { useFormik } from 'formik';
import { Dropdown } from 'primereact/dropdown';
import { Toast } from 'primereact/toast';
import { Tooltip } from 'primereact/tooltip';

const ChatHistory = () => {
  const [messages, setMessages] = useState([]);
  // const [newMessage, setNewMessage] = useState('');
  const chatContainerRef = useRef(null);
  const chatContentRef = useRef(null);
  const toast = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const actions = [
    { name: 'Add example'},
    { name: 'Remove example'},
    { name: 'Set template' },
    { name: 'Refine template'},
  ];

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
    //   console.log(chatContainerRef.current.getYBar());
      const chatContainerElement = chatContainerRef.current;
      const scrollHeight = chatContainerElement.scrollHeight;
      const clientHeight = chatContainerElement.clientHeight;
      const maxScrollTop = scrollHeight - clientHeight;

      if (maxScrollTop > 0) {
        chatContainerElement.scrollTop = maxScrollTop;
      }
    }
  };

  function getEndpointByActionName(actionName) {
    switch (actionName) {
      case 'Add example':
        return '/add_example';
      case 'Remove example':
        return '/remove_example';
      case 'Set template':
        return '/init_template';
      case 'Refine template':
        return '/refine';
      default:
        return ''; // Return a default endpoint or handle the invalid action name
    }
  }
  

  async function submitMessageToBackend(requestText, endpoint) {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: requestText })
      });
  
      // if (!response.ok) {
      //   throw new Error('Failed to submit message to the backend.');
      // }
  
      // Get response status
      const responseStatus = response.status;
      const responseText = await response.text();

      const serverMessage = {
        author: 'server',
        status: responseStatus === 200 ? 'success' : 'error',
        text: responseText,
      }
      return serverMessage;

      // console.log(responseText);
  
    } catch (error) {
      toast.current.show({ severity: 'error', summary: 'Failed to submit message to the backend', detail: `${error}` });
    }
  }

  const formik = useFormik({
      initialValues: {
          action: { name: 'Add example' },
          inputValue: ''
      },
      validate: (data) => {
          let errors = {};

          if (!data.action) {
              errors.action = 'Action is required.';
          }

          if (data.inputValue.trim() === '' && data.action.name !== 'Refine template') {
              errors.inputValue = 'Input Value is required.';
          }

          return errors;
      },
      onSubmit: async (data) => {
          // console.log(data);
          // data.action && show(data);

          const userMessage = {
            // action: data.action.name,
            text: data.action.name + ": " + data.inputValue.trim(),
            status: 'info',
            author: 'user'
          }
          setMessages([...messages, userMessage]);

          // Submit to backend
          const endpoint = getEndpointByActionName(data.action.name);
          if (endpoint) {
            try {
              const serverMessage = await submitMessageToBackend(data.inputValue, endpoint);
              if (serverMessage) {
                setMessages([...messages, userMessage, serverMessage]);
              }
        
              // Reset the form
              formik.resetForm({values: {...formik.values, inputValue: ''}});
        
            } catch (error) {
              toast.current.show({ severity: 'error', summary: 'Failed to submit message to the backend', detail: `${error}` });
            }
          } else {
            toast.current.show({ severity: 'error', summary: 'Invalid Action', detail: `${data.action.name} is not an action` });
          }

          // formik.resetForm();
      }
  });

  const isFormFieldInvalid = (name) => !!(formik.touched[name] && formik.errors[name]);

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      // handleSendMessage();
      formik.handleSubmit();
    }
  };


  return (
    <div className="chat-container">
      <div className="chat-history"  >
        <ScrollPanel
          ref={chatContainerRef}
          style={{height: `calc(100vh - 150px)`}}
        >
        <div ref={chatContentRef}>
        {messages.map((message, index) => {

          // const content = (
          //   <div className="flex align-items-center">
          //       {/* <img alt="logo" src="https://primefaces.org/cdn/primereact/images/logo.png" width="32" /> */}
          //       <div>{message}</div>
          //   </div>
          // );
          // const content = message.action + ": " + message.text;
          const justifyPos = message.author === 'user' ? 'right' : 'left';
          // const severity = message.author === 'user' ? 'success' : 'info';

          return (<div key={index} className="message" style={{justifyContent: justifyPos}}>
            <Message content={message.text} className={`message-${index}`} severity={message.status} style={{
                    // border: 'solid #696cff',
                    borderWidth: '0 0 0 6px',
                    // color: '#696cff',
                    padding: '0.25em'
                }} />
            {/* <Tooltip target={`.message-${index}`} position="right" content={`Tooltip for Message ${index}`} style={{padding: '0.25em'}}/> */}
          </div>);
        })}
        </div>
        </ScrollPanel>
      </div>
      <div className="chat-input" style={{width: "100%"}}>
            {/* <i className="pi pi-star-fill"></i> */}
          {/* <SpeedDial model={items} direction="up" radius={20} buttonStyle={{ width: '24px', height: '24px', fontSize: '12px' }} /> */}
          <form onSubmit={formik.handleSubmit}  style={{width: "100%"}}>
            <Toast ref={toast} />
            <Dropdown
                inputId="city"
                name="city"
                value={formik.values.action}
                options={actions}
                optionLabel="name"
                placeholder="Select an action"
                onChange={(e) => {
                    formik.setFieldValue('action', e.value);
                }}
                className={isFormFieldInvalid('action') ? 'p-invalid' : null}
                style={{fontSize: "12px", height: "50px"}}
            />
            {/* <div className="p-inputgroup"> */}
            <InputText
              value={formik.values.inputValue}
              onChange={(e) => {formik.setFieldValue('inputValue', e.target.value);}}
              onKeyDown={handleKeyDown}
              placeholder="Type a message..."
              className="message-input"
              style={{ width: "calc(100% - 280px)", height: "50px" }} 
            />
            <Button
              label="Send"
              // icon="pi pi-check"
              // onClick={handleSendMessage}
              className="send-button"
              type="submit"
              style={{height: "50px"}}
            />
            {/* </div> */}
          </form>
      </div>
    </div>
  );
};

export default ChatHistory;
