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
        background: "linear-gradient(to bottom right, #6a11cb, #2575fc)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
        fontFamily: "'Roboto', sans-serif",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Decorative background */}
      <div
        style={{
          position: "absolute",
          top: "-50px",
          left: "-100px",
          width: "300px",
          height: "300px",
          background: "rgba(255, 255, 255, 0.2)",
          borderRadius: "50%",
          filter: "blur(100px)",
        }}
      ></div>
      <div
        style={{
          position: "absolute",
          bottom: "-100px",
          right: "-50px",
          width: "400px",
          height: "400px",
          background: "rgba(255, 255, 255, 0.2)",
          borderRadius: "50%",
          filter: "blur(150px)",
        }}
      ></div>
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "900px",
          height: "900px",
          background: "radial-gradient(circle, rgba(255,255,255,0.1), transparent)",
          borderRadius: "50%",
          filter: "blur(150px)",
        }}
      ></div>

      {/* Image at the top */}
      <img
        src="/logo.png" // Path relative to the public folder
        alt="Global Tech Colab Logo"
        style={{
          width: "200px",
          height: "200px",
          marginBottom: "1rem",
          borderRadius: "50%", // Makes the image circular
          boxShadow: "0 4px 6px rgba(0,0,0,0.2)", // Optional shadow for effect
        }}
      />

      <div
        style={{
          zIndex: 1,
          maxWidth: "1200px",
          width: "100%",
          textAlign: "center",
          padding: "3rem",
          background: "#fff",
          borderRadius: "15px",
          boxShadow: "0 6px 12px rgba(0,0,0,0.3)",
        }}
      >
        <h1
          style={{
            color: "#6a11cb",
            fontWeight: "bold",
            fontSize: "2.8rem",
            background: "linear-gradient(to right, #ff6f91, #ff9671)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            animation: "glow 2s infinite alternate",
            textShadow: "0px 4px 6px rgba(0,0,0,0.2)",
            marginBottom: "1rem",
          }}
        >
          Global Tech Colab For Good
        </h1>
        <p
          style={{
            color: "#444",
            fontSize: "1.4rem",
            marginTop: "0.5rem",
            letterSpacing: "0.5px",
            lineHeight: "1.5",
            whiteSpace: "normal",
          }}
        >
          Enter a problem statement to find relevant tech research papers and get an explanation!
        </p>
      </div>
      <div
        style={{
          zIndex: 1,
          marginTop: "2rem",
          width: "100%",
          maxWidth: "600px",
        }}
      >
        <QueryForm onResponse={handleApiResponse} />
      </div>
      {response && (
        <div
          style={{
            zIndex: 1,
            marginTop: "2rem",
            width: "100%",
            maxWidth: "600px",
          }}
        >
          <ResultDisplay response={response} />
        </div>
      )}
    </div>
  );
};

export default App;
