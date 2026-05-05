import React, { useEffect, useState } from "react";

function App() {
  const [incidents, setIncidents] = useState([]);

  const fetchData = () => {
    fetch("http://13.232.110.46:8000/api/incidents")
      .then(res => res.json())
      .then(data => setIncidents(data))
      .catch(err => console.error("Error:", err));
  };

  useEffect(() => {
    fetchData();

    // auto refresh every 5 sec
    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>🚨 Incident Dashboard</h1>

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>ID</th>
            <th>Component</th>
            <th>Message</th>
            <th>Status</th>
            <th>Time</th>
          </tr>
        </thead>

        <tbody>
          {incidents.map(i => (
            <tr key={i.id}>
              <td>{i.id}</td>
              <td>{i.component_id}</td>
              <td>{i.message}</td>
              <td style={{
                color: i.status === "OPEN" ? "red" : "green"
              }}>
                {i.status}
              </td>
              <td>{i.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
