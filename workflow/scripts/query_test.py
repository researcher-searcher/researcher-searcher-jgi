from loguru import logger
from workflow.scripts.es_functions import query_record
from workflow.scripts.general import load_spacy_model

vector_index_name = "sentence_vectors"


def query_vector_data():
    nlp = load_spacy_model()
    test_text1 = (
        "Funding is available from MRC’s Infections and Immunity Board to provide large, "
        "long-term and renewable programme funding for researchers working in the area of "
        "infections and immunity. There is no limit to the funding you can request. This "
        "funding opportunity runs three times every year."
    )
    test_text2 = (
        "Funding is available from MRC’s Neurosciences and Mental Health Board to support new partnerships between "
        "researchers in the area of neurosciences and mental health. Funding varies widely for partnerships lasting "
        "between one and five years. This funding opportunity runs three times every year."
    )
    test_text3 = (
        "We have implemented efficient search methods and an application programming interface, to create fast and convenient"
        " functions to utilize triples extracted from the biomedical literature by SemMedDB."
    )
    doc = nlp(test_text3)
    for sent in doc.sents:
        logger.info(sent)

        # vectors
        sent_vec = sent.vector
        res = query_record(index_name=vector_index_name, query_vector=sent_vec)
        if res:
            for r in res:
                if r["score"] > 0.5:
                    logger.info(f'full sent {r}')

        # noun chunks
        noun_chunk_string = ""
        for chunk in sent.noun_chunks:
            # for token in chunk:
            #    logger.info(token.lemma_)
            # logger.debug(chunk)
            # remove stopwords and things
            if (
                all(token.is_stop != True and token.is_punct != True for token in chunk)
                == True
            ):
                # not sure if should filter on number of words in chunk?
                # might work better here to avoid ambiguous single words, e.g. funding, background...
                if len(chunk) > 1:
                    logger.info(f"noun chunk: {chunk} {len(chunk)}")
                    noun_chunk_string+=str(chunk)+' '
        logger.info(noun_chunk_string)
        if noun_chunk_string != '':
            chunk_vec = nlp(noun_chunk_string).vector
            res = query_record(index_name=vector_index_name, query_vector=chunk_vec)
            if res:
                for r in res:
                    if r["score"] > 0.5:
                        logger.info(f'chunk {r}')
    # return res


# def query_text_data():
# todo

# index_vector_data()
res = query_vector_data()
# if res:
#    for r in res:
#        logger.info(r)
# else:
#    logger.info('No results')
