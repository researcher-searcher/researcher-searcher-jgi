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

def load_model():
    # Load English tokenizer, tagger, parser and NER
    logger.info('Loading spacy model...')
    #nlp = spacy.load("en_core_web_sm")
    nlp = spacy.load("en_core_web_lg")
    #nlp = spacy.load("en_core_sci_scibert")
    #nlp = spacy.load("en_core_sci_lg")
    #nlp = spacy.load("en_ner_bionlp13cg_md")
    #nlp.add_pipe("abbreviation_detector")
    logger.info('Done...')
    return nlp

#from spacy.tokens import Doc

#Doc.set_extension("url", default=None)

parser.add_argument("--input", type=str, help="Input file prefix")
parser.add_argument("--output", type=str, help="Output file prefix")
args = parser.parse_args()

outfile = f'{args.output}_vectors.pkl.gz'
outdata=[]

def create_single_text(row):
    text = row['title']
    if row['abstract']:
        text = row['title']+row['abstract']
    return text 

def create_texts():
    # Process whole documents
    research_df = pd.read_csv(f'{args.input}.tsv.gz',sep='\t')
    existing_data = []
    # check for existing
    if os.path.exists(outfile) and os.path.getsize(outfile) > 1:
        logger.info(f'Reading existing data {outfile}')
        existing_df = pd.read_pickle(outfile)
        if not existing_df.empty:
        #print(existing_df)
            existing_data = list(existing_df['url'].unique())
            # remove matches
            logger.debug(research_df.shape)
            research_df=research_df[~research_df['url'].isin(existing_data)]
            logger.debug(research_df.shape)
            #logger.debug(existing_data)
            try:
                outdata = existing_df.to_dict('records')
            except:
                logger.warning(f'Error when reading {outfile}')
            logger.debug(f'Got data on {len(existing_data)} urls')
        else:
            logger.debug(f'Existing {outfile} is empty')

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
    return research_df

def run_nlp(research_df):
    if research_df.empty:
        logger.info('No new data')
        mark_as_complete(args.output)
        exit()
        
    vector_data = []

    nlp = load_model()
    # do we need to filter stopwords?
    spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
    
    text = list(research_df['text'])
    docs = list(nlp.pipe(text))

    for i in range(0,len(docs)):
        doc = docs[i]
        logger.info(doc)
        df_row=research_df.iloc[i]
        logger.info(f'{i} {len(docs)}')
        
        #logger.info(tokens)
        assert doc.has_annotation("SENT_START")
        sent_num=0
        for sent in doc.sents:
            logger.info(sent.text)

            # create vectors
            #print(doc.vector)
            vector_data.append({'url':df_row['url'],'sent_num':sent_num,'sent_text':sent.text,'vector':list(sent.vector)})

            # Analyze syntax
            noun_phrases=[]
            for chunk in sent.noun_chunks:
                #logger.debug(chunk)
                #remove stopwords and things
                if all(token.is_stop != True and token.is_punct != True and '-PRON-' not in token.lemma_ for token in chunk) == True:
                    # not sure if should filter on number of words in chunk?
                    if len(chunk) > 1:
                        noun_phrases.append(chunk)
                        outdata.append({'url':df_row['url'],'sent':sent_num,'noun_phrase':chunk})
            #logger.info(f"Noun phrases: {noun_phrases}")
            logger.info(f"Verbs: {[token.lemma_ for token in sent if token.pos_ == 'VERB']}")
            #logger.debug(f"All: {[token.lemma_ for token in doc]}")

            # Find named entities, phrases and concepts - can use 
            for entity in sent.ents:
                logger.debug(f'entity: {entity} #entity.text: {entity.text} entity.label_:{entity.label_}')
            sent_num+=1

    #logger.info(data)
    df = pd.DataFrame(outdata)
    logger.info(df.head())
    df.to_csv(f'{args.output}_noun_chunks.tsv.gz',sep='\t',index=False)

    df = pd.DataFrame(vector_data)
    logger.info(df.head())
    df.to_pickle(outfile)

    mark_as_complete(args.output)


    #unpickled_df = pd.read_pickle('workflow/results/sentence_spacy_vector.pkl.gz')
    #logger.info(unpickled_df.head())

research_df = create_texts()
run_nlp(research_df)