import pytest
import os
from unittest.mock import patch, MagicMock
from perform_rag.perform_rag import retrieve_documents, download_files_from_bucket
from langchain_community.document_loaders import TextLoader


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
    mock_chroma_instance.similarity_search.assert_called_once_with("test_query", k=5)

    # Verify the return value
    expected_documents = [
        "\nPage Content: Content of document 1\n",
        "\nPage Content: Content of document 2\n",
    ]
    assert documents == expected_documents
