from loguru import logger
from workflow.scripts.es_functions import create_index, delete_index, index_data, query_record
from workflow.scripts.general import load_spacy_model

index_name = 'test'

def index_vector_data():
    delete_index(index_name)
    create_index(index_name,300)
    index_data(vector_data='workflow/results/text_data_vectors.pkl.gz',index_name=index_name)

def query_vector_data():
    nlp = load_spacy_model()
    #test_sent = 'school and family'
    #test_sent = 'coronary heart disease'
    test_sent = 'machine learning'
    doc = nlp(test_sent)
    doc_vec = doc.vector
    res = query_record(index_name=index_name,query_vector=doc_vec)
    return res

#def query_text_data():
    #todo

#index_vector_data()
res = query_vector_data()
for r in res:
    print(r)
