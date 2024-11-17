import os
import pytest
from unittest.mock import Mock, patch
from google.cloud import storage
import shutil
from embed_papers.embed_papers import (
    set_up_gcs,
    set_up_model,
    upload_to_gcs,
    download_from_gcs,
    delete_from_gcs,
)


@pytest.fixture
def mock_storage_client():
    client = Mock(spec=storage.Client)
    bucket = Mock(spec=storage.Bucket)
    blob = Mock(spec=storage.Blob)

    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    bucket.list_blobs.return_value = []

    return client, bucket, blob


@pytest.fixture
def mock_chroma():
    with patch("embed_papers.embed_papers.Chroma") as mock_chroma:
        mock_db = Mock()
        mock_chroma.return_value = mock_db
        yield mock_db


@pytest.fixture
def mock_embeddings():
    with patch("embed_papers.embed_papers.HuggingFaceEmbeddings") as mock_embeddings:
        mock_embedding = Mock()
        mock_embeddings.return_value = mock_embedding
        yield mock_embedding


@pytest.fixture
def temp_dir(tmp_path):
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_set_up_gcs():
    with patch("google.cloud.storage.Client") as mock_client:
        mock_bucket = Mock()
        mock_client.return_value.bucket.return_value = mock_bucket

        storage_client, bucket, texts_to_retrieve, texts_done = set_up_gcs(
            "test-bucket"
        )

        assert texts_to_retrieve == "manuscript_texts_to_retrieve"
        assert texts_done == "manuscript_texts_done"
        assert os.path.exists(texts_done)
        assert bucket == mock_bucket


def test_set_up_model():
    with patch("embed_papers.embed_papers.Chroma") as mock_chroma, patch(
        "embed_papers.embed_papers.HuggingFaceEmbeddings"
    ) as mock_embeddings:

        mock_db = Mock()
        mock_chroma.return_value = mock_db

        db, persist_directory = set_up_model()

        assert persist_directory == "paper_vector_db"
        assert db == mock_db
        assert mock_chroma.call_count == 1
        mock_embeddings.assert_called_once_with(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )


def test_upload_to_gcs_file(mock_storage_client, temp_dir):
    client, bucket, blob = mock_storage_client
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")

    upload_to_gcs(client, str(test_file), "test-bucket")

    blob.upload_from_filename.assert_called_once_with(str(test_file))


def test_upload_to_gcs_directory(mock_storage_client, temp_dir):
    client, bucket, blob = mock_storage_client

    # Create test directory structure
    sub_dir = temp_dir / "subdir"
    sub_dir.mkdir()
    test_file1 = temp_dir / "test1.txt"
    test_file2 = sub_dir / "test2.txt"
    test_file1.write_text("test content 1")
    test_file2.write_text("test content 2")

    upload_to_gcs(client, str(temp_dir), "test-bucket")

    assert blob.upload_from_filename.call_count == 2


def test_download_from_gcs(mock_storage_client, temp_dir):
    client, bucket, blob = mock_storage_client
    download_path = str(temp_dir / "downloaded.txt")

    download_from_gcs(client, "test_blob", download_path, "test-bucket")

    blob.download_to_filename.assert_called_once_with(download_path)


def test_delete_from_gcs(mock_storage_client):
    client, bucket, blob = mock_storage_client

    delete_from_gcs(client, "test_file.txt", "test-bucket")

    blob.delete.assert_called_once()


if __name__ == "__main__":
    pytest.main()
