#!/bin/bash

# Run container 1
docker build -t retrieve_papers .
docker run --name container1 retrieve_papers
docker wait container1  # Wait for container1 to finish

# Run container 2
docker build -t embed_papers .
docker run --name container2 embed_papers
docker wait container2  # Wait for container2 to finish

# Run container 3
docker build -t rag .
docker run --name container3 rag
docker wait container3  # Wait for container3 to finish

echo "All containers have finished running."
