from fastapi import FastAPI
from pydantic import BaseModel
from src.perform_rag.perform_rag import main as perform_rag_main

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


@app.post("/generate_explanation/")
async def generate_explanation(request: QueryRequest):
    try:
        query = request.query
        # Call the perform_rag logic here
        explanation = perform_rag_main(query)
        return {"explanation": explanation}
    except Exception as e:
        return {"error": str(e)}
