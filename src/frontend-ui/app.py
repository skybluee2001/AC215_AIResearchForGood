# # import streamlit as st
# # import sys
# # import os

# # # Add the src directory to the path to import perform_rag
# # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'perform_rag')))
# # from perform_rag import main as perform_rag_main

# # # Streamlit UI
# # st.title("Global Tech Colab For Good: A Platform for Non-Profits and Research Groups")
# # st.write("Enter a problem statement to find relevant tech research papers and get an explanation for bonus!")

# # # User query input
# # query = st.text_input("Enter your query:", "")

# # if st.button("Submit"):
# #     with st.spinner("Fetching relevant papers and generating explanation..."):
# #         try:
# #             # Get the answer from the RAG pipeline
# #             answer = perform_rag_main(query)
# #             st.success("Explanation generated successfully!")
# #             st.write(answer)
# #         except Exception as e:
# #             st.error(f"An error occurred: {e}")

# # frontend-ui/app.py

# import streamlit as st
# import requests

# st.title("Global Tech Colab For Good: A Platform for Non-Profits and Research Groups")
# st.write("Enter a problem statement to find relevant tech research papers and get an explanation for bonus!")

# query = st.text_input("Enter your query:", "")

# if st.button("Submit"):
#     with st.spinner("Fetching relevant papers and generating explanation..."):
#         try:
#             response = requests.post("http://localhost:8000/get_answer", json={"query": query})
#             # response = requests.post("http://fastapi-service:8000/get_answer", json={"query": query})
#             response.raise_for_status()
#             answer = response.json().get("answer")
#             st.success("Explanation generated successfully!")
#             st.write(answer)
#         except requests.exceptions.RequestException as e:
#             st.error(f"An error occurred: {e}")

import streamlit as st
import requests

# Streamlit UI
st.title("Global Tech Colab For Good: A Platform for Non-Profits and Research Groups")
st.write(
    "Enter a problem statement to find relevant tech research papers and get an explanation for bonus!"
)

# FastAPI endpoint URL
API_URL = "http://localhost:8000/generate_explanation/"

if st.button("Submit"):
    with st.spinner("Fetching relevant papers and generating explanation..."):
        try:
            # Send the query to the FastAPI backend
            response = requests.post(API_URL, json={"query": query})
            response_data = response.json()
            if "explanation" in response_data:
                st.success("Explanation generated successfully!")
                st.write(response_data["explanation"])
            else:
                st.error(
                    f"An error occurred: {response_data.get('error', 'Unknown error')}"
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")
