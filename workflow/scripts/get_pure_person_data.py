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

    top: int = -1  # How many to read


parser.add_arguments(Options, dest="options")

args = parser.parse_args()


def read_file():
    person_df = pd.read_csv(f"{args.input}.tsv.gz", sep="\t")
    person_df['email'] = person_df['email'].str.lower()
    logger.info(person_df.head())
    return person_df

def create_research_data(person_df):
    data = []
    existing_data = []
    f = f"{args.output}.tsv.gz"
    existing_data = []

    # check for existing
    if os.path.exists(f) and os.path.getsize(f) > 1:
        logger.info(f"Reading existing data {f}")
        existing_df = pd.read_csv(f, sep="\t")
        existing_data = list(existing_df["email"])
        try:
            data = existing_df.to_dict("records")
        except:
            logger.warning(f"Error when reading {f}")
        logger.debug(f"Got data on {len(existing_data)} urls")
        exit()

    for i, rows in person_df.iterrows():
        if rows["email"] in existing_data:
            logger.info(f"{rows['email']} already done")
        else:
            url = rows["page"]
            if not url.startswith('https:'):
                logger.warning(f'Bad URL: {url}')
                continue
            person_data, orcid_data = get_person_data(url)
            d = {
                "email": rows["email"],
                "job-description": "NA",
                "academic-school-url": "NA",
                "academic-school-name": "NA",
                "sri-url": "NA",
                "sri-name": "NA",
                "orcid": "NA",
            }
            # person_data,orcid_data = get_person_data('https://research-information.bris.ac.uk/en/persons/benjamin-l-elsworth')
            logger.debug(person_data)
            try:
                x = person_data.find(class_="job-description")
                d["job-description"] = x.getText()
                logger.debug(x.getText())
            except:
                logger.warning("No job-description")
            try:
                x = person_data.find(class_="link academicschool")
                d["academic-school-url"] = x["href"]
                d["academic-school-name"] = x.getText()
            except:
                logger.warning("No academicschool data")
            try:
                x = person_data[0].find(class_="link sri")
                d["sri-url"] = x["href"]
                d["sri-name"] = x.getText()
            except:
                logger.warning("No sri data")
            try:
                d["orcid"] = orcid_data["href"]
            except:
                logger.warning("No orcid data")
            data.append(d)
    # logger.info(data)
    person_details = pd.DataFrame(data)
    person_details.to_csv(f, sep="\t", index=False)
    mark_as_complete(args.output)


def get_person_data(url):
    logger.debug(url)
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        person_data = soup.find(
            "div",
            class_="rendering rendering_person rendering_personorganisationlistrendererportal rendering_person_personorganisationlistrendererportal",
        )
        orcid_data = soup.find("a", class_="orcid")
        # logger.debug(orcid_data)
    except:
        logger.warning(f"get_person_data failed")
        person_data = orcid_data = "NA"
    return person_data, orcid_data

if __name__ == "__main__":
    person_df = read_file()
    create_research_data(person_df)
