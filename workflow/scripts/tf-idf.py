import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from loguru import logger

corpus = pd.read_csv("workflow/results/text_data_noun_chunks.tsv.gz",sep='\t')
logger.info(corpus.head())
#logger.debug(corpus['noun_phrase'])

# http://www.davidsbatista.net/blog/2018/02/28/TfidfVectorizer/
def dummy_fun(doc):
    return doc

docs = [
    ['Two dogs', 'wrongs', 'don\'t', 'make', 'a', 'right', '.'],
    ['The', 'pen', 'is', 'mightier', 'than', 'the', 'sword'],
    ['Don\'t', 'put', 'all', 'your', 'eggs', 'in', 'one', 'basket', '.']
]

def vectorize_corpus(corpus):
    vectorizer = TfidfVectorizer(
        analyzer = 'word',
        tokenizer=dummy_fun,
        preprocessor=dummy_fun,
        token_pattern=None
        )
    # create list of lists
    corpus_data = []
    for i in list(corpus['noun_phrase'].str.lower()):
        corpus_data.append([i])
    vectorizer.fit_transform(corpus_data)
    #logger.info(vectorizer.get_feature_names())
    return vectorizer

def tfidf_doc(tfidf='',text=[]):
    #text=text.lower()
    #transform function transforms a document to document-term matrix
    response = tfidf.transform([text])
    print(response)

    #get the feature name from the model
    feature_names = tfidf.get_feature_names()
    res={}
    sorted_res = []
    for col in response.nonzero()[1]:
        res[feature_names[col]]=response[0, col]
        #reverse sort the results
        sorted_res = sorted(res.items(), key=lambda kv: kv[1], reverse=True)
    return sorted_res

def person_to_output():
    logger.info('Getting person to output data...')

if __name__ == "__main__":
    vectorizer = vectorize_corpus(corpus)
    feature_names = vectorizer.get_feature_names()
    df = pd.DataFrame(feature_names)
    logger.info(df.head())
    df.to_csv("workflow/results/noun_chunks.tsv.gz",index=False,header=False)
    testText = ['knee osteoarthritis','machine learning','vitamin']
    sorted_res = tfidf_doc(tfidf=vectorizer,text=testText)
    logger.info(sorted_res)