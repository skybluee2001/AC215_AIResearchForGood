import urllib.request
import xml.etree.ElementTree as ET
import os
from google.cloud import storage
import requests
import tarfile

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../secrets/ai-research-for-good-b6f4173936f9.json"

bucket_name = 'paper-rec-bucket'
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

def fetch_arxiv_papers(search_query, max_results=50):
    base_url = "http://export.arxiv.org/api/query?"
    url = f'{base_url}search_query=all:{search_query}&start=0&max_results={max_results}&sortBy=lastUpdatedDate&sortOrder=ascending'
    data = urllib.request.urlopen(url)
    xml_data = data.read().decode('utf-8')
    return xml_data

def parse_paper_data(xml_data):
    root = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
        paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text
        authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
        published_date = entry.find('{http://www.w3.org/2005/Atom}published').text

        papers.append({
            "title": title,
            "summary": summary,
            "paper_id": paper_id,
            "authors": authors,
            "published_date": published_date
        })
    return papers

def save_paper_metadata_to_txt(papers, file_name):
    with open(file_name, 'w') as file:
        for paper in papers:
            file.write(f"Title: {paper['title']}\n")
            file.write(f"Summary: {paper['summary']}\n")
            file.write(f"Paper ID: {paper['paper_id']}\n")
            file.write(f"Authors: {', '.join(paper['authors'])}\n")
            file.write(f"Published Date: {paper['published_date']}\n")
            file.write("\n")

def upload_to_gcs(file_name, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    print(f"File {file_name} uploaded to {bucket_name}.")

def download_tar_file(url, output_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded .tar file to {output_path}")
            return output_path
        else:
            print(f"Failed to download the file from {url}. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while downloading the file: {e}")
        return None

def extract_tar_file(tar_path, extract_path):
    try:
        if tarfile.is_tarfile(tar_path):
            with tarfile.open(tar_path, 'r') as tar:
                tar.extractall(path=extract_path)
                print(f"Extracted contents to {extract_path}")
                return extract_path
        else:
            print(f"{tar_path} is not a valid tar file.")
            return None
    except Exception as e:
        print(f"An error occurred while extracting the tar file: {e}")
        return None

def find_tex_file(extracted_folder):
    try:
        for root, dirs, files in os.walk(extracted_folder):
            for file in files:
                if file.endswith(".tex"):
                    tex_file_path = os.path.join(root, file)
                    print(f"Found .tex file: {tex_file_path}")
                    return tex_file_path
        print("No .tex file found.")
        return None
    except Exception as e:
        print(f"An error occurred while searching for the .tex file: {e}")
        return None

def save_tex_as_text(tex_file_path, save_path):
    try:
        with open(tex_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved .tex file as {save_path}")
        return True  # Indicating success
    except Exception as e:
        print(f"An error occurred while saving the .tex file as text: {e}")
        return False  # Indicating failure

def process_paper(url, base_extract_path, final_txt_path):
    try:
        paper_id = url.split("/src/")[-1].replace("/", "_")
        paper_folder = os.path.join(base_extract_path, paper_id)
        os.makedirs(paper_folder, exist_ok=True)

        output_tar_path = os.path.join(paper_folder, f"{paper_id}.tar")
        extracted_folder_path = os.path.join(paper_folder, "extracted")

        if not download_tar_file(url, output_tar_path):
            print(f"Skipping {url} due to download error.")
            return None

        os.makedirs(extracted_folder_path, exist_ok=True)
        if not extract_tar_file(output_tar_path, extracted_folder_path):
            print(f"Skipping {url} due to extraction error.")
            return None

        tex_file_path = find_tex_file(extracted_folder_path)
        if tex_file_path:
            save_file_name = paper_id + ".txt"
            final_save_path = os.path.join(final_txt_path, save_file_name)
            if save_tex_as_text(tex_file_path, final_save_path):  # Check if saving was successful
                return final_save_path
            else:
                print(f"Skipping {url} due to file saving error.")
                return None
        else:
            print(f"No .tex file found for {url}")
            return None
    except Exception as e:
        print(f"An error occurred while processing the paper: {e}")
        return None

def main():
    search_query = 'social+AND+impact+OR+"social+impact"'
    max_results = 30
    output_file = "arxiv_social_impact_papers.txt"
    base_extract_path = 'downloads'
    final_txt_path = 'manuscript_texts_to_retrieve'
    os.makedirs(base_extract_path, exist_ok=True)
    os.makedirs(final_txt_path, exist_ok=True)

    # Fetch papers from arXiv
    xml_data = fetch_arxiv_papers(search_query, max_results)

    # Parse the fetched XML data
    papers = parse_paper_data(xml_data)

    # Save the paper metadata to a .txt file
    save_paper_metadata_to_txt(papers, output_file)

    # Upload the .txt file to Google Cloud bucket
    upload_to_gcs(output_file, bucket_name)

    # Process each paper, downloading and uploading the .tex file if successful
    for paper in papers:
        url = paper['paper_id']
        tex_url = url.replace('/abs/', '/src/')
        print(f"Processing {tex_url}...")
        
        # Process the paper and handle any errors
        processed_paper = process_paper(tex_url, base_extract_path, final_txt_path)
        
        # Only upload if the paper was successfully processed
        if processed_paper:
            upload_to_gcs(processed_paper, bucket_name)
        else:
            print(f"Skipping upload for {tex_url} due to processing errors.")

if __name__ == "__main__":
    main()
