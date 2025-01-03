import React from 'react';
import Upload from './Upload';
import Search from './Search';
import './index.css';

function App() {
  return (
    <div className="App">
      <h1>Intelligent Document Scanner</h1>
      <Upload />
      <Search />
    </div>
  );
}

export default App;
