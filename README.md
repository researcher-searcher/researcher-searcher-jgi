# researcher-searcher-jgi
Researcher Searcher for data science community at University of Bristol

# Setup

[Docs](SETUP.md)

# Info

- Data sources
- Information extraction
- Data Processing
- Storage (graph and Elasticsearch)
- Search methods (API)

## Data sources

Sources:
- List of people and email addresses from the JGI
- https://research-information.bris.ac.uk/

Extraction tool:
- all information scraping done using BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- new structure of research pages makes this quite straight forward, e.g. specific class names for each attribute

#### Find people

For each email address:
- search 
- match results back to email address
- capture person info and page
- e.g. https://research-information.bris.ac.uk/en/searchAll/index/?search=ben+elsworth&pageSize=25&showAdvanced=false&allConcepts=true&inferConcepts=true&searchBy=PartOfNameOrTitle

`snakemake -r find_person -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L19
- issues with wrong email addresses, required some manual searching to match people to home page

#### Get more info for each person

For each person home page:
- job title
- organisation info
- orcid

For each person publication page:
- e.g. https://research-information.bris.ac.uk/en/persons/benjamin-l-elsworth/publications/
- Get URL of publication

`snakemake -r get_person_data -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L43

#### Get publication data

For each publication:
- title
- abstract
- year

`snakemake -r get_research_details -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L52
- takes a long time to query >20,000 pages

#### Summary

CSV Files:
- Person info (name, email, url)
- Person metadata (url, title, org, orcid)
- Output data (url, title, abstract, year)
- Person to output (url, url)

