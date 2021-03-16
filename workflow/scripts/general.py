import scispacy
import spacy
import numpy as np
from scipy.spatial import distance
from loguru import logger


def mark_as_complete(name):
    f = open(name, "w")
    f.write("Done")
    f.close()


def load_spacy_model():
    model_name = "en_core_web_trf"
    # Load English tokenizer, tagger, parser and NER
    logger.info(f"Loading spacy model {model_name}")
    # nlp = spacy.load("en_core_web_sm")
    #nlp = spacy.load("en_core_web_lg")
    nlp = spacy.load(model_name)
    # nlp = spacy.load("en_core_sci_scibert")
    # nlp = spacy.load("en_core_sci_lg")
    # nlp = spacy.load("en_ner_bionlp13cg_md")
    # nlp.add_pipe("abbreviation_detector")

    # add max length for transformer
    if model_name == 'en_core_web_trf':
        nlp.max_length = 512
    logger.info("Done...")
    return nlp

def create_aaa_distances(vectors=[]):
    print('Creating distances...')
    #https://stackoverflow.com/questions/48838346/how-to-speed-up-computation-of-cosine-similarity-between-set-of-vectors

    print(len(vectors))
    data = np.array(vectors)
    pws = distance.pdist(data, metric='cosine')
    #return as square-form distance matrix
    pws = distance.squareform(pws)
    print(len(pws))
    return pws

#takes an array of vectors
def create_pair_distances(v1=[],v2=[]):
    print('Creating distances...')
    #https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html#scipy.spatial.distance.cdist

    print(len(v1),len(v2))
    y = distance.cdist(v1, v2, 'cosine')
    print(len(y))
    return y