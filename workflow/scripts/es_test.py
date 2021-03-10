from loguru import logger
from workflow.scripts.es_functions import create_index, delete_index, index_data

index_name = 'test'
delete_index('test')
create_index('test',300)

index_data(vector_data='workflow/results/text_data_vectors.pkl.gz',index_name=index_name)