# researcher-searcher-jgi
Researcher Searcher for data science community at University of Bristol

# Setup

[Docs](SETUP.md)

# Build process

- Data sources
- Information extraction
- Data Processing
- Storage (graph and Elasticsearch)
- Search methods (API)

## Data sources

### Sources
- List of people and email addresses from the JGI
- https://research-information.bris.ac.uk/

### Tools
- all information scraping done using BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- new structure of research pages makes this quite straight forward, e.g. specific class names for each attribute

## Information extraction

Really just looking for basic info for a set of people, organisations and publications, and the connections between them.

### Find people

For each email address:
- search 
- match results back to email address
- capture person info and page
- e.g. https://research-information.bris.ac.uk/en/searchAll/index/?search=ben+elsworth&pageSize=25&showAdvanced=false&allConcepts=true&inferConcepts=true&searchBy=PartOfNameOrTitle

`snakemake -r find_person -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L19
- issues with wrong email addresses, required some manual searching to match people to home page

### Get more info for each person

For each person home page:
- job title
- organisation info
- orcid

For each person publication page:
- e.g. https://research-information.bris.ac.uk/en/persons/benjamin-l-elsworth/publications/
- Get URL of publication

`snakemake -r get_person_data -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L43

### Get publication data

For each publication:
- title
- abstract
- year

`snakemake -r get_research_details -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L52
- takes a long time to query >20,000 pages

### Summary

CSV Files:
- Person info (name, email, person_id)
- Person metadata (person_id, title, org, orcid)
- Organisation info (org_id, name)
- Output data (output_id, title, abstract, year)
- Person to org (person_id, output_id)
- Person to output (person_id, org_id)

## Data Processing

Aims:
- Extract concepts/phrases from titles/abstract
- Create sentence vectors for titles/abstracts  

#### Concepts/phrases
- Creating a concept summary for each person can be done in many ways, e.g. [gensim phrases](https://radimrehurek.com/gensim/models/phrases.html) [sklearn tfidf-vectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- Currently using [Spacy noun chunks](https://spacy.io/usage/linguistic-features#noun-chunks) then running tf-idf via sklearn

#### Vectors
- Again, many options. Depends on downstream requirements. 
- Tried Spacy vectors but sentences are just averages of words (https://spacy.io/usage/linguistic-features#similarity-expectations)
  - "The similarity of Doc and Span objects defaults to the average of the token vectors. This means that the vector for “fast food” is the average of the vectors for “fast” and “food”, which isn’t necessarily representative of the phrase “fast food”."

`snakemake -r parse_text -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L60
