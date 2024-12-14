import React, { useState } from "react";
import { fetchQueryResults } from "../api";

const QueryForm = ({ onResponse }) => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetchQueryResults(query);
      onResponse(response);
    } catch (err) {
      setError("Failed to fetch data from the server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="e.g., homelessness, healthcare..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          required
          style={{
            width: "100%",
            padding: "0.8rem",
            border: "1px solid #ccc",
            borderRadius: "5px",
            fontSize: "1rem",
          }}
        />
      </div>
      <button
        type="submit"
        style={{
          width: "100%",
          padding: "0.8rem",
          background: "#1565c0",
          color: "#fff",
          border: "none",
          borderRadius: "5px",
          fontSize: "1rem",
          cursor: "pointer",
          transition: "background 0.3s ease",
        }}
        onMouseOver={(e) => (e.target.style.background = "#004ba0")}
        onMouseOut={(e) => (e.target.style.background = "#1565c0")}
        disabled={loading}
      >
        {loading ? "Fetching..." : "Submit"}
      </button>
      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
    </form>
  );
};

export default QueryForm;
