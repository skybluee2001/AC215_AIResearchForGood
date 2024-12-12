from fastapi import APIRouter, HTTPException
from api.utils.llm_rag_utils import download_files_from_bucket, retrieve_documents, rank_and_filter_documents, generate_answer, download_single_file_from_bucket
import vertexai
from vertexai.generative_models import GenerativeModel
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/perform_rag")
async def perform_rag(request: QueryRequest):
    query = request.query  # Access the query field
    try:
        logger.info(f"Received query: {query}")

        # RAG logic remains the same...
        persist_directory = "paper_vector_db/"
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        project_id = "ai-research-for-good"
        location = "us-central1"
        model_id = "gemini-1.5-flash-002"
        TOP_K = 5


        bucket_name = 'paper-rec-bucket'
        folder_prefix = "paper_vector_db/"
        destination_folder = "paper_vector_db"

        model_endpoint = "projects/ai-research-for-good/locations/us-central1/endpoints/3977180947782041600"
        metadata_file_path = 'metadata/arxiv_social_impact_papers.json'

        download_files_from_bucket(bucket_name, folder_prefix, destination_folder)
        download_single_file_from_bucket(bucket_name, metadata_file_path, 'metadata')
        
        logger.debug("Starting document retrieval")
        documents = retrieve_documents(query, persist_directory, model_name)

        logger.debug("Starting document ranking and filtering")
        fine_tuned_model = GenerativeModel(model_endpoint)
        top_documents = rank_and_filter_documents(query, documents, fine_tuned_model)

        logger.debug("Starting answer generation")
        _, answer = generate_answer(top_documents, query, project_id, location, model_id)

        logger.info("Perform RAG completed successfully")
        return {"query": query, "answer": answer}

    except Exception as e:
        logger.error(f"Error in perform_rag: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

