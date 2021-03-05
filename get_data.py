import pandas as pd
import re
import requests

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
    url="https://research-information.bris.ac.uk/en/searchAll/advanced/?searchByRadioGroup=PartOfNameOrTitle&searchBy=PartOfNameOrTitle&allThese=&exactPhrase=ben.elsworth%40bristol.ac.uk&or=&minus=&family=persons&doSearch=Search&slowScroll=true&resultFamilyTabToSelect="
    payload={

    }
    res = requests.get(url,data=payload)
    print(res.text)
    # looking for one of these
    #<a rel="Person" href="https://research-information.bris.ac.uk/en/persons/benjamin-l-elsworth" class="link person"><span>Dr Benjamin L Elsworth</span></a>


#email_df = emails()
uob_finder_web(email='ben.elsworth@bristol.ac.uk')

