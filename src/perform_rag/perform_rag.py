import os
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


def rank_and_filter_documents(query, documents, model, top_k=5):
    """
    Rank and filter documents using the fine-tuned model.
    """
    # Use the fine-tuned model's ranking function
    list_res = []

    for doc in documents:
        Input = f"""You are an expert data annotator who works on a project to connect non-profit users to technological research papers that might be relevant to the non-profit's use case
        Please rate the following research paper for its relevance to the non-profit's user query. Output "Relevant" if the paper relevant, or "Not Relevant" if the paper is not relevant.

        User query: {query}

        Paper snippet: {doc}
        """

        response = model.generate_content(
            Input,
        )
        generated_text = response.text
        if generated_text.lower() == "not relevant":
            # list_res.append(doc)
            continue
        else:
            list_res.append(doc)

    return list_res


def retrieve_documents(query, persist_directory, model_name):
    hf = HuggingFaceEmbeddings(model_name=model_name)
    db = Chroma(
        collection_name="all_manuscripts",
        embedding_function=hf,
        persist_directory=persist_directory,
    )

    results = db.similarity_search(query, k=10)
    documents = []
    for result in results:
        source = result.metadata["source"]
        page_content = result.page_content
        prompt = f"\nPage Content: {page_content}\n"
        documents.append(prompt)

    return documents


def generate_answer_google(documents, query, project_id, location, model_id):
    documents_combined = "\n\n".join(documents)
    prompt = f"""\nYou are a helpful assistant working for Global Tech Colab For Good, an organization that helps connect non-profit organizations to relevant technical research papers.
            The following is a query from the non-profit:
            {query}
            We have retrieved the following chunks of research papers that are relevant to this non-profit's request query.
            {documents_combined}
            Your job is to provide in a digestible manner the title of the paper(s) retrieved and an explanation for how the paper(s) can be used by the non-profit to help with their query.
            If the title isn't available, make up a relevant title. Even if the papers dont seem useful to the query, do not say that. Try to be as useful to the non-profit and remember that they are the reader of your response."""

    vertexai.init(project=project_id, location="us-central1")

    model = GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)

    print(response.text)
    return response.text


def main(query="How to educate communities on homelessness"):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the credentials file
    credentials_path = os.path.join(
        script_dir, "../../../secrets/ai-research-for-good-bdf580df11b3.json"
    )

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    bucket_name = "paper-rec-bucket"
    destination_folder = "paper_vector_db"
    folder_prefix = "paper_vector_db/"
    persist_directory = "paper_vector_db/"
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    TOP_K = 5
    MODEL_ENDPOINT = (
        "projects/129349313346/locations/us-central1/endpoints/3319822527953371136"
    )
    PROJECT_ID = "ai-research-for-good"
    LOCATION = "us-central1"
    MODEL_ID = "gemini-1.5-pro"

    # query = "AI for social impact"

    download_files_from_bucket(bucket_name, folder_prefix, destination_folder)
    documents = retrieve_documents(query, persist_directory, model_name)
    model = GenerativeModel(MODEL_ENDPOINT)
    top_documents = rank_and_filter_documents(query, documents, model, TOP_K)

    answer = generate_answer_google(
        top_documents, query, PROJECT_ID, LOCATION, MODEL_ID
    )

    return answer


if __name__ == "__main__":
    main()
