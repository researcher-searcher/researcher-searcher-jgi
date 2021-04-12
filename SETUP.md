# Environment

### Conda

`conda env create -f environment.yaml`

### Config

`mkdir config data`

### Spacy

- https://spacy.io/models/en
- https://spacy.io/universe/project/spacy-universal-sentence-encoder

```
python -m spacy download en_core_web_lg
pip install spacy-universal-sentence-encoder
```

### ScispaCy

- https://allenai.github.io/scispacy/
- not using for now

```
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_scibert-0.4.0.tar.gz
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_lg-0.4.0.tar.gz

NER
- pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_ner_bionlp13cg_md-0.4.0.tar.gz
```

### Build

Snakemake controls the build process, using cached files to avoid repeated data processing.

`snakemake -r all -j 10`

### Queries

```
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

POST /use_abstract_sentence_vectors/_search
{
  "query": {
    "match": {
      "sent_text": {
        "query": "apple computer"      
      }
    }
  },
  "_source": ["doc_id","sent_num","sent_text"],
  "indices_boost": [
    { "title_sentence_vectors": 1 },
    { "abstract_sentence_vectors": 1 }
  ]
}

```

