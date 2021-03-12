import json
import pprint
import pandas as pd
import numpy as np
from loguru import logger
from workflow.scripts.es_functions import vector_query, standard_query
from workflow.scripts.general import load_spacy_model, create_aaa_distances

RESEARCH_DATA = 'workflow/results/text_data_vectors.pkl.gz'
RESEARCH_VECTORS = 'workflow/results/research_vectors.tsv.gz'

def create_mean_vectors():
    logger.info(f'Reading {RESEARCH_DATA}')
    df = pd.read_pickle(RESEARCH_DATA)
    logger.info(df.head())

    vectors = df[['url','vector']].groupby(['url'])
    data = []
    for v in vectors:
        #logger.info(v[0])
        vector_list = list(v[1]['vector'])
        #logger.info(len(vector_list))
        mean_vector = list(np.mean(vector_list,axis=0))
        #logger.info(len(mean_vector))
        data.append({'url':v[0],'vector':mean_vector})
    md = pd.DataFrame(data)
    md.to_csv(RESEARCH_VECTORS,sep='\t',index=False)

def aaa_vectors():
    vector_df = pd.read_csv(RESEARCH_VECTORS,sep='\t')
    vectors = list(vector_df['vector'])
    logger.info(vectors.shape)
    aaa = create_aaa_distances(vectors)

#create_mean_vectors()
aaa_vectors()
