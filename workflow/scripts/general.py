import scispacy
import spacy

from loguru import logger

def mark_as_complete(name):
    f = open(name,'w')
    f.write('Done')
    f.close()

def load_spacy_model():
    # Load English tokenizer, tagger, parser and NER
    logger.info('Loading spacy model...')
    #nlp = spacy.load("en_core_web_sm")
    nlp = spacy.load("en_core_web_lg")
    #nlp = spacy.load("en_core_sci_scibert")
    #nlp = spacy.load("en_core_sci_lg")
    #nlp = spacy.load("en_ner_bionlp13cg_md")
    #nlp.add_pipe("abbreviation_detector")
    logger.info('Done...')
    return nlp