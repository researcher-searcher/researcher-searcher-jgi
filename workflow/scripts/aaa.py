import json
import pprint
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from loguru import logger
from sklearn.manifold import TSNE
from workflow.scripts.es_functions import vector_query, standard_query
from workflow.scripts.general import load_spacy_model, create_aaa_distances

RESEARCH_DATA = 'workflow/results/text_data_vectors.pkl.gz'
RESEARCH_VECTORS = 'workflow/results/research_vectors.pkl.gz'
RESEARCH_PAIRS = 'workflow/results/research_vector_pairs.pkl.gz'

tSNE=TSNE(n_components=2)

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
        if i % 1000 == 0:
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

def tsne():
    df=pd.read_pickle(RESEARCH_PAIRS)
    print(df.head())
    df_pivot = df.pivot(index='url1', columns='url2', values='score')
    print(df_pivot.shape)
    df_pivot = df_pivot.fillna(1)
    tSNE_result=tSNE.fit_transform(df_pivot)
    x=tSNE_result[:,0]
    y=tSNE_result[:,1]
    vector_df = pd.read_pickle(RESEARCH_VECTORS)
    vector_df['x']=x
    vector_df['y']=y
    print(vector_df.head())
    plt.figure(figsize=(16,7))
    sns.scatterplot(x='x',y='y',data=vector_df, legend="full")
    plt.savefig(f'workflow/results/researh-tsne.pdf')        

create_mean_vectors()
aaa=aaa_vectors()
create_pairwise(aaa)
