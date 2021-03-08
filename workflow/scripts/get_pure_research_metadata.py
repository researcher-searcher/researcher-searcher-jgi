import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from simple_parsing import ArgumentParser

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
    d = []
    for i,rows in person_df.iterrows():
        research_output = get_research_output(rows['page'])
    #research_output = get_research_output('https://research-information.bris.ac.uk/en/persons/benjamin-l-elsworth')
        for r in research_output:
        #logger.debug(i)
            d.append({'email':rows['email'],'url':r['href'],'title':r.getText()})
    #logger.debug(d)
    research_df = pd.DataFrame(d)
    research_df.to_csv('workflow/results/research_meta_data.tsv',sep='\t',index=False)

def get_research_output(url):
    logger.debug(url)
    research_url = f'{url}/publications'
    res = requests.get(research_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    #<a rel="ContributionToJournal" href="https://research-information.bris.ac.uk/en/publications/coffee-consumption-and-risk-of-breast-cancer-a-mendelian-randomiz" class="link"><span>Coffee consumption and risk of breast cancer: a Mendelian Randomization study </span></a>
    research_output = soup.find_all("a", class_="link", rel="ContributionToJournal")
    #logger.debug(research_output)
    return research_output

person_df = read_file()
create_research_data(person_df)