import os
from typing import List, Dict
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import logging
import json
logger = logging.getLogger(__name__)

def download_files_from_bucket(bucket_name: str, folder_prefix: str, destination_folder: str):
    """
    Downloads files from a specified Google Cloud Storage bucket to a local destination folder.
    Args:
        bucket_name (str): The name of the GCS bucket.
        folder_prefix (str): The folder prefix in the bucket to download files from.
        destination_folder (str): The local folder to save the downloaded files.
    """
    logger.info(f"Starting download from bucket: {bucket_name}, prefix: {folder_prefix}")
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

def retrieve_metadata(source, metadata_file="metadata/arxiv_social_impact_papers.json"):
    """Retrieve metadata (title, summary, authors) for a paper from the metadata JSON file."""
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    for paper in metadata:
        id = source.strip('.txt').strip('/tmp/')
        if id in paper["paper_id"]:
            return paper["title"], paper["summary"], paper["authors"], paper["paper_id"]
    return None, None, None,None

def retrieve_documents(query, persist_directory, model_name, metadata_file="metadata/arxiv_social_impact_papers.json"):
    logger.info(f"Retrieving documents for query: {query}")
    hf = HuggingFaceEmbeddings(model_name=model_name)
    logger.debug(f"Using model: {model_name} with persist directory: {persist_directory}")
    db = Chroma(
        collection_name="all_manuscripts",
        embedding_function=hf,
        persist_directory=persist_directory
    )

    results = db.similarity_search(query, k=10)
    logger.info(f"Retrieved {len(results)} results from ChromaDB")

    documents = []
    for result in results:
        source = result.metadata['source']
        page_content = result.page_content

        # Retrieve metadata
        title, summary, authors, url = retrieve_metadata(source, metadata_file)
        if title and summary:
            prompt = {
                "title": title,
                "summary": summary,
                "authors": authors,
                "page_content": page_content,
                "url": url
            }
            documents.append(prompt)

    return documents

def rank_and_filter_documents(query, documents, model):
    """
    Rank and filter documents using the fine-tuned model.
    """
    # Use the fine-tuned model's ranking function
    filtered_docs = []
    print("Query:", query)
    print("Number of documents:", len(documents))
    print("Model:", model)
    
    for doc in documents:
        Input = f"""You are an expert data annotator who works on a project to connect non-profit users to technological research papers that might be relevant to the non-profit's use case.\n\n
                                    Please rate the following research paper for its relevance to the non-profit's user query. Output \"Relevant\" if the paper relevant, or \"Irrelevant\" if the paper is not relevant.\n\n
        User query: {query}

        Paper title: {doc['title']}
        Paper summary: {doc['summary']}
        """

        response = model.generate_content(Input)
        generated_text = response.text
        if "relevant" in generated_text.lower():
            filtered_docs.append(doc)

    return filtered_docs

def generate_answer(documents, query, project_id, location, model_id):
    """
    Generate an answer with structured output combining title, summary, authors, page content, and URL.
    """
    # structured_docs = "\n\n".join(
    #     f"""Title: {doc['title']}
    #     Summary: {doc['summary']}
    #     Authors: {', '.join(doc['authors']) if doc['authors'] else 'Unknown'}
    #     Relevant Chunk: {doc['page_content']}
    #     Paper URL: {doc['url']}
    #             """
    #     for doc in documents
    # )
    structured_docs = [ { "title": doc['title'], "summary": doc['summary'], "authors": ', '.join(doc['authors']) if doc['authors'] else 'Unknown', "page_content": doc['page_content'], "url": doc['url'] } for doc in documents ]

    prompt = f"""\nYou are a helpful assistant working for Global Tech Colab For Good, an organization that helps connect non-profit organizations to relevant technical research papers.
            The following is a query from the non-profit:
            {query}
            We have retrieved the following papers that are relevant to this non-profit's request query.
            {structured_docs}
            Your job is to provide in a digestible manner the title of the paper(s), their summaries, their URLs, and how the papers can be used by the non-profit to help with their query.
            Ensure your answer is structured, clear, and user-friendly, and include the Paper URL in your response for each paper.
            """

    vertexai.init(project=project_id, location=location)
    model = GenerativeModel(model_id)

    response = model.generate_content(prompt)
    print(response.text)
    return prompt, response.text


def download_single_file_from_bucket(bucket_name, file_path, destination_folder):
    """
    Download a single file from a Google Cloud Storage bucket.
    """
    os.makedirs(destination_folder, exist_ok=True)
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    blob = bucket.blob(file_path)
    
    local_file_path = os.path.join(destination_folder, os.path.basename(file_path))
    
    try:
        # Debug
        blob.download_to_filename(local_file_path)
        print(f"Successfully downloaded {file_path} to {local_file_path}")
        return local_file_path
    except Exception as e:
        print(f"Error downloading file {file_path}: {e}")
        return None
