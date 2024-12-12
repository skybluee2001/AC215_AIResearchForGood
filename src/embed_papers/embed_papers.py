import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from google.cloud import storage

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the credentials file
credentials_path = os.path.join(
    script_dir, "../../../secrets/ai-research-for-good-bdf580df11b3.json"
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../secrets/ai-research-for-good-b6f4173936f9.json"


def set_up_gcs(bucket_name):
    """Set up the Google Cloud Storage client."""
    # Google Cloud setup
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    texts_to_retrieve = "manuscript_texts_to_retrieve"
    texts_done = "manuscript_texts_done"
    os.makedirs(texts_done, exist_ok=True)

    return storage_client, bucket, texts_to_retrieve, texts_done


def set_up_model():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    hf = HuggingFaceEmbeddings(model_name=model_name)

    persist_directory = "paper_vector_db"

    db = Chroma(
        collection_name="all_manuscripts",
        embedding_function=hf,
        persist_directory=persist_directory,
    )

    return db, persist_directory


def upload_to_gcs(storage_client, local_path, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    if os.path.isdir(local_path):
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


def download_from_gcs(storage_client, blob_name, download_path, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(download_path)
    print(f"Downloaded {blob_name} from {bucket_name} to {download_path}")


def delete_from_gcs(storage_client, file_path, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.delete()
    print(f"Deleted {file_path} from Google Cloud Storage")


def main():
    bucket_name = "paper-rec-bucket"
    storage_client, bucket, _, texts_done = set_up_gcs("paper-rec-bucket")
    db, persist_directory = set_up_model()

    blobs = bucket.list_blobs(prefix="manuscript_texts_to_retrieve/")
    for blob in blobs:
        if blob.name.endswith(".txt"):
            local_file_path = os.path.join("/tmp", os.path.basename(blob.name))

            download_from_gcs(storage_client, blob.name, local_file_path, bucket_name)

            raw_documents = TextLoader(local_file_path).load()

            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            documents = text_splitter.split_documents(raw_documents)

            db.add_documents(documents)

            new_blob_name = blob.name.replace(
                "manuscript_texts_to_retrieve", "manuscript_texts_done"
            )
            bucket.blob(new_blob_name).upload_from_filename(local_file_path)
            print(f"Moved {blob.name} to {new_blob_name} in the cloud")

            delete_from_gcs(storage_client, blob.name, bucket_name)

            os.remove(local_file_path)
            print(f"Deleted local temp file {local_file_path}")

    upload_to_gcs(storage_client, persist_directory, bucket_name)

    upload_to_gcs(storage_client, texts_done, bucket_name)  # Upload embedded files

    print("All manuscripts have been embedded and uploaded to the cloud.")


if __name__ == "__main__":
    main()
