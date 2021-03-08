import scispacy
import spacy
import pandas as pd
from loguru import logger

# Load English tokenizer, tagger, parser and NER
#nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("en_core_web_lg")
#nlp = spacy.load("en_core_sci_scibert")


#from spacy.tokens import Doc

#Doc.set_extension("url", default=None)

# Process whole documents
research_meta_df = pd.read_csv('workflow/results/research_meta_data.tsv',sep='\t')
abstract_df = pd.read_csv('workflow/results/research_data.tsv',sep='\t')
research_df = pd.merge(research_meta_df,abstract_df,left_on='url',right_on='url')
logger.debug(research_df.head())

def run_nlp(research_df):
    titles = list(research_df['title'])
    docs = list(nlp.pipe(titles))
    for doc in docs:
        #print(doc.vector)
        # Analyze syntax
        logger.debug(f"Noun phrases: {[chunk.text for chunk in doc.noun_chunks]}")
        logger.debug(f"Verbs: {[token.lemma_ for token in doc if token.pos_ == 'VERB']}")
        #print("All:", [token.lemma_ for token in doc])

        # Find named entities, phrases and concepts
        for entity in doc.ents:
            logger.debug(f'{entity.text} {entity.label_}')

run_nlp(research_df)