import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [chat, setChat] = useState([]);
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Handle query input change
  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  // Handle query form submission
  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { sender: 'user', text: query };
    setChat((prevChat) => [...prevChat, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/query/?query=${query}`);
      if (!response.ok) throw new Error('Failed to fetch the answer');

      const data = await response.json();
      const botMessage = { sender: 'bot', text: data.answer };
      setChat((prevChat) => [...prevChat, botMessage]);
    } catch (error) {
      const botMessage = { sender: 'bot', text: 'Error retrieving the answer' };
      setChat((prevChat) => [...prevChat, botMessage]);
    } finally {
      setIsLoading(false);
      setQuery('');
    }
  };

  // Handle file input change
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // Handle file upload form submission
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch('http://localhost:8000/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to upload the file');
      
      const data = await response.json();
      alert(data.message);
    } catch (error) {
      alert('Error uploading file!');
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <h1>Knowledge Base</h1>

        {/* Chat Box */}
        <div className="chat-box">
          {chat.map((message, index) => (
            <div key={index} className={`chat-message ${message.sender}`}>
              <p>{message.text}</p>
            </div>
          ))}
          {isLoading && <div className="chat-message bot"><p>Loading...</p></div>}
        </div>

        {/* Query Form */}
        <form onSubmit={handleQuerySubmit} className="query-form">
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            placeholder="Ask a question..."
          />
          <button type="submit" disabled={isLoading}>Send</button>
        </form>

        {/* File Upload Form */}
        <form onSubmit={handleFileUpload} className="file-upload-form">
          <input type="file" onChange={handleFileChange} />
          <button type="submit">Upload File</button>
        </form>
      </div>
    </div>
  );
}

export default App;
