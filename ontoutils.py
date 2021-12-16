import logging
import sys

STOP_WORDS = {'in', 'the', 'any', 'all', 'for', 'and', 'or', 'dx', 'on', 'fh', 'tx', 'only', 'qnorm', 'w', 'iqb',
              'ds', 'rd', 'rdgwas', 'average', 'weekly', 'monthly', 'daily'}


def label_from_iri(iri):
    if "#" in iri:
        return iri.split("#")[1]
    else:
        return iri.rsplit('/', 1)[1]


def get_logger(name, level):
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def parse_list_file(file_path):
    file = open(file_path)
    lines = file.read().splitlines()
    return lines


OBO_BASE_IRI = "http://purl.obolibrary.org/obo/"
BIOPORTAL_BASE_IRI = "http://purl.bioontology.org/ontology/"
ORPHANET_IRI = "http://www.orpha.net/ORDO/"
ONTOLOGY_IRIS = {"EFO": "http://www.ebi.ac.uk/efo/",
                 "Orphanet": ORPHANET_IRI,
                 "ORPHA": ORPHANET_IRI,
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
