import scispacy
import spacy
import pandas as pd
import os
from simple_parsing import ArgumentParser
from loguru import logger
from workflow.scripts.general import mark_as_complete, load_spacy_model

parser = ArgumentParser()

# from spacy.tokens import Doc

# Doc.set_extension("url", default=None)

parser.add_argument("--input", type=str, help="Input file prefix")
parser.add_argument("--output", type=str, help="Output file prefix")
args = parser.parse_args()

vector_outfile = f"{args.output}_vectors.pkl.gz"
noun_outfile = f"{args.output}_noun_chunks.tsv.gz"

def create_single_text(row):
    text = row["title"]
    if row["abstract"]:
        text = row["title"] + row["abstract"]
    return text


def create_texts():
    # Process whole documents
    research_df = pd.read_csv(f"{args.input}.tsv.gz", sep="\t")
    vector_data = []
    noun_data = []  
    existing_vector_data = []
    # check for existing
    if os.path.exists(vector_outfile) and os.path.getsize(vector_outfile) > 1:
        logger.info(f"Reading existing data {vector_outfile}")
        existing_vector_df = pd.read_pickle(vector_outfile)
        if not existing_vector_df.empty:
            # print(existing_df)
            existing_vector_data = list(existing_vector_df["url"].unique())
            # remove matches
            logger.debug(research_df.shape)
            research_df = research_df[~research_df["url"].isin(existing_vector_data)]
            logger.debug(research_df.shape)
            # logger.debug(existing_data)
            try:
                vector_data = existing_vector_df.to_dict("records")
                existing_noun_df = pd.read_csv(noun_outfile,sep='\t')
                logger.info(existing_noun_df.shape)
                noun_data = existing_noun_df.to_dict("records")
            except:
                logger.warning(f"Error when reading {vector_outfile}")
            logger.debug(f"Got data on {len(existing_vector_data)} urls")
        else:
            logger.debug(f"Existing {vector_outfile} is empty")

    # create single string of text
    # maybe just leave titles and abstract separate if treating each sentence separately
    textList = []
    for i, rows in research_df.iterrows():
        if not type(rows["abstract"]) == float:
            textList.append(f"{rows['title']} {rows['abstract']}")
        else:
            textList.append(rows["title"])
    research_df["text"] = textList
    #logger.debug(research_df.head())
    logger.info(f'Found {len(noun_data)} noun entries')
    logger.info(f'Found {len(vector_data)} vector entries')
    logger.info(f'Parsing data from {research_df.shape[0]} records')
    #research_df=research_df[research_df['url']=='https://research-information.bris.ac.uk/en/publications/long-time-scale-gpu-dynamics-reveal-the-mechanism-of-drug-resista']
    return research_df, noun_data, vector_data


def run_nlp(research_df, noun_data, vector_data):
    if research_df.empty:
        logger.info("No new data")
        mark_as_complete(args.output)
        exit()

    nlp = load_spacy_model()
    # do we need to filter stopwords?
    spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS

    logger.info('Running NLP on docs...')
    text = list(research_df["text"])
    docs = list(nlp.pipe(text))
    logger.info(f'Created {len(docs)} NLP objects')

    for i in range(0, len(docs)):
        doc = docs[i]
        #logger.info(doc)
        df_row = research_df.iloc[i]
        if i % 1000 == 0:
            logger.info(f"{i} {len(docs)}")

        # logger.info(tokens)
        assert doc.has_annotation("SENT_START")
        sent_num = 0
        for sent in doc.sents:
            #logger.info(sent.text)
            words = [token.text for token in sent]
            if len(words)<2:
                logger.info(words)
                continue
            # create vectors
            # print(doc.vector)
            vector_data.append(
                {
                    "url": df_row["url"],
                    "year": df_row["year"],
                    "sent_num": sent_num,
                    "sent_text": sent.text,
                    "vector": list(sent.vector),
                }
            )

            # Analyze syntax
            for chunk in sent.noun_chunks:
                # logger.debug(chunk)
                # remove stopwords and things
                if (
                    all(
                        token.is_stop != True
                        and token.is_punct != True
                        for token in chunk
                    )
                    == True
                ):
                    # not sure if should filter on number of words in chunk?
                    # if len(chunk) > 1:

                    # null string values cause problems with ES, also no need to keep anything less than 3 characters
                    if str(chunk) != 'null' and len(str(chunk))>2:
                        noun_data.append(
                            {
                                "url": df_row["url"], 
                                "year": df_row["year"], 
                                "sent_num": sent_num, 
                                "noun_phrase": chunk
                                }
                        )
            #logger.info(
            #    f"Verbs: {[token.lemma_ for token in sent if token.pos_ == 'VERB']}"
            #)
            # logger.debug(f"All: {[token.lemma_ for token in doc]}")

            # Find named entities, phrases and concepts - can use
            #for entity in sent.ents:
            #    logger.debug(
            #    )
            #        f"entity: {entity} #entity.text: {entity.text} entity.label_:{entity.label_}"
            sent_num += 1

    # logger.info(data)
    df = pd.DataFrame(noun_data)
    df.dropna(inplace=True)
    df.to_csv(noun_outfile, sep="\t", index=False)

    df = pd.DataFrame(vector_data)
    df.dropna(inplace=True)
    logger.info(df.head())
    df.to_pickle(vector_outfile)

    mark_as_complete(args.output)

if __name__ == "__main__":
    research_df, noun_data, vector_data = create_texts()
    run_nlp(research_df, noun_data, vector_data)
