from elasticsearch import Elasticsearch
from elasticsearch import helpers
from collections import deque
from loguru import logger
import numpy as np
import time
import pandas as pd


TIMEOUT=300
es = Elasticsearch(['localhost:9200'],timeout=TIMEOUT)

def create_index(index_name,dim_size):
    if es.indices.exists(index_name, request_timeout=TIMEOUT):
        print ("Index name already exists, please choose another")
    else:
        request_body ={
                "settings":{
                    "number_of_shards" : 5,
                    "number_of_replicas":0,
                    "refresh_interval":-1,
                    "index.max_result_window": 100000
                },
                "mappings": {
                    "dynamic": "true",
                    "_source": {
                    "enabled": "true"
                    },
                    "properties": {
                    "doc-id": {
                        "type": "keyword"
                    },
                    "sent-id": {
                        "type": "keyword"
                    },
                    "sent_text": {
                        "type": "text"
                    },
                    "sent_vector": {
                        "type": "dense_vector",
                        "dims": dim_size
                    }
                    }
                }
            }
        res = es.indices.create(index = index_name, body = request_body, request_timeout=TIMEOUT)
        logger.info(res)

def delete_index(index_name):
    logger.info(f'Deleing {index_name}')
    res = es.indices.delete(index = index_name,request_timeout=TIMEOUT)
    logger.info(res)

def index_data(vector_data, index_name):
    print ("Indexing data...")
    #create_index(index_name)
    bulk_data = []
    counter = 1
    start = time.time()
    chunkSize = 1000

    df = pd.read_pickle(vector_data)
    for i,rows in df.iterrows():
    #with gzip.open(sentence_data) as f:
        # next(f)
        counter += 1
        if counter % 100 == 0:
            end = time.time()
            t = round((end - start), 4)
            print (len(bulk_data), t, counter)
        if counter % chunkSize == 0:
            deque(
                helpers.streaming_bulk(
                    client=es,
                    actions=bulk_data,
                    chunk_size=chunkSize,
                    request_timeout=TIMEOUT,
                    raise_on_error=True,
                ),
                maxlen=0,
            )
            bulk_data = []
        # print(line.decode('utf-8'))
        data_dict = {
            "doc-id": rows['url'],
            "sent-id": rows['sent_num'],
            "sent_text": rows['sent_text'],
            "sent_vector": rows['vector']
        }
        op_dict = {
            "_index": index_name,
            "_source": data_dict,
        }
        bulk_data.append(op_dict)
    print(len(bulk_data))
    deque(
        helpers.streaming_bulk(
            client=es,
            actions=bulk_data,
            chunk_size=chunkSize,
            request_timeout=TIMEOUT,
            raise_on_error=True,
        ),
        maxlen=0,
    )

    # check number of records, doesn't work very well with low refresh rate
    print ("Counting number of records...")
    try:
        es.indices.refresh(index=index_name, request_timeout=TIMEOUT)
        res = es.search(index=index_name, request_timeout=TIMEOUT)
        esRecords = res["hits"]["total"]
        print ("Number of records in index", index_name, "=", esRecords)
    except timeout:
        print ("counting index timeout", index_name)


def query_record(index_name,query_vector,record_size=100000,search_size=1000,score_min=0):
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                #+1 to deal with negative results (script score function must not produce negative scores)
                "source": "cosineSimilarity(params.query_vector, doc['text_vector']) +1",
                "params": {"query_vector": query_vector}
            }
        }
    }
    search_start = time.time()
    response = es.search(
        index=index_name,
        body={
            "size": search_size,
            "query": script_query,
            "_source": {"includes": ["name", "encode_text","full_text"]}
        }
    )
    #search_time = time.time() - search_start
    #print()
    #print("{} total hits.".format(response["hits"]["total"]["value"]))
    #print("search time: {:.2f} ms".format(search_time * 1000))
    results=[]
    for hit in response["hits"]["hits"]:
        #-1 to deal with +1 above
        #print("id: {}, score: {}".format(hit["_id"], hit["_score"] - 1))
        #print(hit["_source"])
        #print()
        #score cutoff
        if hit["_score"]-1>score_min:
            results.append({
                'name':hit["_source"]['name'],
                'score':hit["_score"]-1,
                'encode_text':hit['_source']['encode_text'],
                'full_text':hit['_source']['full_text']
            })
    return results