import unittest
from unittest.mock import patch, MagicMock, call
from embed_papers.embed_papers import download_from_gcs, set_up_gcs, upload_to_gcs


class TestDownloadFromGCS(unittest.TestCase):
    @patch("embed_papers.embed_papers.storage.Client")
    def test_download_from_gcs(self, mock_storage_client):
        # Create a mock bucket and blob
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        # Call the function
        download_from_gcs(
            mock_storage_client.return_value,
            "test_blob",
            "/test/file.txt",
            "test-bucket",
        )

        # Assertions
        mock_storage_client.return_value.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test_blob")
        mock_blob.download_to_filename.assert_called_once_with("/test/file.txt")


class TestSetUpGCS(unittest.TestCase):
    @patch("embed_papers.embed_papers.storage.Client")
    @patch("os.makedirs")
    def test_set_up_gcs(self, mock_makedirs, mock_storage_client):
        # Mock the bucket
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        # Call the function
        storage_client, bucket, texts_to_retrieve, texts_done = set_up_gcs(
            "test-bucket"
        )

        # Assertions
        mock_storage_client.assert_called_once()
        mock_storage_client.return_value.bucket.assert_called_once_with("test-bucket")
        mock_makedirs.assert_called_once_with("manuscript_texts_done", exist_ok=True)

        self.assertEqual(texts_to_retrieve, "manuscript_texts_to_retrieve")
        self.assertEqual(texts_done, "manuscript_texts_done")


if __name__ == "__main__":
    unittest.main()
