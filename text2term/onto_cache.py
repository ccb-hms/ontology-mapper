import text2term
from .mapper import Mapper
import os
from shutil import rmtree
import sys

"""
CACHING FUNCTIONS -- Public
"""
# Caches many ontologies from a csv
def cache_ontology_set(ontology_registry_path):
    registry = pd.read_csv(ontology_registry_path)
    cache_set = {}
    for index, row in registry.iterrows():
        try:
            cache = text2term.cache_ontology(row.url, row.acronym)
            cache_set.update({row.acronym : cache})
        except Exception as err:
            sys.stderr.write("Could not cache ontology", row.acronym, "due to error:", err)
        owlready2.default_world.ontologies.clear()
    return cache_set

# Will check if an acronym exists in the cache
def cache_exists(ontology_acronym=''):
    return os.path.exists("cache/" + ontology_acronym)

# Clears the cache
def clear_cache(ontology_acronym=''):
    cache_dir = "cache/" 
    if ontology_acronym != '':
        cache_dir = os.path.join(cache_dir, ontology_acronym)
    # Is equivalent to: rm -r cache_dir
    try:
        rmtree(cache_dir)
        sys.stderr.write("Cache has been cleared successfully\n")
    except OSError as error:
        sys.stderr.write("Cache cannot be removed:")
        sys.stderr.write(error)

## Class that is returned to run
class OntologyCache:
    def __init__(self, ontology_acronym):
        self.acronym = ontology_acronym
        self.ontology = "cache/" + ontology_acronym + "/"

    def map_terms(self, source_terms, base_iris=(), excl_deprecated=False, max_mappings=3, min_score=0.3,
            mapper=Mapper.TFIDF, output_file='', save_graphs=False, save_mappings=False, source_terms_ids=(), 
            term_type='classes'):
        return text2term.map_terms(source_terms, self.acronym, base_iris=base_iris, \
                excl_deprecated=excl_deprecated, max_mappings=max_mappings, min_score=min_score, \
                mapper=mapper, output_file=output_file, save_graphs=save_graphs, \
                save_mappings=save_mappings, source_terms_ids=source_terms_ids, use_cache=True, \
                term_type=term_type)

    def map_tagged_terms(self, tagged_terms_dict, base_iris=(), excl_deprecated=False, max_mappings=3, min_score=0.3,
            mapper=Mapper.TFIDF, output_file='', save_graphs=False, save_mappings=False, source_terms_ids=(),
            term_type='classes'):
        return text2term.map_tagged_terms(tagged_terms_dict, self.acronym, base_iris=base_iris, \
                excl_deprecated=excl_deprecated, max_mappings=max_mappings, min_score=min_score, \
                mapper=mapper, output_file=output_file, save_graphs=save_graphs, \
                save_mappings=save_mappings, source_terms_ids=source_terms_ids, use_cache=True, \
                term_type=term_type)

    def map_file(self, input_file, base_iris=(), csv_columns=(), excl_deprecated=False, max_mappings=3,
             mapper=Mapper.TFIDF, min_score=0.3, output_file='', save_graphs=False, save_mappings=False,
             separator=',', term_type='classes'):
        return text2term.map_file(source_terms, self.acronym, base_iris=base_iris, csv_columns=csv_columns, \
                excl_deprecated=excl_deprecated, max_mappings=max_mappings, min_score=min_score, \
                mapper=mapper, output_file=output_file, save_graphs=save_graphs, separator=separator, \
                save_mappings=save_mappings, source_terms_ids=source_terms_ids, use_cache=True, \
                term_type=term_type)

    def clear_cache(self):
        clear_cache(self.acronym)

    def cache_exists(self):
        return cache_exists(self.acronym)

    def acroynm(self):
        return self.acronym
