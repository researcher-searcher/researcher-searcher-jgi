import scispacy
import spacy
import pandas as pd
from loguru import logger
from scispacy.abbreviation import AbbreviationDetector
from spacy import displacy


# Load English tokenizer, tagger, parser and NER
#nlp = spacy.load("en_core_web_sm")
#nlp = spacy.load("en_core_web_lg")
#nlp = spacy.load("en_core_sci_scibert")
nlp = spacy.load("en_core_sci_lg")
nlp = spacy.load("en_ner_bionlp13cg_md")
nlp.add_pipe("abbreviation_detector")

# do we need to filter stopwords?
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS

#from spacy.tokens import Doc

#Doc.set_extension("url", default=None)

def create_single_text(row):
    text = row['title']
    if row['abstract']:
        text = row['title']+row['abstract']
    return text 

def create_texts():
    # Process whole documents
    research_meta_df = pd.read_csv('workflow/results/research_meta_data.tsv',sep='\t')
    logger.info(research_meta_df.shape)
    abstract_df = pd.read_csv('workflow/results/research_data.tsv',sep='\t')
    logger.info(abstract_df.shape)
    logger.info(abstract_df.head())
    research_df = pd.merge(research_meta_df,abstract_df,left_on='url',right_on='url')
    logger.info(research_df.shape)

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
    return research_df.tail(n=10)

def run_nlp(research_df):
    text = list(research_df['text'])
    docs = list(nlp.pipe(text))
    for doc in docs:
        logger.info(doc)
        #tokens = [token.text for token in doc if not token.is_stop]
        #logger.info(tokens)
        assert doc.has_annotation("SENT_START")
        for sent in doc.sents:
            
            #displacy
            #html = displacy.render(doc, style="dep", page=True, minify=True)
            #dis = displacy.serve(doc, style="ent")
            #logger.info(html)

            logger.info(sent.text)
            #print(doc.vector)
            # Analyze syntax
            noun_phrases=[]
            for chunk in sent.noun_chunks:
                logger.debug(chunk)
                #remove stopwords
                if all(token.is_stop != True and token.is_punct != True and '-PRON-' not in token.lemma_ for token in chunk) == True:
                    #if len(chunk) > 1:
                    noun_phrases.append(chunk)
            #logger.debug(f"Noun phrases: {[chunk.text for chunk in doc.noun_chunks]}")
            logger.info(f"Noun phrases: {noun_phrases}")
            logger.info(f"Verbs: {[token.lemma_ for token in sent if token.pos_ == 'VERB']}")
            #logger.debug(f"All: {[token.lemma_ for token in doc]}")

            # Find named entities, phrases and concepts
            # This is unlikely to be of use
            for entity in sent.ents:
                logger.debug(f'entity: {entity} #entity.text: {entity.text} entity.label_:{entity.label_}')

        for abrv in doc._.abbreviations:
	        logger.warning(f"{abrv} \t ({abrv.start}, {abrv.end}) {abrv._.long_form} {abrv.label_}")


research_df = create_texts()
run_nlp(research_df)