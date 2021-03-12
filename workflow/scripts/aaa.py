import json
import pprint
import pandas as pd
import numpy as np
from loguru import logger
from workflow.scripts.es_functions import vector_query, standard_query
from workflow.scripts.general import load_spacy_model, create_aaa_distances

RESEARCH_DATA = 'workflow/results/text_data_vectors.pkl.gz'
RESEARCH_VECTORS = 'workflow/results/research_vectors.pkl.gz'
RESEARCH_PAIRS = 'workflow/results/research_vector_pairs.pkl.gz'

def create_mean_vectors():
    logger.info(f'Reading {RESEARCH_DATA}')
    df = pd.read_pickle(RESEARCH_DATA)
    logger.info(df.head())

    vectors = df[['url','vector']].groupby(['url'])
    data = []
    for v in vectors:
        vector_list = list(v[1]['vector'])
        mean_vector = list(np.mean(vector_list,axis=0))
        data.append({'url':v[0],'vector':mean_vector})
    md = pd.DataFrame(data)
    md.to_pickle(RESEARCH_VECTORS)

def aaa_vectors():
    vector_df = pd.read_pickle(RESEARCH_VECTORS)
    vectors = list(vector_df['vector'])
    logger.info(len(vectors))
    aaa = create_aaa_distances(vectors)
    return aaa

def create_pairwise(aaa):
    vector_df = pd.read_pickle(RESEARCH_VECTORS)
    num = vector_df.shape[0]
    data = []
    urls = list(vector_df['url'])
    for i in range(0,num):
        if i % 100 == 0:
            logger.info(i)
        iname = urls[i]
        for j in range(0,num):
            jname = urls[j]
            data.append({
                'url1':iname,
                'url2':jname,
                'score': 1-aaa[i][j]
            })
    df = pd.DataFrame(data)
    df.drop_duplicates(subset=['url1','url2'],inplace=True)
    logger.info(f'Writing {RESEARCH_PAIRS}')
    df.to_pickle(RESEARCH_PAIRS)            

#create_mean_vectors()
aaa=aaa_vectors()
create_pairwise(aaa)
