import React, { useEffect } from "react";

function App() {

  useEffect(() => {
  fetch("/api/health")   // ✅ no IP needed
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.error(err));
}, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>hi darshan</h1>
      </header>
    </div>
  );
}

export default App;