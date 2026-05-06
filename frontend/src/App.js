import React, { useEffect, useState } from "react";

function App() {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);

  const [rca, setRca] = useState({
    root_cause: "",
    fix: "",
    prevention: "",
    start_time: "",
    end_time: ""
  });

  const [rcaSubmitted, setRcaSubmitted] = useState(false);

  // 🔄 Fetch data
  const fetchData = () => {
    fetch("/api/incidents")
      .then(res => res.json())
      .then(data => setIncidents(data))
      .catch(err => console.error("Error:", err));
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // 📩 Submit RCA
  const submitRCA = () => {
    fetch(`/api/incidents/${selectedIncident.id}/rca`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(rca)
    })
      .then(res => res.json())
      .then(() => {
        alert("RCA saved ✅");
        setRcaSubmitted(true);
      })
      .catch(err => console.error(err));
  };

  // 🔒 Close Incident
  const closeIncident = () => {
    fetch(`/api/incidents/${selectedIncident.id}/status`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ status: "CLOSED" })
    })
      .then(res => res.json())
      .then(res => {
        if (res.detail || res.error) {
          alert(res.detail || res.error);
        } else {
          alert("Incident Closed ✅");

          // 🔥 Reset everything
          setSelectedIncident(null);
          setRcaSubmitted(false);
          setRca({
            root_cause: "",
            fix: "",
            prevention: "",
            start_time: "",
            end_time: ""
          });

          fetchData();
        }
      })
      .catch(err => console.error(err));
  };

  const active = incidents.filter(i => i.status === "OPEN");
  const resolved = incidents.filter(i => i.status !== "OPEN");

  return (
    <div style={{ padding: "20px" }}>
      <h1>🚨 Incident Dashboard</h1>

      {/* 🔴 ACTIVE INCIDENTS */}
      <h2 style={{ color: "red" }}>🔴 Active Incidents</h2>
      <table border="1" cellPadding="10" width="100%">
        <thead>
          <tr>
            <th>ID</th>
            <th>Component</th>
            <th>Message</th>
            <th>Status</th>
            <th>Time</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {active.map(i => (
            <tr key={i.id}>
              <td>{i.id}</td>
              <td>{i.component_id}</td>
              <td>{i.message}</td>
              <td style={{ color: "red" }}>{i.status}</td>
              <td>{i.created_at}</td>
              <td>
                <button
                  onClick={() => {
                    setSelectedIncident(i);
                    setRcaSubmitted(false);
                    setRca({
                      root_cause: "",
                      fix: "",
                      prevention: "",
                      start_time: "",
                      end_time: ""
                    });
                  }}
                >
                  Add RCA
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* 🟢 RESOLVED INCIDENTS */}
      <h2 style={{ color: "green", marginTop: "30px" }}>
        🟢 Resolved Incidents
      </h2>
      <table border="1" cellPadding="10" width="100%">
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
          {resolved.map(i => (
            <tr key={i.id}>
              <td>{i.id}</td>
              <td>{i.component_id}</td>
              <td>{i.message}</td>
              <td style={{ color: "green" }}>{i.status}</td>
              <td>{i.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* 📄 RCA FORM */}
      {selectedIncident && (
        <div
          style={{
            marginTop: "30px",
            border: "1px solid black",
            padding: "20px"
          }}
        >
          <h3>RCA for Incident {selectedIncident.id}</h3>

          <input
            placeholder="Root Cause"
            value={rca.root_cause}
            onChange={e =>
              setRca({ ...rca, root_cause: e.target.value })
            }
          />
          <br />

          <input
            placeholder="Fix"
            value={rca.fix}
            onChange={e =>
              setRca({ ...rca, fix: e.target.value })
            }
          />
          <br />

          <input
            placeholder="Prevention"
            value={rca.prevention}
            onChange={e =>
              setRca({ ...rca, prevention: e.target.value })
            }
          />
          <br />

          <input
            type="datetime-local"
            onChange={e =>
              setRca({ ...rca, start_time: e.target.value })
            }
          />
          <br />

          <input
            type="datetime-local"
            onChange={e =>
              setRca({ ...rca, end_time: e.target.value })
            }
          />
          <br /><br />

          <button onClick={submitRCA}>Submit RCA</button>

          <button
            onClick={closeIncident}
            disabled={!rcaSubmitted}
            style={{ marginLeft: "10px" }}
          >
            Close Incident
          </button>

          <br /><br />

          <button onClick={() => setSelectedIncident(null)}>
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
