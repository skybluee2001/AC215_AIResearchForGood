# fastapi_service/api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# Add the perform_rag directory to the path to import the perform_rag module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'perform_rag')))
from perform_rag import main as perform_rag_main

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/get_answer")
def get_answer(request: QueryRequest):
    query = request.query
    try:
        answer = perform_rag_main(query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
