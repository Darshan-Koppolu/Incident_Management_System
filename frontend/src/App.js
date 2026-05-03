import React, { useEffect } from "react";

function App() {

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then(res => res.json())
      .then(data => console.log("Backend Response:", data))
      .catch(err => console.error("Error:", err));
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