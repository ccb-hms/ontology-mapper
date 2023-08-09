import os
import sys
import json
import pickle
import time
import datetime
import owlready2
import pandas as pd
from text2term import onto_utils
from text2term.mapper import Mapper
from text2term import onto_cache
from text2term.term_collector import OntologyTermCollector
from text2term.term_graph_generator import TermGraphGenerator
from text2term.bioportal_mapper import BioPortalAnnotatorMapper
from text2term.syntactic_mapper import SyntacticMapper
from text2term.tfidf_mapper import TFIDFMapper
from text2term.zooma_mapper import ZoomaMapper
from text2term.config import VERSION
from text2term.tagged_terms import TaggedTerm
from text2term.term_mapping import TermMapping

IGNORE_TAGS = ["ignore", "Ignore", "ignore ", "Ignore "]
UNMAPPED_TAG = "unmapped"

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
def map_terms(source_terms, target_ontology, base_iris=(), csv_columns=(), excl_deprecated=False, max_mappings=3,
        min_score=0.3, mapper=Mapper.TFIDF, output_file='', save_graphs=False, save_mappings=False, source_terms_ids=(), 
        separator=',', use_cache=False, term_type='classes', incl_unmapped=False):
    # Parse the possible source terms options and tags
    source_terms, source_term_ids, tags = _parse_source_terms(source_terms, source_terms_ids, csv_columns, separator)
    # Create Source Term Ids if they are not provided
    if len(source_terms_ids) != len(source_terms):
        if len(source_terms_ids) > 0:
            sys.stderr.write("Warning: Source Term Ids are non-zero, but will not be used.")
        source_terms_ids = onto_utils.generate_iris(len(source_terms))
    # Create the output file
    if output_file == '':
        timestamp = datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")
        output_file = "t2t-mappings-" + timestamp + ".csv"
    # Load the ontology for either Zooma, Bioportal, or directly
    if mapper in {Mapper.ZOOMA, Mapper.BIOPORTAL}:
        target_terms = '' if target_ontology.lower() == 'all' else target_ontology
    else:
        target_terms = _load_ontology(target_ontology, base_iris, excl_deprecated, use_cache, term_type)
    # Run the mapper
    mappings_df = _do_mapping(source_terms, source_terms_ids, target_terms, mapper, max_mappings, min_score, tags, incl_unmapped)
    mappings_df["Mapping Score"] = mappings_df["Mapping Score"].astype(float).round(decimals=3)
    if save_mappings:
        _save_mappings(mappings_df, output_file, min_score, mapper, target_ontology, base_iris, \
                    excl_deprecated, max_mappings, term_type, source_terms, incl_unmapped)
    if save_graphs:
        _save_graphs(target_terms, output_file)
    return mappings_df

# Caches a single ontology
def cache_ontology(ontology_url, ontology_acronym="", base_iris=()):
    if ontology_acronym == "":
        ontology_acronym = ontology_url
    ontology_terms = _load_ontology(ontology_url, base_iris, exclude_deprecated=False, term_type='both')
    cache_dir = "cache/" + ontology_acronym + "/"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    _serialize_ontology(ontology_terms, ontology_acronym, cache_dir)
    _save_graphs(ontology_terms, output_file=cache_dir + ontology_acronym)
    ontology_terms.clear()
    return onto_cache.OntologyCache(ontology_acronym)

"""
PRIVATE/HELPER FUNCTIONS
"""
# Parses the source terms and returns what is to be mapped, the term ids, and the tags
def _parse_source_terms(source_terms, source_terms_ids=(), csv_columns=(), separator=','):
    # If source_terms is a string, we assume it is a file location
    if isinstance(source_terms, str):
        terms, source_terms_ids = _load_data(source_terms, csv_columns, separator)
        tags = dict.fromkeys(terms)
    # If  source_terms is a dictionary, the keys are terms and the values are tags
    elif isinstance(source_terms, dict):
        terms = list(source_terms.keys())
        tags = source_terms
    # Otherwise, it is a list of either TaggedTerms or strings
    elif isinstance(source_terms[0], TaggedTerm):
        terms = []
        source_terms_id_list = []
        for tagged_term in source_terms:
            terms.append(tagged_term.get_term())
            if tagged_term.get_source_term_id() != None:
                source_terms_id_list.append(tagged_term.get_source_term_id())
        source_terms_ids = source_terms_id_list
        tags = source_terms
    else:
        terms = source_terms
        tags = dict.fromkeys(terms)
    return terms, source_terms_ids, tags

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

def _load_ontology(ontology, iris, exclude_deprecated, use_cache=False, term_type='classes'):
    term_collector = OntologyTermCollector()
    if use_cache:
        pickle_file = "cache/" + ontology + "/" + ontology + "-term-details.pickle"
        onto_terms_unfiltered = pickle.load(open(pickle_file, "rb"))
        onto_terms = term_collector.filter_terms(onto_terms_unfiltered, iris, exclude_deprecated, term_type)
    else:

        onto_terms = term_collector.get_ontology_terms(ontology, base_iris=iris, exclude_deprecated=exclude_deprecated, term_type=term_type)
    if len(onto_terms) == 0:
        raise RuntimeError("Could not find any terms in the given ontology.")
    return onto_terms

def _do_mapping(source_terms, source_term_ids, ontology_terms, mapper, max_mappings, min_score, tags, incl_unmapped):
    to_map, tags = _process_tags(source_terms, tags)
    if mapper == Mapper.TFIDF:
        term_mapper = TFIDFMapper(ontology_terms)
        mappings_df = term_mapper.map(to_map, source_term_ids, max_mappings=max_mappings, min_score=min_score)
    elif mapper == Mapper.ZOOMA:
        term_mapper = ZoomaMapper()
        mappings_df = term_mapper.map(to_map, source_term_ids, ontologies=ontology_terms, max_mappings=max_mappings)
    elif mapper == Mapper.BIOPORTAL:
        term_mapper = BioPortalAnnotatorMapper("8f0cbe43-2906-431a-9572-8600d3f4266e")
        mappings_df = term_mapper.map(to_map, source_term_ids, ontologies=ontology_terms, max_mappings=max_mappings)
    elif mapper in {Mapper.LEVENSHTEIN, Mapper.JARO, Mapper.JARO_WINKLER, Mapper.INDEL, Mapper.FUZZY, Mapper.JACCARD}:
        term_mapper = SyntacticMapper(ontology_terms)
        mappings_df = term_mapper.map(to_map, source_term_ids, mapper, max_mappings=max_mappings)
    else:
        raise ValueError("Unsupported mapper: " + mapper)

    # Add tags, process, and filter
    df = _filter_mappings(mappings_df, min_score)
    if incl_unmapped:
        df = _add_unmapped_terms(mappings_df, tags, source_terms, source_term_ids)
    df = _add_tags_to_df(mappings_df, tags)
    return df

# Takes in the tags and source terms and processes them accordingly
def _process_tags(source_terms, tags):
    to_map = []
    # IGNORE TAGS SECTION
    for term in source_terms:
        if isinstance(tags, dict):
            term_tags = tags[term]
        else:
            for tag in tags:
                if tag.get_term() == term:
                    term_tags = tag.get_tags()
                    break
        if isinstance(term_tags, list):
            if not any(tag in IGNORE_TAGS for tag in term_tags):
                to_map.append(term)
        else:
            if term_tags not in IGNORE_TAGS:
                to_map.append(term)
    return to_map, tags

def _add_tags_to_df(df, tags):
    if isinstance(tags, dict):
        for key, value in tags.items():
            if isinstance(value, list):
                to_store = ','.join(value)
            else:
                to_store = str(value)
            df.loc[df['Source Term'] == key, "Tags"] = to_store
    else: 
        for term in tags:
            to_store = ','.join(term.get_tags())
            df.loc[df['Source Term'] == term.get_term(), "Tags"] = to_store
    return df

def _filter_mappings(mappings_df, min_score):
    new_df = pd.DataFrame(columns=mappings_df.columns)
    for index, row in mappings_df.iterrows():
        if row['Mapping Score'] >= min_score:
            new_df.loc[len(new_df.index)] = row
    return new_df

def _add_unmapped_terms(mappings_df, tags, source_terms, source_terms_ids):
    mapped = pd.unique(mappings_df["Source Term"])
    for (term, term_id) in zip(source_terms, source_terms_ids):
        if term not in mapped:
            non_mapping = TermMapping(term, term_id, "", "", 0)
            _add_tag(tags, term, UNMAPPED_TAG, ignore=True)
            mappings_df.loc[len(mappings_df.index)] = non_mapping.to_dict()
    return mappings_df

def _add_tag(tags, term, to_add, ignore=False):
    if isinstance(tags, dict):
        new_tags = tags.get(term, [])
        if new_tags is None:
            new_tags = []
        if not (ignore and any(tag in IGNORE_TAGS for tag in new_tags)):
            if isinstance(new_tags, list):
                new_tags.append(to_add)
            elif new_tags != "":
                new_tags = [new_tags, to_add]
            else:
                new_tags = [to_add]
        tags[term] = new_tags
    else:
        for tagged_term in tags:
            check_ignore = not ignore and not any(tagged_term.has_tag(tag) for tag in IGNORE_TAGS)
            if tagged_term.get_term() == term and check_ignore:
                tagged_term.add_tags([to_add])

def _save_mappings(mappings, output_file, min_score, mapper, target_ontology, base_iris, \
                excl_deprecated, max_mappings, term_type, source_terms, incl_unmapped):
    if os.path.dirname(output_file):  # create output directories if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "a") as f:
        f.write("# Date and time run: %s\n" % datetime.datetime.now())
        f.write("# Target Ontology: %s\n" % target_ontology)
        f.write("# Text2term version: %s\n" % VERSION)
        f.write("# Minimum Score: %.2f\n" % min_score)
        f.write("# Mapper: %s\n" % mapper.value)
        f.write("# Base IRIs: %s\n" % (base_iris,))
        f.write("# Max Mappings: %d\n" % max_mappings)
        f.write("# Term Type: %s\n" % term_type)
        f.write("# Deprecated Terms ")
        f.write("Excluded\n" if excl_deprecated else "Included\n")
        f.write("# Unmapped Terms ")
        f.write("Excluded\n" if not incl_unmapped else "Included\n")
        writestring = "# Of " + str(len(source_terms)) + " entries, " + str(len(pd.unique(mappings["Source Term ID"])))
        writestring += " were successfully mapped to " + str(len(pd.unique(mappings["Mapped Term IRI"]))) + " unique terms\n"
        f.write(writestring)
    mappings.to_csv(output_file, index=False, mode='a')

def _save_graphs(terms, output_file):
    term_graphs = TermGraphGenerator(terms).graphs_dicts()
    with open(output_file + "-term-graphs.json", 'w') as json_file:
        json.dump(term_graphs, json_file, indent=2)
