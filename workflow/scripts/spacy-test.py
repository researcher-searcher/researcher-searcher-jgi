import scispacy
import spacy

# Load English tokenizer, tagger, parser and NER
nlp = spacy.load("en_core_web_lg")
#nlp = spacy.load("en_core_sci_scibert")

# Process whole documents
text = ("When Sebastian Thrun started working on self-driving cars at "
        "Google in 2007, few people outside of the company took him "
        "seriously. “I can tell you very senior CEOs of major American "
        "car companies would shake my hand and turn away because I wasn’t "
        "worth talking to,” said Thrun, in an interview with Recode earlier "
        "this week.")
text = """
We investigate parents’ preferences for school attributes in a unique dataset 
of survey, administrative, census and spatial data. Using a conditional 
logit, incorporating characteristics of households, schools, and home-school 
distance, we show that most families have strong preferences for schools’ 
academic performance. Parents also value schools’ socio-economic composition 
and distance, which may limit the potential of school choice to improve 
academic standards. Most of the variation in preferences for school quality 
across socio-economic groups arises from differences in the quality of 
accessible schools rather than differences in parents’ preferences, although 
more advantaged parents have stronger preferences for academic performance.
""".replace("\n"," ")

text="""
Motivation
The wealth of data resources on human phenotypes, risk factors, molecular traits and therapeutic interventions presents new opportunities for population health sciences. These opportunities are paralleled by a growing need for data integration, curation and mining to increase research efficiency, reduce mis-inference and ensure reproducible research.

Results
We developed EpiGraphDB (https://epigraphdb.org/), a graph database containing an array of different biomedical and epidemiological relationships and an analytical platform to support their use in human population health data science. In addition, we present three case studies that illustrate the value of this platform. The first uses EpiGraphDB to evaluate potential pleiotropic relationships, addressing mis-inference in systematic causal analysis. In the second case study, we illustrate how protein–protein interaction data offer opportunities to identify new drug targets. The final case study integrates causal inference using Mendelian randomization with relationships mined from the biomedical literature to ‘triangulate’ evidence from different sources.

Availability and implementation
The EpiGraphDB platform is openly available at https://epigraphdb.org. Code for replicating case study results is available at https://github.com/MRCIEU/epigraphdb as Jupyter notebooks using the API, and https://mrcieu.github.io/epigraphdb-r using the R package.
"""

doc = nlp(text)

# Analyze syntax
print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

# Find named entities, phrases and concepts
for entity in doc.ents:
    print(entity.text, entity.label_)