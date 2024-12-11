import React, { useState } from "react";
import QueryForm from "./components/QueryForm";
import ResultDisplay from "./components/ResultDisplay";

const App = () => {
  const [response, setResponse] = useState(null);

  const handleApiResponse = (data) => {
    setResponse(data);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #f9f9f9, #e3f2fd)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
        fontFamily: "'Roboto', sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "600px",
          textAlign: "center",
          padding: "2rem",
          background: "#fff",
          borderRadius: "10px",
          boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
        }}
      >
        <h1 style={{ color: "#1565c0", fontWeight: "bold", marginBottom: "1rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          Global Tech Colab For Good
        </h1>
        <p style={{ color: "#444", marginBottom: "2rem" }}>
          Enter a problem statement to find relevant tech research papers and get an explanation!
        </p>
        <QueryForm onResponse={handleApiResponse} />
        {response && (
          <div style={{ marginTop: "2rem" }}>
            <ResultDisplay response={response} />
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
