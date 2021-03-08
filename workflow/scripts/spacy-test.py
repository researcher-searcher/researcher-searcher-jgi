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

def create_single_text(row):
    text = row['title']
    if row['abstract']:
        text = row['title']+row['abstract']
    return text 

# Process whole documents
research_meta_df = pd.read_csv('workflow/results/research_meta_data.tsv',sep='\t')
logger.info(research_meta_df.shape)
abstract_df = pd.read_csv('workflow/results/research_data.tsv',sep='\t')
logger.info(abstract_df.shape)
logger.info(abstract_df.head())
research_df = pd.merge(research_meta_df,abstract_df,left_on='url',right_on='url')
logger.info(research_df.shape)

# create single string of text
textList=[]
for i,rows in research_df.iterrows():
    if not isinstance(rows['abstract'],float):
        textList.append(f"{rows['title']} {rows['abstract']}")
    else:
        textList.append(rows['title'])
research_df['text']=textList
logger.debug(research_df.head())

def run_nlp(research_df):
    titles = list(research_df['text'])
    docs = list(nlp.pipe(titles))
    for doc in docs:
        logger.info(doc)
        assert doc.has_annotation("SENT_START")
        for sent in doc.sents:
            logger.info(sent.text)
            #print(doc.vector)
            # Analyze syntax
            logger.debug(f"Noun phrases: {[chunk.text for chunk in doc.noun_chunks]}")
            logger.debug(f"Verbs: {[token.lemma_ for token in doc if token.pos_ == 'VERB']}")
            #print("All:", [token.lemma_ for token in doc])

            # Find named entities, phrases and concepts
            for entity in doc.ents:
                logger.debug(f'{entity.text} {entity.label_}')

    #for i in docs:
    #    for j in docs

run_nlp(research_df)