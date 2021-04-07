import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from loguru import logger

corpus = pd.read_csv("workflow/results/text_data_noun_chunks.tsv.gz",sep='\t',nrows=1000)
logger.info(corpus.head())

def vectorize_corpus(corpus):
    vectorizer = TfidfVectorizer()
    tfs = vectorizer.fit_transform(corpus['noun_phrase'])
    logger.info(vectorizer.get_feature_names())
    return vectorizer, tfs

def tfidf_doc(tfidf='',text=''):
    text=text.lower()
    #transform function transforms a document to document-term matrix
    response = tfidf.transform([text])

    #get the feature name from the model
    feature_names = tfidf.get_feature_names()
    res={}
    for col in response.nonzero()[1]:
        res[feature_names[col]]=response[0, col]
        #reverse sort the results
        sorted_res = sorted(res.items(), key=lambda kv: kv[1], reverse=True)
    return sorted_res

if __name__ == "__main__":
    vectorizer, tfs = vectorize_corpus(corpus)
    testText = 'earlier early eastern eating eating eating eccentric education educational'
    sorted_res = tfidf_doc(tfidf=vectorizer,text=testText)
    logger.info(sorted_res)