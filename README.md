**Group Name:** AI Research For Good 

**Project:** Build a global platform that links AI research groups with organizations aiming to solve social issues using AI. The platform will have a search interface for organizations to look for AI research papers relevant to their social cause. A dashboard will provide a curated list of relevant research to the user prompt, the research groups, and how the research work relates to the user’s problem prompt. The platform will be designed to support a growing number of research groups and global organizations. We process a large corpus of AI research papers & social issue descriptions and train LLMs for information retrieval and matching between research and real-world problems.

The User Interface is as shown:

<img src="references/UI.jpeg"  width="800">


The Pipeline Flow is as shown:

<img src="references/Flowchart.jpeg"  width="800">

## Data Pipeline Overview

**Container 1: Retrieve Papers**

Query ArXiv API for papers on “social impact” and fetch metadata for the top 30 results and saves all the manuscript .txt files to the Google cloud bucket. 

```
cd retrieve_papers
pipenv lock
docker build -t retrieve_papers .
docker run --rm -ti -v "$(pwd)":/app retrieve_papers
python retrieve_papers.py
```

**Container 2: Embedding Papers**

Process the manuscripts, perform chunking, embed each chunk and store the embeddings in a ChromaDB vector database

```
cd embed_papers
pipenv lock
docker build -t embed_papers .
docker run --rm -ti -v "$(pwd)":/app embed_papers
python embed_papers.py
```

**Container 3: RAG**

Manages the retrieval of relevant research papers and generates responses for user queries using Gemini MiniLM

```
cd perform_rag
pipenv lock
docker build -t perform_rag .
docker run --rm -ti -v "$(pwd)":/app perform_rag
python perform_rag.py
```
