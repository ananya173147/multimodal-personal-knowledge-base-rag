import React, { useState } from 'react';
import axios from 'axios';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const response = await axios.post("http://localhost:8000/query", { query });
    setResults(response.data);
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Search documents"
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>
      <ul>
        {results.map((res, index) => (
          <li key={index}>{res}</li>
        ))}
      </ul>
    </div>
  );
}

export default Search;
