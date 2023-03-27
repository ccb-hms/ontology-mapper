import logging
import re
import sys
import pandas as pd
import bioregistry
import shortuuid
from owlready2 import *
from gensim.parsing import strip_non_alphanum, strip_multiple_whitespaces


BASE_IRI = "http://ccb.hms.harvard.edu/t2t/"

STOP_WORDS = {'in', 'the', 'any', 'all', 'for', 'and', 'or', 'dx', 'on', 'fh', 'tx', 'only', 'qnorm', 'w', 'iqb', 's',
              'ds', 'rd', 'rdgwas', 'ICD', 'excluded', 'excluding', 'unspecified', 'certain', 'also', 'undefined',
              'ordinary', 'least', 'squares', 'FINNGEN', 'elsewhere', 'more', 'excluded', 'classified', 'classifeid',
              'unspcified', 'unspesified', 'specified', 'acquired', 'combined', 'unspeficied', 'elsewhere', 'not', 'by',
              'strict', 'wide', 'definition', 'definitions', 'confirmed', 'chapter', 'chapters', 'controls',
              'characterized', 'main', 'diagnosis', 'hospital', 'admissions', 'other', 'resulting', 'from'}

TEMPORAL_WORDS = {'age', 'time', 'times', 'date', 'initiation', 'cessation', 'progression', 'duration', 'early', 'late',
                  'later', 'trimester'}

QUANTITY_WORDS = {'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'frequently', 'per', 'hour', 'day', 'week', 'month',
                  'year', 'years', 'total', 'quantity', 'amount', 'level', 'levels', 'volume', 'count', 'counts', 'percentage',
                  'abundance', 'proportion', 'content', 'average', 'prevalence', 'mean', 'ratio'}


def normalize_list(token_list):
    normalized_token_list = []
    for token in token_list:
        normalized_token_list.append(normalize(token))
    return normalized_token_list


def normalize(token):
    """
    Normalizes a given string by converting to lower case, removing non-word characters, stop words, white space
    :param token: Text to be normalized
    :return: Normalized string
    """
    token = strip_non_alphanum(token).lower()
    token = token.replace("_", " ")
    token = " ".join(w for w in token.split() if w not in STOP_WORDS)
    token = strip_multiple_whitespaces(token)
    return token


def remove_quotes(string):
    string = string.replace("\"", "")
    string = string.replace("\'", "")
    return string


def remove_whitespace(string):
    return string.replace(' ', '')


def curie_from_iri(iri):
    curie = bioregistry.curie_from_iri(iri)
    if curie is None:
        sys.stderr.write("Error obtaining CURIE for IRI: " + iri)
        return ""
    else:
        return curie.upper()


def label_from_iri(iri):
    if "#" in iri:
        return iri.split("#")[1]
    else:
        return iri.rsplit('/', 1)[1]


def iri_from_tag(source_tag):
    iri = source_tag
    if len(source_tag) > 0 and source_tag != "NA":
        iri = remove_whitespace(iri)
        if ":" in source_tag:
            onto_name = iri.split(":")[0]
            term_name = iri.replace(":", "_")
            full_iri = _get_iri(onto_name, term_name)
            iri = full_iri if len(full_iri) > 0 else iri
        elif "_" in source_tag:
            onto_name = iri.split("_")[0]
            full_iri = _get_iri(onto_name, iri)
            iri = full_iri if len(full_iri) > 0 else iri
    return iri


def _get_iri(ont_name, term_name):
    iri = ''
    if ont_name in ONTOLOGY_IRIS:
        if ont_name == 'ORPHA':
            iri = ONTOLOGY_IRIS.get(ont_name) + term_name.replace('ORPHA_', 'Orphanet_')
        elif ont_name == 'SNOMED' or ont_name == 'OMIM':
            iri = ONTOLOGY_IRIS.get(ont_name) + term_name.replace(ont_name + '_', '')
        else:
            iri = ONTOLOGY_IRIS.get(ont_name) + term_name
    return iri


def get_logger(name, level=logging.INFO):
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
    logger.propagate = False
    return logger


def parse_list_file(file_path):
    file = open(file_path)
    lines = file.read().splitlines()
    file.close()
    return lines


def parse_csv_file(file_path, term_column_name, term_id_column_name, separator=','):
    data = pd.read_csv(file_path, sep=separator, engine='python')
    data = data.dropna(subset=[term_column_name, term_id_column_name])
    if term_column_name not in data.columns:
        raise ValueError("Could not find specified column name for input terms: " + term_column_name)
    terms = data[term_column_name].values
    if term_id_column_name not in data.columns:
        term_ids = generate_iris(len(terms))
    elif data[term_id_column_name].isnull().values.all():
        term_ids = generate_iris(len(terms))
    else:
        term_ids = data[term_id_column_name].values
    return terms, term_ids


def parse_tsv_file(file_path, term_column_name, term_id_column_name):
    return parse_csv_file(file_path, term_column_name, term_id_column_name, separator="\t")


def get_ontology_from_labels(term_labels):
    onto_iri = BASE_IRI + "Ontology-" + generate_uuid()
    onto = owlready2.get_ontology(onto_iri)
    onto.metadata.comment.append("Created dynamically using text2term")
    onto.metadata.comment.append(datetime.datetime.now())
    for term_label in term_labels:
        with onto:
            new_term_iri = generate_iri()
            new_term = types.new_class(new_term_iri, (Thing,))
            new_term.label = term_label
    return onto


def generate_uuid():
    return str(shortuuid.ShortUUID().random(length=10))


def generate_iri():
    return BASE_IRI + "R" + generate_uuid()


def generate_iris(quantity):
    return [generate_iri() for _ in range(quantity)]


OBO_BASE_IRI = "http://purl.obolibrary.org/obo/"
BIOPORTAL_BASE_IRI = "http://purl.bioontology.org/ontology/"
ORPHANET_IRI = "http://www.orpha.net/ORDO/"
ONTOLOGY_IRIS = {"EFO": "http://www.ebi.ac.uk/efo/",
                 "Orphanet": ORPHANET_IRI,
                 "ORPHA": ORPHANET_IRI,
                 "CL": OBO_BASE_IRI,
                 "MONDO": OBO_BASE_IRI,
                 "HP": OBO_BASE_IRI,
                 "UBERON": OBO_BASE_IRI,
                 "GO": OBO_BASE_IRI,
                 "DOID": OBO_BASE_IRI,
                 "CHEBI": OBO_BASE_IRI,
                 "OMIT": OBO_BASE_IRI,
                 "NCIT": OBO_BASE_IRI,
                 "MAXO": OBO_BASE_IRI,
                 "DRON": OBO_BASE_IRI,
                 "OAE": OBO_BASE_IRI,
                 "CIDO": OBO_BASE_IRI,
                 "OMIM": BIOPORTAL_BASE_IRI + "OMIM/",
                 "PATO": OBO_BASE_IRI,
                 "SNOMED": "http://snomed.info/id/"}
