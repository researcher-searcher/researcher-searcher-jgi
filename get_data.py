import pandas as pd
import re

df = pd.read_csv('data/email.txt',names=['email'])
print(df.head())

pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@bristol.ac.uk$)") 
email_check = df['email'].apply(lambda x: True if pattern.match(x) else False)
print(email_check.value_counts())
print(df.head())
