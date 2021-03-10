from loguru import logger
from workflow.scripts.es_functions import create_index, delete_index

index_name = 'test'
delete_index('test')
create_index('test',100)