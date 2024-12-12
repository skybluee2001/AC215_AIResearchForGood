export const fetchQueryResults = async (query) => {
    const API_URL = "http://localhost:9000/api/perform_rag";
  
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });
  
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
  
    return response.json();
  };
  