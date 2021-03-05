import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

def read_emails():
    df = pd.read_csv('data/email.txt',names=['email'])
    print(df.head())

    # check for dups
    df.drop_duplicates(inplace=True)

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
    people_data = soup.find_all("li", class_="grid-result-item")
    person_page = False
    for p in people_data:
        find_person = p.find_all("a", class_="link person")
        #print(p)
        e = p.find("span", text=re.compile(email, re.IGNORECASE))
        if e:
            #print(find_person,e)
            person_page = find_person[0]['href']
            print(person_page)
    if person_page == False:
        print('No page found')
        return 'NA'
    else:
        return person_page

data_df = read_emails()
person_pages = []
for i,row in data_df.iterrows():
    person_page = uob_finder_web(email=row['email'])
    person_pages.append(person_page)
data_df['person_page']=person_pages
data_df.to_csv('data/person_pages.tsv',sep='\t',index=False)
#person_page = uob_finder_web(email='D.Wilson@bristol.ac.uk')
#print(person_page)
#uob_finder_web(email='ben.elsworth@bristol.ac.uk')
