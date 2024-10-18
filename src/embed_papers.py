import os
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from google.cloud import storage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/content/ai-research-for-good-b6f4173936f9.json"

# Google Cloud setup
bucket_name = 'paper-rec-bucket'
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# Directory setup
texts_to_retrieve = 'manuscript_texts_to_retrieve'
texts_done = 'manuscript_texts_done'
os.makedirs(texts_done, exist_ok=True)

# Initialize the HuggingFace embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
hf = HuggingFaceEmbeddings(model_name=model_name)

# Initialize the vector store
persist_directory = "paper_vector_db"
db = Chroma(
    collection_name="example_collection",
    embedding_function=hf,  # HuggingFace embeddings initialized earlier
    persist_directory=persist_directory  # Where to save data locally
)

def upload_to_gcs(local_path, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    if os.path.isdir(local_path):
        # If it's a directory, upload all contents
        for root, dirs, files in os.walk(local_path):
            for file in files:
                file_path = os.path.join(root, file)
                blob = bucket.blob(file_path)
                blob.upload_from_filename(file_path)
                print(f"Uploaded {file_path} to {bucket_name}")
    else:
        blob = bucket.blob(local_path)
        blob.upload_from_filename(local_path)
        print(f"Uploaded {local_path} to {bucket_name}")

def download_from_gcs(blob_name, download_path, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(download_path)
    print(f"Downloaded {blob_name} from {bucket_name} to {download_path}")

def delete_from_gcs(file_path, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.delete()
    print(f"Deleted {file_path} from Google Cloud Storage")

blobs = bucket.list_blobs(prefix='manuscripts_texts_to_retrieve/')
for blob in blobs:
    if blob.name.endswith(".txt"):
        local_file_path = os.path.join('/tmp', os.path.basename(blob.name))  

        download_from_gcs(blob.name, local_file_path, bucket_name)

        raw_documents = TextLoader(local_file_path).load()

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        documents = text_splitter.split_documents(raw_documents)

        db.add_documents(documents)

        new_blob_name = blob.name.replace('manuscripts_texts_to_retrieve', 'manuscripts_texts_done')
        bucket.blob(new_blob_name).upload_from_filename(local_file_path)
        print(f"Moved {blob.name} to {new_blob_name} in the cloud")

        delete_from_gcs(blob.name, bucket_name)

        os.remove(local_file_path)
        print(f"Deleted local temp file {local_file_path}")

upload_to_gcs(persist_directory, bucket_name)

upload_to_gcs(texts_done, bucket_name)  # Upload embedded files

print("All manuscripts have been embedded and uploaded to the cloud.")