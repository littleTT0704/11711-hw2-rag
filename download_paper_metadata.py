# Download papers given list of faculty info
# !/usr/bin/env python3
import json
import dotenv
import requests

dotenv.load_dotenv()

import os
from requests import Session
from typing import Union
import urllib3


api_key = ''


def get_paper(session: Session, paper_id: str, fields: str = 'paperId,title', **kwargs) -> dict:
    params = {
        'fields': fields,
        **kwargs,
    }
    headers = {
        'X-API-KEY': api_key,
    }
    with session.get(f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}', params=params,
                     headers=headers) as response:
        response.raise_for_status()
        return response.json()


def download_pdf(session: Session, url: str, path: str, user_agent: str = 'requests/2.0.0'):
    headers = {
        'user-agent': user_agent,
    }
    with session.get(url, headers=headers, stream=True, verify=False) as response:
        response.raise_for_status()
        if response.headers['content-type'] != 'application/pdf':
            raise Exception('The response is not a pdf')
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


def download_paper(session: Session, paper_id: str, directory: str = 'papers', user_agent: str = 'requests/2.0.0') -> \
Union[str, None]:
    paper = get_paper(session, paper_id, fields='paperId,isOpenAccess,openAccessPdf,year')
    if not paper['isOpenAccess']:
        return None
    if paper['openAccessPdf'] is None:
        return None
    if paper['year'] != 2023:
        return None

    paperId: str = paper['paperId']
    pdf_url: str = paper['openAccessPdf']['url']
    pdf_path = os.path.join(directory, f'{paperId}.pdf')
    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(pdf_path):
        download_pdf(session, pdf_url, pdf_path, user_agent=user_agent)

    return pdf_path


# Set up the headers with the API key
headers = {
    "x-api-key": api_key
}

# Specify the folder to store the JSON files and PDF files
json_output_folder = "author_data"
pdf_output_folder = "papers——2"

# Create the output folders if they don't exist
os.makedirs(json_output_folder, exist_ok=True)
os.makedirs(pdf_output_folder, exist_ok=True)

# Read the author information from the file
with open("faculty_info", "r") as file:
    author_info = file.read()

# Split the author information into lines
lines = author_info.split("\n")

# Loop through each line
for line in lines:
    # Split the line into fields
    fields = line.split(";")

    # Extract the author name and ID
    author_name = fields[0].strip()
    author_id = fields[-1].strip()

    # Specify the fields you want to fetch
    fields = "authorId,name,paperCount,papers.paperId"

    # Make the GET request to fetch author details with the specified fields and year filter
    response = requests.get(
        f'https://api.semanticscholar.org/graph/v1/author/{author_id}',
        headers=headers,
        params={'fields': fields, 'year': '2023'}
    )

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract the total count of papers
        paper_count = data.get("paperCount", 0)

        # Generate the filename for the JSON file
        filename = f"{author_name.replace(' ', '_')}.json"

        # Create the file path by joining the output folder and filename
        file_path = os.path.join(json_output_folder, filename)

        # Save the data as a JSON file in the output folder
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)

        print(f"Data for {author_name} saved as {file_path}")
        print(f"Total paper count for {author_name}: {paper_count}")

        # Extract the paper IDs from the response
        paper_ids = [paper["paperId"] for paper in data.get("papers", [])]

        # Download the papers
        for paper_id in paper_ids:
            try:
                result = download_paper(Session(), paper_id, directory=pdf_output_folder)
                if result is None:
                    print(f"'{paper_id}' is not open access or not published in 2023")
                else:
                    print(f"Downloaded '{paper_id}' to '{result}'")
            except Exception as e:
                print(f"Failed to download '{paper_id}': {type(e).__name__}: {e}")
    else:
        print(f"Error: {response.status_code}")
        if response.text:
            print(response.json())
        else:
            print("No additional error information is provided.")

#%%
def download_paper(session: Session, paper_id: str, directory: str = 'papers', user_agent: str = 'requests/2.0.0') -> Union[dict, None]:
    paper = get_paper(session, paper_id, fields='paperId,isOpenAccess,openAccessPdf,year,title,abstract,authors,venue,tldr')
    if not paper['isOpenAccess']:
        return None
    if paper['openAccessPdf'] is None:
        return None
    if paper['year'] != 2023:
        return None

    paperId: str = paper['paperId']
    pdf_url: str = paper['openAccessPdf']['url']
    pdf_path = os.path.join(directory, f'{paperId}.pdf')
    os.makedirs(directory, exist_ok=True)
#%%
# create Metadata given faculty_info
# !/usr/bin/env python3

import dotenv

dotenv.load_dotenv()

import os
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_key = ''


def get_paper_metadata(paper_id: str) -> dict:
    fields = 'paperId,title,abstract,authors,venue,year,tldr'
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields={fields}'
    headers = {
        'x-api-key': api_key
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        if response.text:
            print(response.json())
        else:
            print("No additional error information is provided.")
        return None


# Set up the headers with the API key
headers = {
    "x-api-key": api_key
}

# Specify the folder to store the JSON files
json_output_folder = "author_data"

# Create the output folder if it doesn't exist
os.makedirs(json_output_folder, exist_ok=True)

# Read the author information from the file
with open("faculty_info", "r") as file:
    author_info = file.read()

# Split the author information into lines
lines = author_info.split("\n")

# Loop through each line
for line in lines:
    # Split the line into fields
    fields = line.split(";")

    # Extract the author name and ID
    author_name = fields[0].strip()
    author_id = fields[-1].strip()

    # Specify the fields you want to fetch
    fields = "authorId,name,paperCount,papers.paperId"

    # Make the GET request to fetch author details with the specified fields and year filter
    response = requests.get(
        f'https://api.semanticscholar.org/graph/v1/author/{author_id}',
        headers=headers,
        params={'fields': fields, 'year': '2023'}
    )

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract the total count of papers
        paper_count = data.get("paperCount", 0)

        # Generate the filename for the JSON file
        filename = f"{author_name.replace(' ', '_')}.json"

        # Create the file path by joining the output folder and filename
        file_path = os.path.join(json_output_folder, filename)

        # Save the data as a JSON file in the output folder
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)

        print(f"Data for {author_name} saved as {file_path}")
        print(f"Total paper count for {author_name}: {paper_count}")

        # Extract the paper IDs from the response
        paper_ids = [paper["paperId"] for paper in data.get("papers", [])]

        # Retrieve metadata for each paper
        for paper_id in paper_ids:
            paper_metadata = get_paper_metadata(paper_id)
            if paper_metadata:
                print(f"Metadata for paper '{paper_id}':")
                print(json.dumps(paper_metadata, indent=2))
    else:
        print(f"Error: {response.status_code}")
        if response.text:
            print(response.json())
        else:
            print("No additional error information is provided.")

#%%
#li lei paper validation only
# !/usr/bin/env python3

import dotenv

dotenv.load_dotenv()

import os
import requests
from requests import Session
from typing import Union
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_key = '0OnRRg9xiz24obk7Om2IOaCeOlSVDfMbpYBohJme'


def get_paper(session: Session, paper_id: str, fields: str = 'paperId,title', **kwargs) -> dict:
    params = {
        'fields': fields,
        **kwargs,
    }
    headers = {
        'X-API-KEY': api_key,
    }
    with session.get(f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}', params=params,
                     headers=headers) as response:
        response.raise_for_status()
        return response.json()


def download_pdf(session: Session, url: str, path: str, user_agent: str = 'requests/2.0.0'):
    headers = {
        'user-agent': user_agent,
    }
    with session.get(url, headers=headers, stream=True, verify=False) as response:
        response.raise_for_status()
        if response.headers['content-type'] != 'application/pdf':
            raise Exception('The response is not a pdf')
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


def download_paper(session: Session, paper_id: str, directory: str = 'papers', user_agent: str = 'requests/2.0.0') -> Union[str, None]:
    paper = get_paper(session, paper_id, fields='paperId,isOpenAccess,openAccessPdf,year')
    if not paper['isOpenAccess']:
        return None
    if paper['openAccessPdf'] is None:
        return None
    if paper['year'] != 2023:
        return None

    paperId: str = paper['paperId']
    pdf_url: str = paper['openAccessPdf']['url']
    pdf_path = os.path.join(directory, f'{paperId}.pdf')
    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(pdf_path):
        download_pdf(session, pdf_url, pdf_path, user_agent=user_agent)

    return pdf_path


# Set up the headers with the API key
headers = {
    "x-api-key": api_key
}

# Specify the folder to store the JSON files and PDF files
json_output_folder = "author_data-li-lei"
pdf_output_folder = "papers-li-lei"

# Create the output folders if they don't exist
os.makedirs(json_output_folder, exist_ok=True)
os.makedirs(pdf_output_folder, exist_ok=True)

# Author information
author_name = "Lei Li"
author_id = "49192881"

# Specify the fields you want to fetch
fields = "authorId,name,paperCount,papers.paperId"

# Make the GET request to fetch author details with the specified fields and year filter
response = requests.get(
    f'https://api.semanticscholar.org/graph/v1/author/{author_id}',
    headers=headers,
    params={'fields': fields, 'year': '2023'}
)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Extract the total count of papers
    paper_count = data.get("paperCount", 0)

    # Generate the filename for the JSON file
    filename = f"{author_name.replace(' ', '_')}.json"

    # Create the file path by joining the output folder and filename
    file_path = os.path.join(json_output_folder, filename)

    # Save the data as a JSON file in the output folder
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

    print(f"Data for {author_name} saved as {file_path}")
    print(f"Total paper count for {author_name}: {paper_count}")

    # Extract the paper IDs from the response
    paper_ids = [paper["paperId"] for paper in data.get("papers", [])]

    # Download the papers
    for paper_id in paper_ids:
        try:
            result = download_paper(Session(), paper_id, directory=pdf_output_folder)
            if result is None:
                print(f"'{paper_id}' is not open access or not published in 2023")
            else:
                print(f"Downloaded '{paper_id}' to '{result}'")
        except Exception as e:
            print(f"Failed to download '{paper_id}': {type(e).__name__}: {e}")
else:
    print(f"Error: {response.status_code}")
    if response.text:
        print(response.json())
    else:
        print("No additional error information is provided.")
