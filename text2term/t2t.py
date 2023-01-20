"""Provides Text2Term class"""

import os
import sys
import json
import pickle
import time
import datetime
import owlready2
import pandas as pd
from shutil import rmtree
from text2term import onto_utils
from text2term.mapper import Mapper
from text2term.term_collector import OntologyTermCollector
from text2term.term_graph_generator import TermGraphGenerator
from text2term.bioportal_mapper import BioPortalAnnotatorMapper
from text2term.syntactic_mapper import SyntacticMapper
from text2term.tfidf_mapper import TFIDFMapper
from text2term.zooma_mapper import ZoomaMapper

def map_file(input_file, target_ontology, base_iris=(), csv_columns=(), excl_deprecated=False, max_mappings=3,
             mapper=Mapper.TFIDF, min_score=0.3, output_file='', save_graphs=False, save_mappings=False,
             separator=',', use_cache=False):
    """
    Maps the terms in the given input file to the specified target ontology.

    Parameters
    ----------
    input_file : str
        Path to input file containing 'source' terms to map to ontology terms (list of terms or CSV file)
    target_ontology : str
        Path or URL of 'target' ontology to map the source terms to. When the chosen mapper is BioPortal or Zooma,
        provide a comma-separated list of ontology acronyms (eg 'EFO,HPO') or write 'all' to search all ontologies
    base_iris : tuple
        Map only to ontology terms whose IRIs start with one of the strings given in this tuple, for example:
        ('http://www.ebi.ac.uk/efo','http://purl.obolibrary.org/obo/HP')
    csv_columns : tuple
        Name of the column that contains the terms to map, optionally followed by the name of the column that
        contains identifiers for the terms (eg 'my_terms,my_term_ids')
    separator : str
        Specifies the cell separator to be used when reading a non-comma-separated tabular file
    excl_deprecated : bool
        Exclude ontology terms stated as deprecated via `owl:deprecated true`
    mapper : mapper.Mapper
        Method used to compare source terms with ontology terms. One of: levenshtein, jaro, jarowinkler, jaccard,
        fuzzy, tfidf, zooma, bioportal
    max_mappings : int
        Maximum number of top-ranked mappings returned per source term
    min_score : float
        Minimum similarity score [0,1] for the mappings (1=exact match)
    output_file : str
        Path to desired output file for the mappings
    save_graphs : bool
        Save vis.js graphs representing the neighborhood of each ontology term
    save_mappings : bool
        Save the generated mappings to a file (specified by `output_file`)

    Returns
    ----------
    df
        Data frame containing the generated ontology mappings
    """
    source_terms, source_terms_ids = _load_data(input_file, csv_columns, separator)
    return map_terms(source_terms, target_ontology, source_terms_ids=source_terms_ids, base_iris=base_iris,
                    excl_deprecated=excl_deprecated, max_mappings=max_mappings, mapper=mapper, min_score=min_score,
                    output_file=output_file, save_graphs=save_graphs, save_mappings=save_mappings, use_cache=use_cache)

def map_terms(source_terms, target_ontology, base_iris=(), excl_deprecated=False, max_mappings=3, min_score=0.3,
        mapper=Mapper.TFIDF, output_file='', save_graphs=False, save_mappings=False, source_terms_ids=(), use_cache=False):
    """
    Maps the terms in the given list to the specified target ontology.

    Parameters
    ----------
    source_terms : list
        List of 'source' terms to map to ontology terms
    target_ontology : str
        Path or URL of 'target' ontology to map the source terms to. When the chosen mapper is BioPortal or Zooma,
        provide a comma-separated list of ontology acronyms (eg 'EFO,HPO') or write 'all' to search all ontologies
    base_iris : tuple
        Map only to ontology terms whose IRIs start with one of the strings given in this tuple, for example:
        ('http://www.ebi.ac.uk/efo','http://purl.obolibrary.org/obo/HP')
    source_terms_ids : tuple
        Collection of identifiers for the given source terms
    excl_deprecated : bool
        Exclude ontology terms stated as deprecated via `owl:deprecated true`
    mapper : mapper.Mapper
        Method used to compare source terms with ontology terms. One of: levenshtein, jaro, jarowinkler, jaccard,
        fuzzy, tfidf, zooma, bioportal
    max_mappings : int
        Maximum number of top-ranked mappings returned per source term
    min_score : float
        Minimum similarity score [0,1] for the mappings (1=exact match)
    output_file : str
        Path to desired output file for the mappings
    save_graphs : bool
        Save vis.js graphs representing the neighborhood of each ontology term
    save_mappings : bool
        Save the generated mappings to a file (specified by `output_file`)

    Returns
    ----------
    df
        Data frame containing the generated ontology mappings
    """
    if len(source_terms_ids) != len(source_terms):
        source_terms_ids = onto_utils.generate_iris(len(source_terms))
    if output_file == '':
        timestamp = datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")
        output_file = "t2t-mappings-" + timestamp + ".csv"
    if mapper in {Mapper.ZOOMA, Mapper.BIOPORTAL}:
        target_terms = '' if target_ontology.lower() == 'all' else target_ontology
    else:
        target_terms = _load_ontology(target_ontology, base_iris, excl_deprecated, use_cache)
    mappings_df = _do_mapping(source_terms, source_terms_ids, target_terms, mapper, max_mappings, min_score)
    if save_mappings:
        _save_mappings(mappings_df, output_file)
    if save_graphs:
        _save_graphs(target_terms, output_file)
    return mappings_df

"""
CACHING FUNCTIONS -- Public
"""
# Caches many ontologies from a csv
def cache_ontology_set(ontology_registry_path):
    registry = pd.read_csv(ontology_registry_path)
    for index, row in registry.iterrows():
        try:
            cache_ontology(row.url, row.acronym)
        except Exception as err:
            sys.stderr.write("Could not cache ontology", row.acronym, "due to error:", err)
        owlready2.default_world.ontologies.clear()

# Caches a single ontology
def cache_ontology(ontology_url, ontology_acronym, base_iris=()):
    ontology_terms = _load_ontology(ontology_url, base_iris, exclude_deprecated=False)
    cache_dir = "cache/" + ontology_acronym + "/"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    _serialize_ontology(ontology_terms, ontology_acronym, cache_dir)
    _save_graphs(ontology_terms, output_file=cache_dir + ontology_acronym)
    ontology_terms.clear()

# Will check if an acronym exists in the cache
def cache_exists(ontology_acronym):
    return os.path.exists("cache/" + ontology_acronym)

# Clears the cache
def clear_cache(ontology_acronym=''):
    cache_dir = "cache/" 
    if ontology_acronym != '':
        cache_dir = os.path.join(cache_dir, ontology_acronym)
    # Is equivalent to: rm -r cache_dir
    try:
        rmtree(cache_dir)
        sys.stderr.write("Cache has been cleared successfully")
    except OSError as error:
        sys.stderr.write("Cache cannot be removed:")
        sys.stderr.write(error)

"""
PRIVATE/HELPER FUNCTIONS
"""
def _serialize_ontology(ontology_terms, ontology_acronym, cache_dir):
    start = time.time()
    with open(cache_dir + ontology_acronym + "-term-details.pickle", 'wb+') as out_file:
        pickle.dump(ontology_terms, out_file)
    end = time.time()

def _load_data(input_file_path, csv_column_names, separator):
    if len(csv_column_names) >= 1:
        term_id_col_name = ""
        if len(csv_column_names) == 2:
            term_id_col_name = csv_column_names[1]
        terms, term_ids = onto_utils.parse_csv_file(input_file_path, separator=separator,
                                                    term_column_name=csv_column_names[0],
                                                    term_id_column_name=term_id_col_name)
    else:
        terms = onto_utils.parse_list_file(input_file_path)
        term_ids = onto_utils.generate_iris(len(terms))
    return terms, term_ids

def _load_ontology(ontology, iris, exclude_deprecated, use_cache=False):
    term_collector = OntologyTermCollector()
    if use_cache:
        pickle_file = "cache/" + ontology + "/" + ontology + "-term-details.pickle"
        onto_terms_unfiltered = pickle.load(open(pickle_file, "rb"))
        onto_terms = term_collector.filter_terms(onto_terms_unfiltered, iris, exclude_deprecated)
    else:
        onto_terms = term_collector.get_ontology_terms(ontology, base_iris=iris, exclude_deprecated=exclude_deprecated)
    if len(onto_terms) == 0:
        raise RuntimeError("Could not find any terms in the given ontology.")
    return onto_terms

def _do_mapping(source_terms, source_term_ids, ontology_terms, mapper, max_mappings, min_score):
    if mapper == Mapper.TFIDF:
        term_mapper = TFIDFMapper(ontology_terms)
        return term_mapper.map(source_terms, source_term_ids, max_mappings=max_mappings, min_score=min_score)
    elif mapper == Mapper.ZOOMA:
        term_mapper = ZoomaMapper()
        return term_mapper.map(source_terms, source_term_ids, ontologies=ontology_terms, max_mappings=max_mappings)
    elif mapper == Mapper.BIOPORTAL:
        term_mapper = BioPortalAnnotatorMapper("8f0cbe43-2906-431a-9572-8600d3f4266e")
        return term_mapper.map(source_terms, source_term_ids, ontologies=ontology_terms, max_mappings=max_mappings)
    elif mapper in {Mapper.LEVENSHTEIN, Mapper.JARO, Mapper.JARO_WINKLER, Mapper.INDEL, Mapper.FUZZY, Mapper.JACCARD}:
        term_mapper = SyntacticMapper(ontology_terms)
        return term_mapper.map(source_terms, source_term_ids, mapper, max_mappings=max_mappings)
    else:
        raise ValueError("Unsupported mapper: " + mapper)

def _save_mappings(mappings, output_file):
    if os.path.dirname(output_file):  # create output directories if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    mappings.to_csv(output_file, index=False)

def _save_graphs(terms, output_file):
    term_graphs = TermGraphGenerator(terms).graphs_dicts()
    with open(output_file + "-term-graphs.json", 'w') as json_file:
        json.dump(term_graphs, json_file, indent=2)
