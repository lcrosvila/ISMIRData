import os
import requests
import json
import re
import time
from datetime import datetime

def fetch_ismir_data(year):
    """Fetches the JSON data from DBLP for a given year."""
    url = f'https://dblp.uni-trier.de/search/publ/api?q=toc%3Adb/conf/ismir/ismir{year}.bht%3A&h=1000&format=json'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for year {year}")
        return None

def get_zenodo_metadata(title):
    """Searches for Zenodo metadata using the title."""
    zenodo_url = "https://zenodo.org/api/records"
    # replace '/' from title to ' ' 
    title = title.replace('/', ' ')
    params = {'q': title, 'size': 1}
    try:
        response = requests.get(zenodo_url, params=params)
        if response.status_code == 200 and response.json()['hits']['hits']:
            record = response.json()['hits']['hits'][0]
            doi = record.get('doi')
            zenodo_id = record.get('id')
            abstract = record.get('metadata', {}).get('description', None)
            return doi, zenodo_id, abstract
    except Exception as e:
        print(f"Error searching Zenodo for title '{title}': {e}")
    return None, None, None

def parse_data(hit):
    """Parses a single entry from the DBLP hit and retrieves relevant information."""
    info = hit.get('info', {})
    title = info.get('title')
    authors = info.get('authors', {}).get('author', [])
    year = info.get('year')
    ee = info.get('ee')
    dblp_key = info.get('key')

    # Normalize author field (single author vs list of authors)
    if isinstance(authors, dict):
        authors = [authors.get('text')]
    else:
        authors = [author.get('text') for author in authors]

    # Get DOI, Zenodo ID, and abstract
    doi, zenodo_id, abstract = get_zenodo_metadata(title)

    # Construct URL from DOI if available
    url = f"https://doi.org/{doi}" if doi else None

    # Construct entry
    entry = {
        "title": title,
        "author": authors,
        "year": year,
        "doi": doi,
        "url": url,
        "ee": ee,
        "abstract": abstract,
        "zenodo_id": zenodo_id,
        "dblp_key": dblp_key
    }
    return entry

def save_data(year, data):
    """Saves the parsed data for a given year into a JSON file in the 'proceedings' folder."""
    if not os.path.exists('proceedings'):
        os.makedirs('proceedings')

    file_path = os.path.join('proceedings', f'{year}.json')
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved data for year {year} to {file_path}")

def main():
    current_year = datetime.now().year

    # Iterate through each year from 2000 to the current year
    for year in range(2000, current_year + 1):
        print(f"Fetching data for year {year}...")
        json_data = fetch_ismir_data(year)
        if json_data:
            hits = json_data.get('result', {}).get('hits', {}).get('hit', [])
            parsed_entries = [parse_data(hit) for hit in hits]
            save_data(year, parsed_entries)

        # Respectful delay to avoid rate limiting
        time.sleep(1)

        print("Data collection complete. All files saved in the 'proceedings' folder.")

if __name__ == "__main__":
    main()
