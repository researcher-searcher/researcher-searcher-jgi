# researcher-searcher-jgi
Researcher Searcher for data science community at University of Bristol

# Setup

### Spacy

- https://spacy.io/models/en
- https://spacy.io/universe/project/spacy-universal-sentence-encoder

python -m spacy download en_core_web_lg
python -m spacy download en_core_web_trf


### ScispaCy

- https://allenai.github.io/scispacy/
- not using for now

pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_scibert-0.4.0.tar.gz

pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_lg-0.4.0.tar.gz

NER
- pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_ner_bionlp13cg_md-0.4.0.tar.gz

### Config

`mkdir config data`

### Queries

'''
POST /sentence_nouns/_search
{
  "query": {
    "match": {
      "noun_phrase": {
        "query": "breast cancer",
        "operator": "and",
        "fuzziness": "AUTO"
      }
    }
  },
  "_source": ["doc_id","sent_num","noun_phrase"]
}

POST /sentence_nouns/_search
{
  "query": {
    "match": {
      "noun_phrase": {
        "query": "cancer"      
      }
    }
  },
  "_source": ["doc_id","sent_num","noun_phrase"]
}

# use this to get tf-idf frequencies of words?
GET /sentence_nouns/_termvectors
{
  "doc": {
    "noun_phrase": "breast cancer"
  },
  "term_statistics": true,
  "field_statistics": true,
  "positions": false,
  "offsets": false,
  "filter": {
    "max_num_terms": 3,
    "min_term_freq": 1,
    "min_doc_freq": 1
  }
}

GET /sentence_vectors/_termvectors
{
  "doc": {
    "sent_text": "breast cancer"
  },
  "term_statistics": true,
  "field_statistics": true,
  "positions": false,
  "offsets": false,
  "filter": {
    "max_num_terms": 3,
    "min_term_freq": 1,
    "min_doc_freq": 1
  }
}
'''
