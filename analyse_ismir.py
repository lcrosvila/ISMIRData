# %%
import json
import os
import matplotlib.pyplot as plt

def search_topic_in_paper(paper, topic_keywords):
    """
    Check if the paper is related to any of the topic keywords.
    """
    title = paper.get('title', '').lower()

    if paper.get('abstract') is not None:  # Check if abstract is present
        abstract = paper.get('abstract', '').lower()
    elif paper.get('Abstract') is not None:
        abstract = paper.get('Abstract', '').lower()
    else:
        abstract = ''

    for keyword in topic_keywords:
        if keyword.lower() in title or keyword.lower() in abstract:
            return True
    return False

def analyze_proceedings(folder_path, topic_keywords):
    """
    Analyze proceedings JSON files to find papers related to the given topic keywords.
    """
    yearwise_papers_count_generation = {}
    yearwise_relevant_papers_count_generation = {}

    # Initialize yearwise counts
    for year in range(2000, 2023):  # Assuming years from 2000 to 2022
        yearwise_papers_count_generation[year] = 0
        yearwise_relevant_papers_count_generation[year] = 0

    # Iterate over each JSON file in the folder
    for filename in os.listdir(folder_path):
        if '2020' in filename:
            print('2020')
        if filename.endswith('.json'):
            year = int(filename.split('.')[0])  # Extract year from filename
            if year == '2020':
                print('2020')
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                papers = json.load(file)

                # Count papers for each year
                yearwise_papers_count_generation[year] += len(papers)

                # Count relevant papers for each year
                for paper in papers:
                    if search_topic_in_paper(paper, topic_keywords):
                        yearwise_relevant_papers_count_generation[year] += 1

    return yearwise_papers_count_generation, yearwise_relevant_papers_count_generation

# %%
# Define the folder path containing the JSON files
folder_path = 'proceedings'

# Define the topic keywords
topic_keywords = [
    "generative AI",
    "algorithmic composition",
    "music generation",
    "generation",
    "generate",
    "composition",
    "AI-driven composition",
    "neural network music",
    "automatic composition",
    "musical creativity",
    "machine-generated music",
    "AI-generated music"
]

analysis_topic_keywords = [
    "analysis",
    "evaluation",
    "criticism"
]

# %%
# Analyze the proceedings
yearwise_papers_count_generation, yearwise_relevant_papers_count_generation = analyze_proceedings(folder_path, topic_keywords)

# Calculate percentages for each year
yearwise_percentages = {year: (yearwise_relevant_papers_count_generation[year] / yearwise_papers_count_generation[year]) * 100
                        for year in range(2000, 2023)}

yearwise_absolute_counts_generation = {year: yearwise_relevant_papers_count_generation[year] for year in range(2000, 2023)}

# %%
# Plotting
plt.figure(figsize=(10, 6))
plt.plot(list(yearwise_percentages.keys()), list(yearwise_percentages.values()), marker='o')
plt.title('Percentage of Papers Related to Topics Over Years')
plt.xlabel('Year')
plt.ylabel('Percentage of Relevant Papers')
plt.grid(True)
plt.xticks(range(2000, 2023), rotation=45)
plt.tight_layout()
plt.show()

# %%
# do the same for analysis
yearwise_papers_count_analysis, yearwise_relevant_papers_count_analysis = analyze_proceedings(folder_path, analysis_topic_keywords)

yearwise_percentages_analysis = {year: (yearwise_relevant_papers_count_analysis[year] / yearwise_papers_count_analysis[year]) * 100
                        for year in range(2000, 2023)}

yearwise_absolute_counts_analysis = {year: yearwise_relevant_papers_count_analysis[year] for year in range(2000, 2023)}

plt.figure(figsize=(10, 6))
plt.plot(list(yearwise_percentages_analysis.keys()), list(yearwise_percentages_analysis.values()), marker='o')
plt.title('Percentage of Papers Related to Analysis Over Years')
plt.xlabel('Year')
plt.ylabel('Percentage of Relevant Papers')
plt.grid(True)
plt.xticks(range(2000, 2023), rotation=45)
plt.tight_layout()
plt.show()

# %%
# overlay the two plots
plt.figure(figsize=(10, 6))
plt.plot(list(yearwise_percentages.keys()), list(yearwise_percentages.values()), marker='o', label='Generation')
plt.plot(list(yearwise_percentages_analysis.keys()), list(yearwise_percentages_analysis.values()), marker='o', label='Analysis')
plt.title('Percentage of Papers Related to Topics Over Years')
plt.xlabel('Year')
plt.ylabel('Percentage of Relevant Papers')
plt.grid(True)
plt.xticks(range(2000, 2023), rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

# %%
# plot both in absolute counts
plt.figure(figsize=(10, 6))
plt.plot(list(yearwise_absolute_counts_generation.keys()), list(yearwise_absolute_counts_generation.values()), marker='o', label='Generation')
plt.plot(list(yearwise_absolute_counts_analysis.keys()), list(yearwise_absolute_counts_analysis.values()), marker='o', label='Analysis')
plt.title('Number of Papers Related to Topics Over Years')
plt.xlabel('Year')
plt.ylabel('Number of Relevant Papers')
plt.grid(True)
plt.xticks(range(2000, 2023), rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

# %%
# print the title of 5 papers for each year with most downloads matching the generation keywords
import requests

for year in range(2019, 2023):
    file_path = os.path.join(folder_path, f'{year}.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        papers = json.load(file)
        relevant_papers = [paper for paper in papers if search_topic_in_paper(paper, topic_keywords)]
        print(f'Year: {year}')
        # get the https://zenodo.org/api/records/{zenodo_id}/versions?size=5&sort=version&allversions=true using the zenodo_id
        for paper in relevant_papers:
            zenodo_id = paper.get('zenodo_id')
            if zenodo_id is not None:
                response = requests.get(f'https://zenodo.org/api/records/{zenodo_id}/versions?size=5&sort=version&allversions=true')
                if response.status_code == 200:
                    data = response.json()
                    for hit in data['hits']['hits']:
                        downloads = hit['stats']['downloads']
                        # add downloads to the paper 
                        paper['downloads'] = downloads
                else:
                    print('Error fetching data from Zenodo API')
            else:
                print(paper.get('title'))
        # sample relevant papers ordered by most downloads
        relevant_papers = sorted(relevant_papers, key=lambda x: x.get('downloads', 0), reverse=True)
        for paper in relevant_papers[:5]:
            print(paper.get('title'))
            print(paper.get('url'))
            # executre curl https://zenodo.org/records/{zenodo_id}/export/bibtex
            zenodo_id = paper.get('zenodo_id')
            if zenodo_id is not None:
                os.system(f'curl https://zenodo.org/records/{zenodo_id}/export/bibtex')