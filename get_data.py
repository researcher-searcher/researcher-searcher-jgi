import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

def read_emails():
    df = pd.read_csv('data/email.txt',names=['email'])
    print(df.head())

    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@bristol.ac.uk$)") 
    email_check = df['email'].apply(lambda x: True if pattern.match(x) else False)
    bad_emails = df[~email_check]
    print(bad_emails)
    print(f'Removing {bad_emails.shape[0]} bad emails')

    df = df[email_check]
    print(f'Left with {df.shape[0]} emails')
    return df

def uob_finder_web(email):
    print(f'Searching for {email}')
    #https://research-information.bris.ac.uk/en/searchAll/advanced/?searchByRadioGroup=PartOfNameOrTitle&searchBy=PartOfNameOrTitle&allThese=&exactPhrase=ben.elsworth%40bristol.ac.uk&or=&minus=&family=persons&doSearch=Search&slowScroll=true&resultFamilyTabToSelect=
    url=f"https://research-information.bris.ac.uk/en/searchAll/advanced/?exactPhrase={email}&or=&minus=&family=persons&doSearch=Search&slowScroll=true&resultFamilyTabToSelect="
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    find_person = soup.find_all("a", class_="link person")
    print(len(find_person))
    if len(find_person)==1:
        print(find_person)
    else:
        print(f'Error, more than one person {len(find_person)} \n{find_person}')

email_df = read_emails()
for i,row in email_df.head().iterrows():
    uob_finder_web(email=row['email'])

