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
    #test_sent = 'machine learning'
    #test_sent = 'Bioinformatics computational biology'
    #test_sent = 'genome wide association studies gwas'
    #test_sent = 'Mendelian randomization'
    #test_sent = 'gwas'
    test_sent = 'What are the risk factors of breast cancer?'
    test_sent = 'breast cancer'
    doc = nlp(test_sent)
    doc_vec = doc.vector
    res = query_record(index_name=index_name,query_vector=doc_vec)
    return res

#def query_text_data():
    #todo

#index_vector_data()
res = query_vector_data()
if res:
    for r in res:
        logger.info(r)
else:
    logger.info('No results')
