import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from simple_parsing import ArgumentParser
from loguru import logger

parser = ArgumentParser()
parser.add_argument("--file", type=str, help="List of email addresses")

@dataclass
class Options:
    """ Help string for this group of command-line arguments """
    top: int = -1 # How many emails to read

parser.add_arguments(Options, dest="options")

args = parser.parse_args()
logger.debug(args)
logger.debug("options:", args.options.top)

def read_emails():
    df = pd.read_csv(args.file,names=['email'])
    logger.debug(df.head())

    # check for dups
    df.drop_duplicates(inplace=True)

    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@bristol.ac.uk$)") 
    email_check = df['email'].apply(lambda x: True if pattern.match(x) else False)
    bad_emails = df[~email_check]
    bad_emails.to_csv('workflow/results/bad_emails.txt',index=False,header=False)
    #logger.debug(bad_emails)
    logger.debug(f'Removing {bad_emails.shape[0]} bad emails, see them here results/bad_emails.txt')

    df = df[email_check]
    logger.debug(f'Left with {df.shape[0]} emails')

    # use top argument for testing
    if args.options.top:
        logger.debug(f'Keeping top {args.options.top}')
        df = df.head(n=args.options.top) 

    logger.debug(f'Left with {df.shape[0]} emails')
    return df

def uob_finder_web(email):
    logger.debug(f'Searching for {email}')
    #https://research-information.bris.ac.uk/en/searchAll/advanced/?searchByRadioGroup=PartOfNameOrTitle&searchBy=PartOfNameOrTitle&allThese=&exactPhrase=ben.elsworth%40bristol.ac.uk&or=&minus=&family=persons&doSearch=Search&slowScroll=true&resultFamilyTabToSelect=
    url=f"https://research-information.bris.ac.uk/en/searchAll/advanced/?exactPhrase={email}&or=&minus=&family=persons&doSearch=Search&slowScroll=true&resultFamilyTabToSelect="
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    people_data = soup.find_all("li", class_="grid-result-item")
    person_info = False
    for p in people_data:
        find_person = p.find_all("a", class_="link person")
        #logger.debug(p)
        e = p.find("span", text=re.compile(email, re.IGNORECASE))
        if e:
            logger.debug(f'{find_person} {e}')
            person_page = find_person[0]['href']
            # get name
            #m = re.match()
            name = find_person[0].getText()
            logger.debug(person_page)
            person_info={'page':person_page,'name':name,'email':email}
    if person_info == False:
        logger.debug('No page found')
        person_info={'page':'NA','name':'NA','email':email}
    return person_info

def get_all_people(email_df):
    person_data = []
    for i,row in email_df.iterrows():
        person_info = uob_finder_web(email=row['email'])
        person_data.append(person_info)
    person_df = pd.DataFrame(person_data)
    email_df = pd.merge(email_df,person_df,left_on='email',right_on='email')
    logger.debug(email_df.head())
    email_df.to_csv('workflow/results/person_pages.tsv',sep='\t',index=False)

email_df = read_emails()
get_all_people(email_df)