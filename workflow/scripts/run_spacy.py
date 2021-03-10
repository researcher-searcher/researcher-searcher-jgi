import scispacy
import spacy
import pandas as pd
import os
from scispacy.abbreviation import AbbreviationDetector
from spacy import displacy
from simple_parsing import ArgumentParser
from loguru import logger
from workflow.scripts.general import mark_as_complete

parser = ArgumentParser()

# Load English tokenizer, tagger, parser and NER
logger.info('Loading spacy model...')
#nlp = spacy.load("en_core_web_sm")
#nlp = spacy.load("en_core_web_lg")
#nlp = spacy.load("en_core_sci_scibert")
#nlp = spacy.load("en_core_sci_lg")
nlp = spacy.load("en_ner_bionlp13cg_md")
#nlp.add_pipe("abbreviation_detector")
logger.info('Done...')

# do we need to filter stopwords?
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS

#from spacy.tokens import Doc

#Doc.set_extension("url", default=None)

parser.add_argument("--input", type=str, help="Input file prefix")
parser.add_argument("--output", type=str, help="Output file prefix")
args = parser.parse_args()

def create_single_text(row):
    text = row['title']
    if row['abstract']:
        text = row['title']+row['abstract']
    return text 

def create_texts():
    # Process whole documents
    research_df = pd.read_csv(f'{args.input}.tsv.gz',sep='\t')

    # create single string of text
    # maybe just leave titles and abstract separate if treating each sentence separately
    textList=[]
    for i,rows in research_df.iterrows():
        if not type(rows['abstract']) == float:
            textList.append(f"{rows['title']} {rows['abstract']}")
        else:
            textList.append(rows['title'])
    research_df['text']=textList
    logger.debug(research_df.head())
    return research_df.tail()

def run_nlp(research_df):
    data = []
    existing_data = []
    vector_data = []
    text = list(research_df['text'])
    docs = list(nlp.pipe(text))

    f = f'{args.output}_vectors.pkl.gz'

    # check for existing
    if os.path.exists(f) and os.path.getsize(f) > 1:
        logger.info(f'Reading existing data {f}')
        existing_df = pd.read_pickle(f)
        #print(existing_df)
        existing_data = list(existing_df['url'].unique())
        #logger.debug(existing_data)
        try:
            data = existing_df.to_dict('records')
        except:
            logger.warning(f'Error when reading {f}')
        logger.debug(f'Got data on {len(existing_data)} emails')

    for i in range(0,len(docs)):
        doc = docs[i]
        
        logger.info(doc)
        df_row=research_df.iloc[i]
        if df_row['url'] in existing_data:
            logger.debug(f"{rows['url']} already done")
            continue
        logger.info(f'{i} {len(docs)}')
        
        #logger.info(tokens)
        assert doc.has_annotation("SENT_START")
        sent_num=0
        for sent in doc.sents:
            logger.info(sent.text)

            # create vectors
            #print(doc.vector)
            vector_data.append({'url':df_row['url'],'sent':sent_num,'vector':list(sent.vector)})

            # Analyze syntax
            noun_phrases=[]
            for chunk in sent.noun_chunks:
                #logger.debug(chunk)
                #remove stopwords and things
                if all(token.is_stop != True and token.is_punct != True and '-PRON-' not in token.lemma_ for token in chunk) == True:
                    # not sure if should filter on number of words in chunk?
                    if len(chunk) > 1:
                        noun_phrases.append(chunk)
                        data.append({'url':df_row['url'],'sent':sent_num,'noun_phrase':chunk})
            #logger.info(f"Noun phrases: {noun_phrases}")
            logger.info(f"Verbs: {[token.lemma_ for token in sent if token.pos_ == 'VERB']}")
            #logger.debug(f"All: {[token.lemma_ for token in doc]}")

            # Find named entities, phrases and concepts - can use 
            for entity in sent.ents:
                logger.debug(f'entity: {entity} #entity.text: {entity.text} entity.label_:{entity.label_}')
            sent_num+=1

    #logger.info(data)
    df = pd.DataFrame(data)
    logger.info(df.head())
    df.to_csv(f'{args.output}_noun_chunks.tsv.gz',sep='\t',index=False)

    df = pd.DataFrame(vector_data)
    logger.info(df.head())
    df.to_pickle(f)

    mark_as_complete(args.output)


    #unpickled_df = pd.read_pickle('workflow/results/sentence_spacy_vector.pkl.gz')
    #logger.info(unpickled_df.head())

research_df = create_texts()
run_nlp(research_df)