import requests
from bs4 import BeautifulSoup
import json
from unicodedata import normalize
import pandas as pd
import json
from datetime import datetime

def extract_nom_jsonld(nom_url):
    r = requests.get(nom_url)
    soup = BeautifulSoup(r.text,'lxml')
    json_ld_text = soup.find('script', {'type':'application/ld+json'}).text
    json_ld = json.loads(json_ld_text)
    
    subset = {}
    subset['id'] = json_ld['@id']
    #definition
    if 'skos:definition' in json_ld:
        if isinstance(json_ld['skos:definition'],list):
            for definition in json_ld['skos:definition']:
                if definition['@language'] == 'en':
                    subset['definition'] = definition['@value']
        elif isinstance(json_ld['skos:definition'],dict):
            definition = json_ld['skos:definition']
            if definition['@language'] == 'en':
                subset['definition'] = definition['@value']
        subset['definition'] = normalize("NFKD",subset['definition']).replace('\n',' ')
    #term
    if 'skos:prefLabel' in json_ld:
        if isinstance(json_ld['skos:prefLabel'],list):
            for label in json_ld['skos:prefLabel']:
                if label['@language'] == 'en':
                    subset['term'] = label['@value']
        elif isinstance(json_ld['skos:prefLabel'],dict):
            label = json_ld['skos:prefLabel']
            if label['@language'] == 'en':
                    subset['term'] = label['@value']
        subset['term'] = normalize("NFKD",subset['term']).replace('\n',' ')
    #children
    if 'skos:narrower' in json_ld:
        children = []
        for child in json_ld['skos:narrower']:
            children.append(child['@id'])
        subset['children'] = children
    #parent
    if 'skos:broader' in json_ld:
        subset['parent'] = json_ld['skos:broader'][0]['@id']
    return json_ld, subset

ids_to_grab = ['http://nomenclature.info/nom/2',
               'http://nomenclature.info/nom/967',
               'http://nomenclature.info/nom/1934',
               'http://nomenclature.info/nom/3176',
               'http://nomenclature.info/nom/7685',
               'http://nomenclature.info/nom/10378',
               'http://nomenclature.info/nom/11633',
               'http://nomenclature.info/nom/12838',
               'http://nomenclature.info/nom/14135',
               'http://nomenclature.info/nom/14897']

subset_results = []
all_results = []

while len(ids_to_grab) > 0:
    nom_id = ids_to_grab.pop()
    full_json, ld_dict = extract_nom_jsonld(nom_id)
    all_results.append(full_json)
    if 'children' in ld_dict:
        for child in ld_dict['children']:
            ids_to_grab.append(child)
    nom_result = {k: ld_dict.get(k, None) for k in ('id','definition','parent','term')}
    subset_results.append(nom_result)

    if len(subset_results) % 100 == 0:
        dt_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(dt_string, len(subset_results))

nom_df = pd.DataFrame(subset_results)
nom_df.to_csv('nomenclature_subset.tsv', sep='\t', index=False)

with open('nomenclature_all.json','w') as json_out:
    json.dump(all_results, json_out)