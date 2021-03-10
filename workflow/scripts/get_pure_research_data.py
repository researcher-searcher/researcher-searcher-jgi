import pandas as pd
import re
import requests
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from simple_parsing import ArgumentParser
from loguru import logger
from workflow.scripts.general import mark_as_complete

parser = ArgumentParser()
parser.add_argument("--input", type=str, help="Input file prefix")
parser.add_argument("--output", type=str, help="Output file prefix")
@dataclass
class Options:
    """ Help string for this group of command-line arguments """
    top: int = -1 # How many to read

parser.add_arguments(Options, dest="options")

args = parser.parse_args()

def read_file():
    df = pd.read_csv(f'{args.input}.tsv.gz',sep='\t')
    df.drop_duplicates(subset='url',inplace=True)
    logger.debug(df.head())
    return df

def create_research_data(df):
    data = []
    existing_data = []
    # check for existing data
    f=f'{args.output}.tsv.gz'

    if os.path.exists(f) and os.path.getsize(f) > 1:
        logger.info(f'Reading existing data {f}')
        existing_df = pd.read_csv(f,sep='\t')
        #print(existing_df)
        existing_data = list(existing_df['url'])
        #logger.debug(existing_data)
        try:
            data = existing_df.to_dict('records')
        except:
            logger.warning(f'Error when reading {f}')
        logger.debug(f'Got data on {len(existing_data)} urls')

    for i,rows in df.iterrows():
        if rows['url'] in existing_data:
            logger.debug(f"{rows['url']} already done")
        else:
            d = {
                'url':rows['url'],
                'title':rows['title'],
                'abstract':'NA',
            }
            abstract_data = get_research_data(rows['url'])
            #logger.debug(abstract_data)
            try:
                d['abstract']=abstract_data.getText().strip().replace('\n',' ')
                logger.debug(abstract_data.getText())
            except:
                logger.warning(f"No abstract for {rows['url']}")
        
            data.append(d)
    #logger.debug(data)
    research_details = pd.DataFrame(data)
    research_details.to_csv(f,sep='\t',index=False)
    mark_as_complete(args.output)

def get_research_data(url):
    logger.debug(url)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    abstract_data = soup.find("div", class_="rendering rendering_researchoutput rendering_researchoutput_abstractportal rendering_contributiontojournal rendering_abstractportal rendering_contributiontojournal_abstractportal")
    return abstract_data

df = read_file()
create_research_data(df)