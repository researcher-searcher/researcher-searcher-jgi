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

PEOPLE_DATA = 'workflow/results/person_data.tsv.gz'
RESEARCH_METADATA = 'workflow/results/research_metadata.tsv.gz'
RESEARCH_DATA = 'workflow/results/text_data_vectors.pkl.gz'
RESEARCH_VECTORS = 'workflow/results/research_vectors.pkl.gz'
PEOPLE_VECTORS = 'workflow/results/people_vectors.pkl.gz'
RESEARCH_PAIRS = 'workflow/results/research_vector_pairs.pkl.gz'
PEOPLE_PAIRS = 'workflow/results/people_vector_pairs.pkl.gz'

tSNE=TSNE(n_components=2)

def create_mean_research_vectors():
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

def aaa_vectors(vector_file):
    vector_df = pd.read_pickle(vector_file)
    vectors = list(vector_df['vector'])
    logger.info(len(vectors))
    aaa = create_aaa_distances(vectors)
    return aaa

def create_pairwise_research(aaa):
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

def tsne_research():
    df=pd.read_pickle(RESEARCH_PAIRS)
    logger.info(df.head())
    df_pivot = df.pivot(index='url1', columns='url2', values='score')
    logger.info(df_pivot.shape)
    df_pivot = df_pivot.fillna(1)
    tSNE_result=tSNE.fit_transform(df_pivot)
    x=tSNE_result[:,0]
    y=tSNE_result[:,1]
    vector_df = pd.read_pickle(RESEARCH_VECTORS)
    vector_df['x']=x
    vector_df['y']=y
    logger.info(vector_df.head())
    plt.figure(figsize=(16,7))
    sns.scatterplot(x='x',y='y',data=vector_df, legend="full")
    plt.savefig(f'workflow/results/research-tsne.pdf')        

def create_mean_people_vectors():
    logger.info(f'Reading {RESEARCH_METADATA}')
    meta_df = pd.read_csv(RESEARCH_METADATA,sep='\t')
    logger.info(meta_df.head())

    #merge with research info
    logger.info(f'Reading {RESEARCH_DATA}')
    data_df = pd.read_pickle(RESEARCH_DATA)
    logger.info(data_df.head())

    df = pd.merge(meta_df,data_df,left_on='url',right_on='url')
    logger.info(df.shape)
    logger.info(f'\n{df.head()}')
    
    vectors = df[['email','vector']].groupby(['email'])
    data = []
    for v in vectors:
        vector_list = list(v[1]['vector'])
        mean_vector = list(np.mean(vector_list,axis=0))
        data.append({'email':v[0],'vector':mean_vector})
    md = pd.DataFrame(data)
    md.to_pickle(PEOPLE_VECTORS)

def create_pairwise_people(aaa):
    vector_df = pd.read_pickle(PEOPLE_VECTORS)
    num = vector_df.shape[0]
    data = []
    emails = list(vector_df['email'])
    for i in range(0,num):
        if i % 1000 == 0:
            logger.info(i)
        iname = emails[i]
        for j in range(0,num):
            jname = emails[j]
            data.append({
                'email1':iname,
                'email2':jname,
                'score': 1-aaa[i][j]
            })
    df = pd.DataFrame(data)
    df.drop_duplicates(subset=['email1','email2'],inplace=True)
    logger.info(f'Writing {PEOPLE_PAIRS}')
    df.to_pickle(PEOPLE_PAIRS)  

def tsne_people():
    df=pd.read_pickle(PEOPLE_PAIRS)
    logger.info(df.head())
    df_pivot = df.pivot(index='email1', columns='email2', values='score')
    logger.info(df_pivot.shape)
    df_pivot = df_pivot.fillna(1)
    tSNE_result=tSNE.fit_transform(df_pivot)
    x=tSNE_result[:,0]
    y=tSNE_result[:,1]
    vector_df = pd.read_pickle(PEOPLE_VECTORS)
    vector_df['x']=x
    vector_df['y']=y
    logger.info(vector_df.head())
    plt.figure(figsize=(16,7))
    sns.scatterplot(x='x',y='y',data=vector_df, legend="full")
    plt.savefig(f'workflow/results/people-tsne.pdf')  

########################################

def research_aaa():
    create_mean_research_vectors()
    aaa=aaa_vectors(RESEARCH_VECTORS)
    create_pairwise_research(aaa)
    tsne_research()

def people_aaa():
    create_mean_people_vectors()
    aaa=aaa_vectors(PEOPLE_VECTORS)
    create_pairwise_people(aaa)
    tsne_people()
    
people_aaa()