import React from "react";

const ResultDisplay = ({ response }) => {
  return (
    <div
      style={{
        padding: "1.5rem",
        background: "#e3f2fd",
        borderRadius: "8px",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        textAlign: "left",
      }}
    >
      <p style={{ fontSize: "1.2rem", lineHeight: "1.8", color: "#333" }}>
        {response.answer}
      </p>
    </div>
  );
};

export default ResultDisplay;
