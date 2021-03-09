import pandas as pd
import re
import requests
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from simple_parsing import ArgumentParser
from loguru import logger

parser = ArgumentParser()
parser.add_argument("--file", type=str, help="File of people")

@dataclass
class Options:
    """ Help string for this group of command-line arguments """
    top: int = -1 # How many to read

parser.add_arguments(Options, dest="options")

args = parser.parse_args()
logger.debug(args)
logger.debug("options:", args.options.top)

def read_file():
    person_df = pd.read_csv(args.file,sep='\t')
    logger.debug(person_df.head())
    return person_df

def create_research_data(person_df):
    data = []
    existing_data = []
    # check for existing data
    f='workflow/results/research_meta_data.tsv'

    if os.path.exists(f) and os.path.getsize(f) > 1:
        logger.info(f'Reading existing data {f}')
        existing_df = pd.read_csv(f,sep='\t')
        #print(existing_df)
        existing_data = list(existing_df['email'].unique())
        #logger.debug(existing_data)
        try:
            data = existing_df.to_dict('records')
        except:
            logger.warning(f'Error when reading {f}')
        logger.debug(f'Got data on {len(existing_data)} emails')

    for i,rows in person_df.iterrows():
        if rows['email'] in existing_data:
            logger.debug(f"{rows['email']} already done")
        else:
            research_output = get_research_output(rows['page'])
        #research_output = get_research_output('https://research-information.bris.ac.uk/en/persons/benjamin-l-elsworth')
            for r in research_output:
            #logger.debug(i)
                data.append({'email':rows['email'],'url':r['href'],'title':r.getText()})
    #logger.debug(d)
    research_df = pd.DataFrame(data)
    research_df.to_csv(f,sep='\t',index=False)

    # mark as completed and use this file for snakemake, can then rerun by removing this and keeping data
    f = open('workflow/results/research_metadata.complete','w')
    f.write('Done')
    f.close()

def get_research_output(url):
    logger.debug(url)
    try:
        research_url = f'{url}/publications'
        res = requests.get(research_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        #<a rel="ContributionToJournal" href="https://research-information.bris.ac.uk/en/publications/coffee-consumption-and-risk-of-breast-cancer-a-mendelian-randomiz" class="link"><span>Coffee consumption and risk of breast cancer: a Mendelian Randomization study </span></a>
        research_output = soup.find_all("a", class_="link", rel="ContributionToJournal")
    except:
        logger.warning('get_research_output failed')
        research_output = []
    #logger.debug(research_output)
    return research_output

person_df = read_file()
create_research_data(person_df)