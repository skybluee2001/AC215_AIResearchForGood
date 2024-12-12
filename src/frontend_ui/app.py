import streamlit as st
import requests

# Streamlit UI
st.title("Global Tech Colab For Good: A Platform for Non-Profits and Research Groups")
st.write(
    "Enter a problem statement to find relevant tech research papers and get an explanation!"
)

# FastAPI endpoint URL
API_URL = "http://localhost:9000/api/perform_rag"

# Input for the query
query = st.text_input("Enter your query:")

if st.button("Submit"):
    with st.spinner("Fetching relevant papers and generating explanation..."):
        try:
            st.write("Sending query to backend...")
            response = requests.post(API_URL, json={"query": query})

            if response.status_code == 200:
                st.write("Received response from backend.")
                response_data = response.json()
                st.success("Explanation generated successfully!")
                st.write("### Query")
                st.write(response_data["query"])
                st.write("### Relevant Documents")
                for idx, doc in enumerate(response_data.get("documents", [])):
                    st.write(f"**Document {idx + 1}:** {doc}")
                st.write("### Answer")
                st.write(response_data["answer"])
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.write("Exception details:", e)
