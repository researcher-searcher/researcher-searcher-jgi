from loguru import logger
from workflow.scripts.es_functions import query_record
from workflow.scripts.general import load_spacy_model

index_name = 'test'

def query_vector_data():
    nlp = load_spacy_model()
    test_text = (
        "Funding is available from MRC’s Infections and Immunity Board to provide large, "
        "long-term and renewable programme funding for researchers working in the area of "
        "infections and immunity. There is no limit to the funding you can request. This "
        "funding opportunity runs three times every year."
        )
    doc = nlp(test_text)
    for sent in doc.sents:
        logger.info(sent)

        #vectors
        sent_vec = sent.vector
        res = query_record(index_name=index_name,query_vector=sent_vec)
        if res:
            for r in res:
                if r['score']>0.5:
                    logger.info(r)

        #noun chunks
        for chunk in sent.noun_chunks:
            #for token in chunk:
            #    logger.info(token.lemma_)
            #logger.debug(chunk)
            #remove stopwords and things
            if all(token.is_stop != True and token.is_punct != True for token in chunk) == True:
                # not sure if should filter on number of words in chunk?
                #if len(chunk) > 1:
                logger.info(f'noun chunk: {chunk} {len(chunk)}')
    #return res  

#def query_text_data():
    #todo

#index_vector_data()
res = query_vector_data()
#if res:
#    for r in res:
#        logger.info(r)
#else:
#    logger.info('No results')
