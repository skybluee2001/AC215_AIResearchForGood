import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from google.cloud import storage
from google.cloud import aiplatform

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/content/ai-research-for-good-b6f4173936f9.json"

bucket_name = 'paper-rec-bucket'
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

destination_folder = 'paper_vector_db'
model_name = "sentence-transformers/all-MiniLM-L6-v2"
hf = HuggingFaceEmbeddings(model_name=model_name)

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)
folder_prefix = 'paper_vector_db/'

blobs = bucket.list_blobs(prefix='paper_vector_db/')

for blob in blobs:
    relative_path = os.path.relpath(blob.name, folder_prefix)

    local_path = os.path.join(destination_folder, relative_path)

    local_folder = os.path.dirname(local_path)
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    blob.download_to_filename(local_path)
    print(f"Downloaded {blob.name} to {local_path}")
    
persist_directory = "paper_vector_db/"

db = Chroma(
    collection_name="example_collection",
    embedding_function=hf,  
    persist_directory=persist_directory
)

results = db.similarity_search(
    "AI for homelessness",
    k=5
)

for result in results: 
    source = result.metadata['source']
    page_content = result.page_content
    prompt = ""
    prompt += f"Source: {source}\n"
    prompt += f"Page Content: {page_content}\n"
    prompt += f"Similarity: {result.similarity}\n"


PROJECT_ID = "ai-research-for-good"
LOCATION = "us-central1"        
MODEL_ID = "gemini-1.5-pro"

aiplatform.init(project=PROJECT_ID, location=LOCATION)

def generate_answer_google(query):

    prompt += f"For the query '{query}, please generate an explanation for the relevance of the above papers to the query."
    model = aiplatform.Model(MODEL_ID)
    response = model.predict([prompt], temperature=0.7)

    return response.predictions[0] 

query = "AI for homelessness"
answer = generate_answer_google(query)
print(answer)
