import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from simple_parsing import ArgumentParser
from loguru import logger

parser = ArgumentParser()
parser.add_argument("--file", type=str, help="File of starting email addresses")

@dataclass
class Options:
    """ Help string for this group of command-line arguments """
    top: int = -1 # How many to read

parser.add_arguments(Options, dest="options")

args = parser.parse_args()

def read_file():
    person_df = pd.read_csv(args.file,sep='\t')
    return person_df

def create_research_data(person_df):
    data = []
    for i,rows in person_df.iterrows():
        person_data,orcid_data = get_person_data(rows['page'])
        d = {
            'email':rows['email'],
            'job-description':'NA',
            'academic-school-url':'NA',
            'academic-school-name':'NA',
            'sri-url':'NA',
            'sri-name':'NA',
            'orcid':'NA'
        }
        #person_data,orcid_data = get_person_data('https://research-information.bris.ac.uk/en/persons/benjamin-l-elsworth')
        logger.debug(person_data)
        try:
            x = person_data.find(class_="job-description")
            d['job-description']=x.getText()
            logger.debug(x.getText())
        except:
            logger.warning('No job-description')
        try:
            x = person_data.find(class_="link academicschool")
            d['academic-school-url']=x['href']
            d['academic-school-name']=x.getText()
        except:
            logger.warning('No academicschool data')
        try:
            x = person_data[0].find(class_="link sri")
            d['sri-url']=x['href']
            d['sri-name']=x.getText()
        except:
            logger.warning('No sri data')
        try:
            d['orcid']=orcid_data['href']
        except:
            logger.warning('No orcid data')
        data.append(d)
    logger.info(data)
    person_details = pd.DataFrame(data)
    person_details.to_csv('workflow/results/person_data.tsv',sep='\t',index=False)

def get_person_data(url):
    print(url)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    person_data = soup.find("div", class_="rendering rendering_person rendering_personorganisationlistrendererportal rendering_person_personorganisationlistrendererportal")
    orcid_data = soup.find("a",class_="orcid")
    logger.debug(orcid_data)
    return person_data,orcid_data

person_df = read_file()
create_research_data(person_df)