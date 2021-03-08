import pandas as pd
import re
import requests
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from simple_parsing import ArgumentParser
from loguru import logger

parser = ArgumentParser()
parser.add_argument("--file", type=str, help="File of research metadata")

@dataclass
class Options:
    """ Help string for this group of command-line arguments """
    top: int = -1 # How many to read

parser.add_arguments(Options, dest="options")

args = parser.parse_args()
logger.debug(args)
logger.debug("options:", args.options.top)

def read_file():
    df = pd.read_csv(args.file,sep='\t')
    logger.debug(df.head())
    return df

def create_research_data(df):
    data = []
    existing_data = []
    # check for existing data
    f='workflow/results/research_data.tsv'

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
                'abstract':'NA',
            }
            abstract_data = get_research_data(rows['url'])
            #logger.debug(abstract_data)
            try:
                d['abstract']=abstract_data.getText()
                logger.debug(abstract_data.getText())
            except:
                logger.warning(f"No abstract for {rows['url']}")
        
            data.append(d)
    #logger.debug(data)
    research_details = pd.DataFrame(data)
    research_details.to_csv('workflow/results/research_data.tsv',sep='\t',index=False)
    
    # mark as completed and use this file for snakemake, can then rerun by removing this and keeping data
    f = open('workflow/results/research_data.complete','w')
    f.write('Done')
    f.close()

def get_research_data(url):
    logger.debug(url)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    abstract_data = soup.find("div", class_="rendering rendering_researchoutput rendering_researchoutput_abstractportal rendering_contributiontojournal rendering_abstractportal rendering_contributiontojournal_abstractportal")
    return abstract_data

df = read_file()
create_research_data(df)