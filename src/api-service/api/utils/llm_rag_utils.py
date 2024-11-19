# import os
# from typing import Dict, Any, List, Optional
# from fastapi import HTTPException
# import base64
# import io
# from PIL import Image
# from pathlib import Path
# import traceback
# import chromadb
# from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
# from vertexai.generative_models import GenerativeModel, ChatSession, Part

# # Setup
# GCP_PROJECT = os.environ["GCP_PROJECT"]
# GCP_LOCATION = "us-central1"
# EMBEDDING_MODEL = "text-embedding-004"
# EMBEDDING_DIMENSION = 256
# GENERATIVE_MODEL = "gemini-1.5-flash-002"
# CHROMADB_HOST = os.environ["CHROMADB_HOST"]
# CHROMADB_PORT = os.environ["CHROMADB_PORT"]

# # Configuration settings for the content generation
# generation_config = {
#     "max_output_tokens": 3000,  # Maximum number of tokens for output
#     "temperature": 0.1,  # Control randomness in output
#     "top_p": 0.95,  # Use nucleus sampling
# }

# # Initialize the GenerativeModel with specific system instructions
# SYSTEM_INSTRUCTION = """
# You are an AI assistant specialized in cheese knowledge. Your responses are based solely on the information provided in the text chunks given to you. Do not use any external knowledge or make assumptions beyond what is explicitly stated in these chunks.

# When answering a query:
# 1. Carefully read all the text chunks provided.
# 2. Identify the most relevant information from these chunks to address the user's question.
# 3. Formulate your response using only the information found in the given chunks.
# 4. If the provided chunks do not contain sufficient information to answer the query, state that you don't have enough information to provide a complete answer.
# 5. Always maintain a professional and knowledgeable tone, befitting a cheese expert.
# 6. If there are contradictions in the provided chunks, mention this in your response and explain the different viewpoints presented.

# Remember:
# - You are an expert in cheese, but your knowledge is limited to the information in the provided chunks.
# - Do not invent information or draw from knowledge outside of the given text chunks.
# - If asked about topics unrelated to cheese, politely redirect the conversation back to cheese-related subjects.
# - Be concise in your responses while ensuring you cover all relevant information from the chunks.

# Your goal is to provide accurate, helpful information about cheese based solely on the content of the text chunks you receive with each query.
# """
# generative_model = GenerativeModel(
# 	GENERATIVE_MODEL,
# 	system_instruction=[SYSTEM_INSTRUCTION]
# )
# # https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#python
# embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

# # Initialize chat sessions
# chat_sessions: Dict[str, ChatSession] = {}

# # Connect to chroma DB
# client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
# method = "recursive-split"
# collection_name = f"{method}-collection"
# # Get the collection
# collection = client.get_collection(name=collection_name)

# def generate_query_embedding(query):
# 	query_embedding_inputs = [TextEmbeddingInput(task_type='RETRIEVAL_DOCUMENT', text=query)]
# 	kwargs = dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
# 	embeddings = embedding_model.get_embeddings(query_embedding_inputs, **kwargs)
# 	return embeddings[0].values

# def create_chat_session() -> ChatSession:
#     """Create a new chat session with the model"""
#     return generative_model.start_chat()

# def generate_chat_response(chat_session: ChatSession, message: Dict) -> str:
#     """
#     Generate a response using the chat session to maintain history.
#     Handles both text and image inputs.

#     Args:
#         chat_session: The Vertex AI chat session
#         message: Dict containing 'content' (text) and optionally 'image' (base64 string)

#     Returns:
#         str: The model's response
#     """
#     try:
#         # Initialize parts list for the message
#         message_parts = []


#         # Process image if present
#         if message.get("image"):
#             try:
#                 # Extract the actual base64 data and mime type
#                 base64_string = message.get("image")
#                 if ',' in base64_string:
#                     header, base64_data = base64_string.split(',', 1)
#                     mime_type = header.split(':')[1].split(';')[0]
#                 else:
#                     base64_data = base64_string
#                     mime_type = 'image/jpeg'  # default to JPEG if no header

#                 # Decode base64 to bytes
#                 image_bytes = base64.b64decode(base64_data)

#                 # Create an image Part using FileData
#                 image_part = Part.from_data(image_bytes, mime_type=mime_type)
#                 message_parts.append(image_part)

#                 # Add text content if present
#                 if message.get("content"):
#                     message_parts.append(message["content"])
#                 else:
#                     message_parts.append("Name the cheese in the image, no descriptions needed")

#             except ValueError as e:
#                 print(f"Error processing image: {str(e)}")
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"Image processing failed: {str(e)}"
#                 )
#         elif message.get("image_path"):
#             # Read the image file
#             image_path = os.path.join("chat-history","llm-rag",message.get("image_path"))
#             with Path(image_path).open('rb') as f:
#                 image_bytes = f.read()

#             # Determine MIME type based on file extension
#             mime_type = {
#                 '.jpg': 'image/jpeg',
#                 '.jpeg': 'image/jpeg',
#                 '.png': 'image/png',
#                 '.gif': 'image/gif'
#             }.get(Path(image_path).suffix.lower(), 'image/jpeg')

#             # Create an image Part using FileData
#             image_part = Part.from_data(image_bytes, mime_type=mime_type)
#             message_parts.append(image_part)

#             # Add text content if present
#             if message.get("content"):
#                 message_parts.append(message["content"])
#             else:
#                 message_parts.append("Name the cheese in the image, no descriptions needed")
#         else:
#             # Add text content if present
#             if message.get("content"):
#                 # Create embeddings for the message content
#                 query_embedding = generate_query_embedding(message["content"])
#                 # Retrieve chunks based on embedding value
#                 results = collection.query(
#                     query_embeddings=[query_embedding],
#                     n_results=5
#                 )
#                 INPUT_PROMPT = f"""
#                 {message["content"]}
#                 {"\n".join(results["documents"][0])}
#                 """
#                 message_parts.append(INPUT_PROMPT)


#         if not message_parts:
#             raise ValueError("Message must contain either text content or image")

#         # Send message with all parts to the model
#         response = chat_session.send_message(
#             message_parts,
#             generation_config=generation_config
#         )

#         return response.text

#     except Exception as e:
#         print(f"Error generating response: {str(e)}")
#         traceback.print_exc()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to generate response: {str(e)}"
#         )

# def rebuild_chat_session(chat_history: List[Dict]) -> ChatSession:
#     """Rebuild a chat session with complete context"""
#     new_session = create_chat_session()

#     for message in chat_history:
#         if message["role"] == "user":
#             generate_chat_response(new_session, message)

#     return new_session

import os
from typing import List, Dict
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)


def download_files_from_bucket(
    bucket_name: str, folder_prefix: str, destination_folder: str
):
    """
    Downloads files from a specified Google Cloud Storage bucket to a local destination folder.
    Args:
        bucket_name (str): The name of the GCS bucket.
        folder_prefix (str): The folder prefix in the bucket to download files from.
        destination_folder (str): The local folder to save the downloaded files.
    """
    logger.info(
        f"Starting download from bucket: {bucket_name}, prefix: {folder_prefix}"
    )
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        logger.info(f"Created destination folder: {destination_folder}")

    blobs = bucket.list_blobs(prefix=folder_prefix)
    for blob in blobs:
        relative_path = os.path.relpath(blob.name, folder_prefix)
        local_path = os.path.join(destination_folder, relative_path)
        local_folder = os.path.dirname(local_path)
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)
            logger.debug(f"Created local folder: {local_folder}")
        logger.info(f"Downloading: {blob.name} -> {local_path}")
        blob.download_to_filename(local_path)
        print(f"Downloaded {blob.name} to {local_path}")
        logger.debug(f"Downloaded {blob.name} to {local_path}")

    logger.info("All files downloaded successfully.")


def retrieve_documents(
    query: str, persist_directory: str, model_name: str
) -> List[str]:
    """
    Retrieves relevant documents from a Chroma database using similarity search.
    Args:
        query (str): The query string to search for.
        persist_directory (str): The directory where Chroma persists its database.
        model_name (str): The HuggingFace model used for embedding.
    Returns:
        List[str]: A list of relevant document snippets.
    """
    logger.info(f"Retrieving documents for query: {query}")
    hf = HuggingFaceEmbeddings(model_name=model_name)
    logger.debug(
        f"Using model: {model_name} with persist directory: {persist_directory}"
    )
    db = Chroma(
        collection_name="all_manuscripts",
        embedding_function=hf,
        persist_directory=persist_directory,
    )

    results = db.similarity_search(query, k=10)
    logger.info(f"Retrieved {len(results)} results from ChromaDB")
    documents = []
    for result in results:
        source = result.metadata.get("source", "Unknown Source")
        page_content = result.page_content
        snippet = f"Source: {source}\nContent: {page_content}"
        documents.append(snippet)

    return documents


# def rank_and_filter_documents(query: str, documents: List[str], model: GenerativeModel, top_k: int = 5) -> List[str]:
#     """
#     Ranks and filters documents using a fine-tuned generative model.
#     Args:
#         query (str): The query string for ranking.
#         documents (List[str]): A list of document snippets to evaluate.
#         model (GenerativeModel): A Vertex AI generative model for ranking.
#         top_k (int): The number of top documents to retain.
#     Returns:
#         List[str]: A list of top-ranked document snippets.
#     """
#     ranked_documents = []

#     logger.info(f"Ranking and filtering {len(documents)} documents for query: {query}")
#     # for doc in documents:
#     for idx, doc in enumerate(documents):
#         logger.debug(f"Document {idx + 1}: {doc[:200]}")  # Log first 200 characters of each document
#         input_prompt = f"""
#         You are an expert data annotator tasked with connecting non-profits to relevant research papers.
#         Please evaluate the following paper snippet for its relevance to the query.

#         User query: {query}

#         Paper snippet: {doc}

#         Output "Relevant" if the paper is relevant, or "Not Relevant" if it is not.
#         """
#         response = model.generate_content(input_prompt)
#         generated_text = response.text.strip().lower()
#         if generated_text == "relevant":
#             ranked_documents.append(doc)

#     return ranked_documents[:top_k]


def rank_and_filter_documents(query, documents, model, top_k=5):
    # This function ranks and filters documents using the fine-tuned model.
    list_res = []

    for doc in documents:
        input_text = f"""You are an expert data annotator who works on a project to connect non-profit users to technological research papers that might be relevant to the non-profit's use case
        Please rate the following research paper for its relevance to the non-profit's user query. Output "Relevant" if the paper relevant, or "Not Relevant" if the paper is not relevant.

        User query: {query}

        Paper snippet: {doc}
        """

        print("Query:", query)
        print("Number of documents:", len(documents))
        print("Top K:", top_k)
        print("Model:", model)

        model = GenerativeModel(
            "projects/ai-research-for-good/locations/us-central1/endpoints/8528956776635170816"
        )
        response = model.generate_content(
            [input_text],
        )
        generated_text = response.text.strip()  # Strip whitespace from response

        if generated_text.lower() == "relevant":
            print("added")
            list_res.append(doc)

        return list_res


def generate_answer(
    documents: List[str], query: str, project_id: str, location: str, model_id: str
) -> str:
    """
    Generates a consolidated response using a generative model on Google Vertex AI.
    Args:
        documents (List[str]): A list of top-ranked document snippets.
        query (str): The user query.
        project_id (str): Google Cloud project ID.
        location (str): Google Cloud location.
        model_id (str): ID of the Vertex AI generative model.
    Returns:
        str: The generated response.
    """
    logger.info(
        f"Generating answer for query: {query} using {len(documents)} documents"
    )
    documents_combined = "\n\n".join(documents)
    logger.debug(
        f"Combined documents:\n{documents_combined[:500]}"
    )  # Log the first 500 characters
    prompt = f"""
    You are a helpful assistant for Global Tech Colab For Good, connecting non-profits with relevant research papers.

    Query: {query}

    Here are some relevant research paper snippets:
    {documents_combined}

    Please provide a summary of the papers and explain how they can help address the query.
    If the title of a paper is unavailable, make up a relevant title.
    """

    vertexai.init(project=project_id, location=location)
    model = GenerativeModel(model_id)

    response = model.generate_content(prompt)
    return response.text
