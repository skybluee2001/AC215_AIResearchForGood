import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel


def download_files_from_bucket(bucket_name, folder_prefix, destination_folder):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    blobs = bucket.list_blobs(prefix=folder_prefix)
    for blob in blobs:
        relative_path = os.path.relpath(blob.name, folder_prefix)
        local_path = os.path.join(destination_folder, relative_path)
        local_folder = os.path.dirname(local_path)
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)
        blob.download_to_filename(local_path)
        print(f"Downloaded {blob.name} to {local_path}")

def retrieve_documents(query, persist_directory, model_name):
    hf = HuggingFaceEmbeddings(model_name=model_name)
    db = Chroma(
        collection_name="all_manuscripts",
        embedding_function=hf,
        persist_directory=persist_directory
    )

    results = db.similarity_search(query, k=5)
    documents = []
    for result in results:
        source = result.metadata['source']
        page_content = result.page_content
        print(page_content)
        prompt = f"\nPage Content: {page_content}\n"
        documents.append(prompt)

    return documents

def generate_answer_google(documents, query, project_id, location, model_id):
    prompt = "\n\n".join(documents)
    prompt += f"\nFor the query '{query}', please give paper name and summary of the above papers and show how it relates to the query."

    vertexai.init(project=project_id, location="us-central1")

    model = GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
       prompt
    )

    print(response.text)
    return response.text

def main(query):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/ai-research-for-good-b6f4173936f9.json"

    bucket_name = 'paper-rec-bucket'
    destination_folder = 'paper_vector_db'
    folder_prefix = 'paper_vector_db/'
    persist_directory = 'paper_vector_db/'
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    PROJECT_ID = "ai-research-for-good"
    LOCATION = "us-central1"
    MODEL_ID = "gemini-1.5-pro"

    #query = "AI for social impact"

    download_files_from_bucket(bucket_name, folder_prefix, destination_folder)
    documents = retrieve_documents(query, persist_directory, model_name)
    # print(documents)
    answer = generate_answer_google(documents, query, PROJECT_ID, LOCATION, MODEL_ID)

    return answer

if __name__ == "__main__":
    main()
