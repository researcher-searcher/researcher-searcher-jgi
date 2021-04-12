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

### Data sources

https://research-information.bris.ac.uk/

##### Find people

For each email address:
- search 
- match results back to email address
- capture person info and page
- e.g. https://research-information.bris.ac.uk/en/searchAll/index/?search=ben+elsworth&pageSize=25&showAdvanced=false&allConcepts=true&inferConcepts=true&searchBy=PartOfNameOrTitle

`snakemake -r find_person -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L19
- issues with wrong email addresses, required some manual searching to match people to home page

##### Get more info for each person

For each person home page:
- job title
- organisation info
- orcid

For each person publication page:
- e.g. https://research-information.bris.ac.uk/en/persons/benjamin-l-elsworth/publications/
- Get URL of publication

`snakemake -r get_person_data -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L43

##### 
