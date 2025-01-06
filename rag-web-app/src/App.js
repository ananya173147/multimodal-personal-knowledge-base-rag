import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [chat, setChat] = useState([]);
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // Fetch files on component mount and after uploads
  const fetchFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/files/');
      if (!response.ok) throw new Error('Failed to fetch files');
      const data = await response.json();
      setUploadedFiles(data.files);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

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

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

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
      fetchFiles(); // Refresh the file list after successful upload
    } catch (error) {
      alert('Error uploading file!');
    }
  };

  return (
    <div className="App">
      <div className="app-container">
        <div className="files-sidebar">
          <h2>Uploaded Files</h2>
          <div className="files-list">
            {uploadedFiles.length > 0 ? (
              uploadedFiles.map((fileName, index) => (
                <div key={index} className="file-item">
                  <span className="file-icon">📄</span>
                  <span className="file-name">{fileName}</span>
                </div>
              ))
            ) : (
              <p className="no-files">No files uploaded yet</p>
            )}
          </div>
          <form onSubmit={handleFileUpload} className="file-upload-form">
            <input 
              type="file" 
              onChange={handleFileChange}
              className="file-input" 
            />
            <button type="submit" className="upload-button">
              Upload File
            </button>
          </form>
        </div>

        <div className="chat-container">
          <h1>Knowledge Base</h1>
          <div className="chat-box">
            {chat.map((message, index) => (
              <div key={index} className={`chat-message ${message.sender}`}>
                <p>{message.text}</p>
              </div>
            ))}
            {isLoading && <div className="chat-message bot"><p>Loading...</p></div>}
          </div>
          <form onSubmit={handleQuerySubmit} className="query-form">
            <input
              type="text"
              value={query}
              onChange={handleQueryChange}
              placeholder="Ask a question..."
              className="query-input"
            />
            <button type="submit" disabled={isLoading} className="send-button">
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
