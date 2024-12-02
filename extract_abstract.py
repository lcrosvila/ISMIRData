import requests
import fitz 
import re
import os
import json

def extract_abstract(url):
    # Set headers to avoid the 406 error
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "application/pdf",
    }

    # Fetch the PDF file content
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Save the PDF content to a temporary file
        with open("temp.pdf", "wb") as f:
            f.write(response.content)

        # Open the PDF file using PyMuPDF (fitz)
        try:
            with fitz.open("temp.pdf") as doc:
                full_text = ""

                # Iterate through the pages to find the abstract
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # Extract the text using PyMuPDF's text extraction with layout
                    full_text += page.get_text("text")  # Extract all the text in layout
        except:
            print("Could not load pdf")
            full_text = ""  
            
        # Split the extracted text into lines
        lines = full_text.split('\n')

        # Iterate through the lines and extract the abstract
        abstract_lines = []
        capture = False
        for line in lines:
            # Check if this line contains the word "Abstract" (case-insensitive)
            if re.search(r"\babstract\b", line, re.IGNORECASE):
                capture = True
                continue
            
            # If we are capturing the abstract, collect the lines
            if capture:
                # Stop capturing if we hit a typical section header or an empty line
                if re.match(r"(\d\.|Background|Introduction|System Overview|Methods|References)", line, re.IGNORECASE) or line.strip() == "":
                    capture = False
                    break
                abstract_lines.append(line.strip())
        
        # Join the extracted lines to form the abstract text
        abstract = " ".join(abstract_lines).strip()

        # remove pdf
        os.remove("temp.pdf")

        return abstract

    else:
        print(f"Failed to fetch the PDF file. Status code: {response.status_code}")
        return None

def process_json_files(folder_path):
    # Get all JSON files in the 'proceedings' folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            print('Processing ', filename)
            file_path = os.path.join(folder_path, filename)
            
            # Open and load the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Iterate through each entry in the JSON file
            for entry in data:
                # Check if the abstract is null or contains '[TODO]'
                if not entry.get('abstract') or '[TODO]' in entry.get('abstract'):
                    print('Processing: ', entry.get('title'))
                    url = entry.get('ee')
                    if url is None or 'https' not in url: 
                        try:
                            file_key = requests.get(f"https://zenodo.org/api/records/{entry.get('zenodo_id')}/files").json()["entries"][0]["key"]
                            url = f"https://zenodo.org/records/{entry.get('zenodo_id')}/files/{file_key}"
                            entry['ee'] = url
                            # Extract the abstract using the URL
                            abstract = extract_abstract(url)
                        except:
                            print("could not extract url")
                            abstract = None
                    
                    else:
                        # Extract the abstract using the URL
                        abstract = extract_abstract(url)

                    # If the abstract is successfully extracted, update it in the JSON
                    if abstract:
                        entry['abstract'] = abstract
                    else:
                        print(f"Failed to extract abstract for {entry['title']}")
            
            # Save the updated JSON data back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Processed {filename}")

def clean_up_abstracts(proceedings_folder):
    """
    Function that cleans up the abstracts by removing HTML tags and entities.
    """
    for filename in os.listdir(proceedings_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(proceedings_folder, filename)
            with open(file_path) as file:
                data = json.load(file)
                for paper in data:
                    abstract = paper.get('abstract')
                    if abstract:
                        # Remove all html tags (e.g. &nbsp;</p>\n\n<p>&nbsp;</p>)
                        abstract = re.sub(r'<[^>]*>', '', abstract)
                        # Remove html entities
                        abstract = re.sub(r'&[a-z]+;', '', abstract)
                        # replace "\ufb01" by "fi"
                        abstract = abstract.replace("\ufb01", "fi")
                        # replace "\ufb02" by "fl"
                        abstract = abstract.replace("\ufb02", "fl")
                        # replace "\ufb03" by "ffi"
                        abstract = abstract.replace("\ufb03", "ffi")
                        # replace "\ufb04" by "ffl"
                        abstract = abstract.replace("\ufb04", "ffl")
                        # replace "\ufb00" by "ff"
                        abstract = abstract.replace("\ufb00", "ff")
                        # replace "\uf6d9" by ""
                        abstract = abstract.replace("\uf6d9", "")
                        # replace "\uffff" by ""
                        abstract = abstract.replace("\uffff", "")
                        paper['abstract'] = abstract
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

# Set the path to the 'proceedings' folder
proceedings_folder = 'proceedings'

# Call the function to process the JSON files
process_json_files(proceedings_folder)

# Call the function to clean up the abstracts
clean_up_abstracts(proceedings_folder)