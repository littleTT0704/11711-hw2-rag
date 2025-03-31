import requests
from bs4 import BeautifulSoup

# Your Semantic Scholar API key
API_KEY = ''  # Replace with your actual Semantic Scholar API key

# Headers to include in every API request
HEADERS = {
    'x-api-key': API_KEY
}

def get_faculty_names(urls):
    faculty_names = []  # Initialize an empty list to store faculty names
    for url in urls:
        while url:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            faculty_divs = soup.find_all('div', class_='views-field-nothing')
            for div in faculty_divs:
                name = div.find('h2').text.strip()
                faculty_names.append(name)  # Add the faculty name to the list

            next_page_link = soup.find('a', title="Go to next page")
            if next_page_link:
                url = 'https://lti.cs.cmu.edu' + next_page_link['href']
            else:
                url = None
    return faculty_names

def search_author_and_fetch_papers(author_name):
    # Define the API endpoint for searching authors by name
    search_url = "https://api.semanticscholar.org/graph/v1/author/search"
    query_params = {
        "query": author_name,
        "fields": "authorId,name"
    }

    # Send the search request
    search_response = requests.get(search_url, headers=HEADERS, params=query_params)
    if search_response.status_code == 200:
        search_results = search_response.json()
        authors = search_results.get('data', [])
        if authors:
            # Only consider the first author result
            author = authors[0]
            author_id = author['authorId']
            print(f"Author: {author['name']}, ID: {author_id}")

            # Fetch papers for this author
            papers_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers"
            papers_response = requests.get(papers_url, headers=HEADERS)
            if papers_response.status_code == 200:
                papers_results = papers_response.json()
                for paper in papers_results.get('data', []):
                    print(f" - Paper Title: {paper.get('title')}")
            else:
                print(f"Failed to fetch papers for author ID {author_id}")
        else:
            print(f"No results found for author {author_name}")
    else:
        print(f"Search failed for author {author_name} with status code {search_response.status_code}")

# Starting URLs for faculty
start_urls = [
    'https://lti.cs.cmu.edu/directory/all/154/1',      # Core faculty
    'https://lti.cs.cmu.edu/directory/all/154/2728',   # Affiliated faculty
    'https://lti.cs.cmu.edu/directory/all/154/200'     # Adjunct faculty
]

# Extract faculty names
faculty_names = get_faculty_names(start_urls)
lti_faculty_names = []  # Initialize the list

# For each faculty name, search for the author on Semantic Scholar and fetch their papers
for name in faculty_names:
    lti_faculty_names.append(name)  # Append each name to the lti_faculty_names list
    #search_author_and_fetch_papers(name)
#%%
print(lti_faculty_names)
#%%
#!/usr/bin/env python3
import requests
from requests import Session
import os
import urllib3

# Suppress warnings if you are not verifying SSL certificates
urllib3.disable_warnings()

# Your Semantic Scholar API key
S2_API_KEY = os.environ.get('S2_API_KEY', '')  # Replace 'Your API Key Here' with your actual Semantic Scholar API key

def get_author_papers(author_name: str) -> list[str]:
    """Fetch paper IDs for the given author."""
    url = 'https://api.semanticscholar.org/graph/v1/author/search'
    headers = {'x-api-key': S2_API_KEY}
    params = {'query': author_name, 'fields': 'authorId'}
    paper_ids = []

    with requests.get(url, headers=headers, params=params) as response:
        response.raise_for_status()
        authors = response.json().get('data', [])
        if authors:
            author_id = authors[0]['authorId']
            papers_url = f'https://api.semanticscholar.org/graph/v1/author/{author_id}/papers'
            with requests.get(papers_url, headers=headers) as papers_response:
                papers_response.raise_for_status()
                papers = papers_response.json().get('data', [])
                for paper in papers:
                    paper_ids.append(paper['paperId'])
    return paper_ids

def download_paper(session: Session, paper_id: str, directory: str = 'papers') -> str:
    """Download the paper if it's open access."""
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}'
    headers = {'X-API-KEY': S2_API_KEY}
    params = {'fields': 'paperId,isOpenAccess,openAccessPdf'}

    with session.get(url, params=params, headers=headers) as response:
        response.raise_for_status()
        paper = response.json()
        if not paper.get('isOpenAccess'):
            return 'Not open access'
        pdf_url = paper.get('openAccessPdf', {}).get('url')
        if not pdf_url:
            return 'No PDF available'
        pdf_path = os.path.join(directory, f'{paper_id}.pdf')
        os.makedirs(directory, exist_ok=True)
        if not os.path.exists(pdf_path):
            user_agent = 'requests/2.0.0'
            headers = {'user-agent': user_agent}
            with session.get(pdf_url, headers=headers, stream=True, verify=False) as pdf_response:
                pdf_response.raise_for_status()
                if pdf_response.headers.get('content-type') != 'application/pdf':
                    raise Exception('The response is not a PDF')
                with open(pdf_path, 'wb') as f:
                    for chunk in pdf_response.iter_content(chunk_size=8192):
                        f.write(chunk)
        return pdf_path
#%%

def main(faculty_names):
    """Fetch and download papers for a list of faculty names."""
    with Session() as session:
        for author_name in faculty_names:
            print(f'Fetching papers for {author_name}')
            paper_ids = get_author_papers(author_name)
            for paper_id in paper_ids:
                try:
                    result = download_paper(session, paper_id)
                    if result not in ['Not open access', 'No PDF available']:
                        print(f"Downloaded '{paper_id}' to '{result}'")
                    else:
                        print(f"'{paper_id}' {result}")
                except Exception as e:
                    print(f"Failed to download '{paper_id}': {e}")

if __name__ == '__main__':
    main(faculty_names)

#%%

import os

# Directory where the papers are stored
papers_directory = '/Users/evelynzhu/PycharmProjects/nlp-hw2-extraction/papers'

# List all files in the directory
all_files = os.listdir(papers_directory)

# Set to store seen file hashes
seen_hashes = set()
duplicates = []

# Iterate over files and check for duplicates based on file names (assuming file names are unique identifiers for the content)
for filename in all_files:
    # Create a unique identifier for the file (e.g., using the file name)
    # In real scenarios, you might want to use file content or a hash of it for duplication check
    if filename in seen_hashes:
        # This is a duplicate
        duplicates.append(filename)
    else:
        seen_hashes.add(filename)

# Remove duplicate files
for duplicate in duplicates:
    os.remove(os.path.join(papers_directory, duplicate))

# Return the number of removed duplicates
len(duplicates)
