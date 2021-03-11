from simple_parsing import ArgumentParser
from loguru import logger
from workflow.scripts.general import mark_as_complete, load_spacy_model
from workflow.scripts.es_functions import create_index, delete_index, index_data

parser = ArgumentParser()

#from spacy.tokens import Doc

#Doc.set_extension("url", default=None)

parser.add_argument("--input", type=str, help="Input file prefix")
parser.add_argument("--output", type=str, help="Output file prefix")
args = parser.parse_args()

index_name = 'test'

def index_vector_data():
    delete_index(index_name)
    create_index(index_name,300)
    index_data(vector_data=f'{args.input}_vectors.pkl.gz',index_name=index_name)
    mark_as_complete(args.output)

index_vector_data()