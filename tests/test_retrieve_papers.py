import pytest, os
from unittest.mock import patch, MagicMock
from retrieve_papers.retrieve_papers import (
    fetch_arxiv_papers,
    parse_paper_data,
    save_paper_metadata_to_txt,
    download_tar_file,
    extract_tar_file,
    find_tex_file,
    save_tex_as_text,
)


def test_import():
    """Test importing the module."""
    assert type("retrieve_papers") == str


@patch("retrieve_papers.retrieve_papers.urllib.request.urlopen")
def test_fetch_arxiv_papers(mock_urlopen):
    """Test fetching papers from arXiv."""
    mock_response = MagicMock()
    mock_response.read.return_value = b"<xml>mock_data</xml>"
    mock_urlopen.return_value = mock_response

    xml_data = fetch_arxiv_papers("test_query", max_results=10)
    assert xml_data == "<xml>mock_data</xml>"
    mock_urlopen.assert_called_once_with(
        "http://export.arxiv.org/api/query?search_query=all:test_query&start=0&max_results=10&sortBy=lastUpdatedDate&sortOrder=ascending"
    )


def test_parse_paper_data():
    """Test parsing paper data from XML."""
    xml_data = """
    <feed xmlns="http://www.w3.org/2005/Atom">
        <entry>
            <title>Test Paper</title>
            <summary>Test Summary</summary>
            <id>http://arxiv.org/abs/test_id</id>
            <author><name>Author One</name></author>
            <published>2024-01-01</published>
        </entry>
    </feed>
    """
    papers = parse_paper_data(xml_data)
    assert len(papers) == 1
    assert papers[0]["title"] == "Test Paper"
    assert papers[0]["summary"] == "Test Summary"
    assert papers[0]["paper_id"] == "http://arxiv.org/abs/test_id"
    assert papers[0]["authors"] == ["Author One"]
    assert papers[0]["published_date"] == "2024-01-01"


from unittest.mock import mock_open


@patch("builtins.open", new_callable=mock_open)
def test_save_paper_metadata_to_txt(mock_open):
    papers = [
        {
            "title": "Test Paper",
            "summary": "Test Summary",
            "paper_id": "http://arxiv.org/abs/test_id",
            "authors": ["Author One"],
            "published_date": "2024-01-01",
        }
    ]
    save_paper_metadata_to_txt(papers, "test_file.txt")

    mock_open.assert_called_once_with("test_file.txt", "w")
    mock_open().write.assert_any_call("Title: Test Paper\n")
    mock_open().write.assert_any_call("Summary: Test Summary\n")


@patch("retrieve_papers.retrieve_papers.requests.get")
def test_download_tar_file(mock_get):
    """Test downloading a tar file."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
    mock_get.return_value = mock_response

    result = download_tar_file("http://example.com/test.tar", "test_output.tar")
    assert result == "test_output.tar"
    mock_get.assert_called_once_with("http://example.com/test.tar", stream=True)


@patch("retrieve_papers.retrieve_papers.tarfile.open")
def test_extract_tar_file(mock_tarfile_open):
    """Test extracting a tar file."""
    mock_tar = MagicMock()
    mock_tarfile_open.return_value = mock_tar
    mock_tarfile_open.return_value.__enter__.return_value = mock_tar

    result = extract_tar_file("test_input.tar", "test_output")
    assert result == "test_output"
    mock_tar.extractall.assert_called_once_with(path="test_output")


def test_find_tex_file():
    """Test finding a .tex file in a directory."""
    with patch("os.walk") as mock_walk:
        mock_walk.return_value = [
            ("root", ["dir"], ["file1.txt", "file2.tex"]),
        ]
        result = find_tex_file("test_dir")
        assert result == os.path.join("root", "file2.tex")


@patch("builtins.open", new_callable=MagicMock)
def test_save_tex_as_text(mock_open):
    """Test saving a .tex file as a text file."""
    mock_open.return_value.read.return_value = "Test Content"
    result = save_tex_as_text("input.tex", "output.txt")
    assert result is True
    mock_open.assert_any_call("input.tex", "r", encoding="utf-8", errors="ignore")
    mock_open.assert_any_call("output.txt", "w", encoding="utf-8")
