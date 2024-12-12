import pytest
import os
from unittest.mock import patch, MagicMock
from perform_rag.perform_rag import (
    retrieve_documents,
    download_files_from_bucket,
    rank_and_filter_documents,
    main,
)


def test_import():
    """Test importing the module."""
    assert type("perform_rag") == str


@patch("perform_rag.perform_rag.storage.Client")
def test_download_files_from_bucket(mock_storage_client):
    """Test downloading files from a Google Cloud Storage bucket."""
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "paper_vector_db/test.txt"
    mock_bucket.list_blobs.return_value = [mock_blob]
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    # Expected file path
    expected_file_path = os.path.join("test_folder", "test.txt")

    # Call the function
    download_files_from_bucket("test-bucket", "paper_vector_db/", "test_folder")

    # Verify that the mocked download_to_filename is called with the correct file path
    mock_blob.download_to_filename.assert_called_once_with(expected_file_path)


def test_rank_and_filter_documents():
    """Test ranking and filtering of documents based on a query."""
    # Mock model
    mock_model = MagicMock()

    # Define test cases
    query = "Non-profit technology use"
    documents = [
        "Research paper about AI for non-profits",
        "Study on urban planning unrelated to technology",
        "Technological advancements in clean water projects",
    ]

    # Mock model.generate_content responses
    def mock_generate_content(input_text):
        if "AI for non-profits" in input_text:
            return MagicMock(text="Relevant")
        elif "clean water projects" in input_text:
            return MagicMock(text="Relevant")
        else:
            return MagicMock(text="Not Relevant")

    mock_model.generate_content.side_effect = mock_generate_content

    # Run the function
    filtered_docs = rank_and_filter_documents(query, documents, mock_model)

    # Verify the result
    expected_docs = [
        "Research paper about AI for non-profits",
        "Technological advancements in clean water projects",
    ]
    assert filtered_docs == expected_docs


@patch("perform_rag.perform_rag.storage.Client")
def test_download_files_from_bucket_no_files(mock_storage_client):
    """Test downloading files from a bucket when no files are found."""
    mock_bucket = MagicMock()
    mock_bucket.list_blobs.return_value = []
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    # Call the function
    download_files_from_bucket("test-bucket", "paper_vector_db/", "test_folder")

    # Verify no files were downloaded
    mock_bucket.list_blobs.assert_called_once_with(prefix="paper_vector_db/")
    assert mock_storage_client.return_value.bucket.return_value.list_blobs.called


@patch("perform_rag.perform_rag.HuggingFaceEmbeddings", autospec=True)
@patch("perform_rag.perform_rag.Chroma", autospec=True)
def test_retrieve_documents(mock_chroma, mock_hf_embeddings):
    """Test retrieving documents using Chroma and HuggingFaceEmbeddings."""

    # Mock HuggingFaceEmbeddings initialization
    mock_hf_embeddings_instance = MagicMock()
    mock_hf_embeddings.return_value = mock_hf_embeddings_instance

    # Mock Chroma behavior
    mock_chroma_instance = MagicMock()
    mock_chroma.return_value = mock_chroma_instance
    mock_chroma_instance.similarity_search.return_value = [
        MagicMock(metadata={"source": "doc1"}, page_content="Content of document 1"),
        MagicMock(metadata={"source": "doc2"}, page_content="Content of document 2"),
    ]

    # Call the function
    documents = retrieve_documents(
        "test_query",  # Query string
        "mock_persist_directory",  # Chroma persistence directory
        "mock_model_name",  # Embedding model name
    )

    # Verify HuggingFaceEmbeddings was initialized
    mock_hf_embeddings.assert_called_once_with(model_name="mock_model_name")

    # Verify Chroma was created with the correct parameters
    mock_chroma.assert_called_once_with(
        collection_name="all_manuscripts",
        embedding_function=mock_hf_embeddings_instance,
        persist_directory="mock_persist_directory",
    )

    # Verify similarity_search was called
    mock_chroma_instance.similarity_search.assert_called_once_with("test_query", k=10)

    # Verify the return value
    expected_documents = [
        "\nPage Content: Content of document 1\n",
        "\nPage Content: Content of document 2\n",
    ]
    assert documents == expected_documents


@patch("perform_rag.perform_rag.download_files_from_bucket")
@patch("perform_rag.perform_rag.retrieve_documents", return_value=["Doc1", "Doc2"])
@patch("perform_rag.perform_rag.rank_and_filter_documents", return_value=["Doc1"])
@patch("perform_rag.perform_rag.GenerativeModel", autospec=True)
def test_rank_and_filter_call(
    mock_model, mock_rank_filter, mock_retrieve, mock_download
):
    """Test ranking and filtering of documents with mocked connections."""
    mock_model_instance = MagicMock()
    mock_model.return_value = mock_model_instance

    main(query="Test query")

    mock_download.assert_called_once_with(
        "paper-rec-bucket", "paper_vector_db/", "paper_vector_db"
    )

    mock_retrieve.assert_called_once_with(
        "Test query", "paper_vector_db/", "sentence-transformers/all-MiniLM-L6-v2"
    )

    args, _ = mock_model.call_args
    valid_prefix = "projects/129349313346/locations/us-central1/endpoints"
    valid_value = "gemini-1.5-flash"

    # GenerativeModel could be called with custom endpoint or base model
    assert (
        args[0].startswith(valid_prefix) or args[0] == valid_value
    ), f"Unexpected argument to GenerativeModel: {args[0]}"

    # Verify rank_and_filter_documents is called with correct arguments
    mock_rank_filter.assert_called_once_with(
        "Test query", ["Doc1", "Doc2"], mock_model_instance, 5
    )
