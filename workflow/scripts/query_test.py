from loguru import logger
from workflow.scripts.es_functions import query_record
from workflow.scripts.general import load_spacy_model

vector_index_name = "sentence_vectors"
nlp = load_spacy_model()

def q1():
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

def q2():
    test_text4 = (
        "Ankyrin-R provides a key link between band 3 and the spectrin cytoskeleton that helps to maintain the highly "
        "specialised erythrocyte biconcave shape. Ankyrin deficiency results in fragile spherocytic erythrocytes with "
        "reduced band 3 and protein 4.2 expression. We use in vitro differentiation of erythroblasts transduced with shRNAs "
        "targeting the ANK1 gene to generate erythroblasts and reticulocytes with a novel ankyrin-R ‘near null’ human "
        "phenotype with less than 5% of normal ankyrin expression. Using this model we demonstrate that absence of ankyrin "
        "negatively impacts the reticulocyte expression of a variety of proteins including band 3, glycophorin A, spectrin, "
        "adducin and more strikingly protein 4.2, CD44, CD47 and Rh/RhAG. Loss of band 3, which fails to form tetrameric "
        "complexes in the absence of ankyrin, alongside GPA, occurs due to reduced retention within the reticulocyte membrane "
        "during erythroblast enucleation. However, loss of RhAG is temporally and mechanistically distinct, occurring "
        "predominantly as a result of instability at the plasma membrane and lysosomal degradation prior to enucleation. "
        "Loss of Rh/RhAG was identified as common to erythrocytes with naturally occurring ankyrin deficiency and "
        "demonstrated to occur prior to enucleation in cultures of erythroblasts from a hereditary spherocytosis patient "
        "with severe ankyrin deficiency but not in those exhibiting milder reductions in expression. The identification of "
        "prominently reduced surface expression of Rh/RhAG in combination with direct evaluation of ankyrin expression using "
        "flow cytometry provides an efficient and rapid approach for the categorisation of hereditary spherocytosis arising "
        "from ankyrin deficiency."
    )
    doc = nlp(test_text4)
    res = query_record(index_name=vector_index_name, query_vector=doc.vector)
    if res:
        for r in res:
            if r["score"] > 0.5:
                logger.info(f'full sent {r}')


# def query_text_data():
# todo

# index_vector_data()
#res = q1()
res = q2()
# if res:
#    for r in res:
#        logger.info(r)
# else:
#    logger.info('No results')
