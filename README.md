# researcher-searcher-jgi
Researcher Searcher for data science community at University of Bristol

# Setup

[Docs](SETUP.md)

# Build process

- Data sources
- Information extraction
- Data Processing
- Search (needs to move to separete repo)
- Graph (https://github.com/elswob/researcher-searcher-graph)
- API (https://github.com/elswob/researcher-searcher-api)

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
- search https://research-information.bris.ac.uk/
- match results back to email address
- capture person info and page
- e.g. https://research-information.bris.ac.uk/en/searchAll/index/?search=ben+elsworth&pageSize=25&showAdvanced=false&allConcepts=true&inferConcepts=true&searchBy=PartOfNameOrTitle

#### Run
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

#### Run
`snakemake -r get_person_data -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L43

### Get publication data

For each publication:
- title
- abstract
- year

#### Run
`snakemake -r get_research_details -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L52
- takes a long time to query >20,000 pages

### Output

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
- Compare vectors

#### Run
`snakemake -r parse_text -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L60
`snakemake -r process_text -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L68

### Concepts/phrases
- Creating a concept summary for each person can be done in many ways, e.g. [gensim phrases](https://radimrehurek.com/gensim/models/phrases.html) [sklearn tfidf-vectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- Currently using [Spacy noun chunks](https://spacy.io/usage/linguistic-features#noun-chunks) then running tf-idf via sklearn

### TF-IDF

Can override the default method from sklearn tfidf-vectorizer to create tf-idf score for spacy noun chunks.
- create files connecting each person to noun_chunks with tf-idf score

### Vectors
- Again, many options, partially depends on downstream requirements. 
- Tried Spacy vectors but sentences are just averages of words (https://spacy.io/usage/linguistic-features#similarity-expectations)
  - "The similarity of Doc and Span objects defaults to the average of the token vectors. This means that the vector for “fast food” is the average of the vectors for “fast” and “food”, which isn’t necessarily representative of the phrase “fast food”."
- Currently using Google Universal Sentence Embedding via spacy (https://spacy.io/universe/project/spacy-universal-sentence-encoder)
  - not convinced this is better for single words.... 
- Currently creating a vector for every sentence in every title and abstract

### Calculating distances

Once we have vectors for every sentence we can create distances between publications and people.
- create mean sentence vectors

Example of how this can be visualised - `output/plotly.html`

### Output

CSV files:
- vectors for each sentence (output_id, sentence_id, vector)
- noun chunks for each sentence (output_id, sentence_id, noun_chunk)

## Search

#### Method

- create indexes for sentence title and abstract vectors (https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html)
  - also include full text indexing (https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html)
- Create indexes for sentence title and abstract noun_chunks
  - not using at the moment

#### Build

Docker containers for Elasticsearch and Kibana

`docker-compose up`

#### Run

Currently Elasticsearch indexes are created and populated within this repo, but should move to separate.

`snakemake -r index_data -j 1`
- https://github.com/elswob/researcher-searcher-jgi/blob/main/workflow/Snakefile#L76


## Graph

Using our [Neo4j build pipeline](https://github.com/elswob/neo4j-build-pipeline)
- defined schemas
- pre and post build tests

![graph schema](https://github.com/elswob/researcher-searcher-jgi/blob/main/output/graph.png?raw=true)

## API

Using FastAPI docker image as starting point - https://fastapi.tiangolo.com/deployment/docker/
- modify to different version of FastAPI due to issues with Universal Sentence Encoder requirements

Currently, three end points
1. text search (top 100)
  - return person via sentence vectors 
  - return person via full text 
  - return person via person vectors
  - return publication via publication vectors
2. person
  - return top x noun chunks for a given person
3. collaboration
  - return most similar person (with/without shared publications)
 
API - https://bdsn-api.mrcieu.ac.uk/
