import pytest
from unittest.mock import Mock, patch
import os
from retrieve_papers.retrieve_papers import main as retrieve_main
from embed_papers.embed_papers import main as embed_main


@pytest.mark.integration_test
def test_retrieve_and_embed_integration(tmp_path):
    """Test the integration between paper retrieval and embedding"""
    with patch(
        "retrieve_papers.retrieve_papers.urllib.request.urlopen"
    ) as mock_urlopen, patch(
        "retrieve_papers.retrieve_papers.requests.get"
    ) as mock_get, patch(
        "embed_papers.embed_papers.Chroma"
    ) as mock_chroma, patch(
        "google.cloud.storage.Client"
    ) as mock_storage_client:

        # Mock ArXiv API response
        mock_response = Mock()
        mock_response.read.return_value = b"""<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
                <entry>
                    <title>Test Paper</title>
                    <id>http://arxiv.org/abs/2304.12345</id>
                    <summary>Test summary</summary>
                    <author><name>Test Author</name></author>
                    <published>2024-01-01T00:00:00Z</published>
                </entry>
            </feed>"""
        mock_urlopen.return_value = mock_response

        # Mock paper download response
        mock_tar_response = Mock()
        mock_tar_response.status_code = 200
        mock_tar_response.iter_content.return_value = [b"Test paper content"]
        mock_get.return_value = mock_tar_response

        # Mock storage client
        mock_bucket = Mock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = []

        os.makedirs(tmp_path / "manuscript_texts_to_retrieve", exist_ok=True)
        os.makedirs(tmp_path / "manuscript_texts_done", exist_ok=True)

        # Run retrieve papers process
        with patch("os.environ", {"GOOGLE_APPLICATION_CREDENTIALS": "dummy_path"}):
            retrieve_main()

            mock_urlopen.assert_called_once()
            mock_get.assert_called_once()

            embed_main()

            mock_chroma.assert_called_once()

            assert mock_storage_client.call_count >= 1
            assert mock_bucket.blob.call_count >= 1


if __name__ == "__main__":
    pytest.main(["-v"])
