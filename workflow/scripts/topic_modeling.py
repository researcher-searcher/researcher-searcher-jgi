import pandas as pd
import os
from top2vec import Top2Vec
from loguru import logger

output_data = 'workflow/results/research_data.tsv.gz'
model_out = "workflow/results/top2vec.mdl"

def create_model():

    if os.path.exists(model_out):
        logger.info('Model exists')
    else:
        df = pd.read_csv(output_data,sep='\t',nrows=10000)
        logger.info(df)

        textList = []
        for i, rows in df.iterrows():
            if not type(rows["abstract"]) == float:
                textList.append(f"{rows['title']} {rows['abstract']}")
            else:
                textList.append(rows["title"])
        #research_df["text"] = textList

        model = Top2Vec(textList,speed='learn',workers=40)
        model.save(model_out)

def load_model():
    logger.info(f'loading model {model_out}')
    model = Top2Vec.load(model_out)
    return model

def explore(model):
    num_topics = model.get_num_topics()
    logger.info(f'{num_topics}')
    #topic_words, word_scores, topic_scores, topic_nums = model.search_topics(keywords=["machine","learning"], num_topics=5)
    #logger.info(topic_words)
    #logger.info(word_scores)
    #logger.info(topic_scores)
    #logger.info(topic_nums)

    # Semantic Search Documents by Keywords - https://github.com/ddangelov/Top2Vec#semantic-search-documents-by-keywords
    documents, document_scores, document_ids = model.search_documents_by_keywords(keywords=["machine", "learning"], num_docs=5)
    for doc, score, doc_id in zip(documents, document_scores, document_ids):
        logger.info(f"Document: {doc_id}, Score: {score}")
        logger.info("-----------")
        logger.info(doc)
        logger.info("-----------")
        logger.info()

create_model()
model = load_model()
explore(model)
