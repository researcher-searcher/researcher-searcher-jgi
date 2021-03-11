import pandas as pd
from simple_parsing import ArgumentParser
from loguru import logger
from workflow.scripts.general import mark_as_complete, load_spacy_model
from workflow.scripts.es_functions import (
    create_vector_index,
    create_noun_index,
    delete_index,
    index_vector_data,
    index_noun_data,
)

parser = ArgumentParser()

parser.add_argument("--input", type=str, help="Input file prefix")
parser.add_argument("--output", type=str, help="Output file prefix")
args = parser.parse_args()


def index_vectors():
    vector_index_name = "sentence_vectors"
    delete_index(vector_index_name)
    create_vector_index(index_name=vector_index_name, dim_size=300)
    df = pd.read_pickle(f"{args.input}_vectors.pkl.gz")
    index_vector_data(
        df=df, index_name=vector_index_name
    )

def index_nouns():
    noun_index_name = "sentence_nouns"
    delete_index(noun_index_name)
    create_noun_index(index_name=noun_index_name, dim_size=300)
    df = pd.read_csv(f'{args.input}_noun_chunks.tsv.gz',sep='\t')
    index_noun_data(
        df=df,index_name=noun_index_name
    )

if __name__ == "__main__":
    index_vectors()
    index_nouns()
    mark_as_complete(args.output)
