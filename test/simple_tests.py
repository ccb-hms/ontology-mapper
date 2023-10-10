import os
import pandas as pd
import text2term
from term import OntologyTermType
from mapper import Mapper

pd.set_option('display.max_columns', None)


def run_tests():
    efo_url = "https://github.com/EBISPOT/efo/releases/download/v3.57.0/efo.owl"
    pizza = "https://protege.stanford.edu/ontologies/pizza/pizza.owl"
    ncit = "http://purl.obolibrary.org/obo/ncit/releases/2022-08-19/ncit.owl"
    hpo = "http://purl.obolibrary.org/obo/hp/releases/2022-06-11/hp.owl"
    ecto = "http://purl.obolibrary.org/obo/ecto/releases/2022-12-12/ecto.owl"

    # ONTOLOGY CACHING
    # Test caching an ontology loaded from a URL
    print("Test caching an ontology loaded from a URL...")
    efo_cache = text2term.cache_ontology(ontology_url=efo_url, ontology_acronym="EFO")
    print(f"Cache exists: {efo_cache.cache_exists()}\n")

    # Test caching an ontology by resolving its acronym using bioregistry
    print("Test caching an ontology by resolving its acronym using bioregistry...")
    clo_cache = text2term.cache_ontology(ontology_url="CLO", ontology_acronym="CLO")
    print(f"Cache exists: {clo_cache.cache_exists()}\n")
    print()

    # Test caching the set of ontologies specified in resources/ontologies.csv
    caches = text2term.cache_ontology_set(os.path.join("..", "text2term", "resources", "ontologies.csv"))

    # MAPPING TO A (CACHED) ONTOLOGY
    # Test mapping a list of terms to cached EFO ontology
    print("Test mapping a list of terms to cached EFO ontology...")
    mappings_efo_cache = efo_cache.map_terms(["asthma", "disease location", "food allergy"],
                                             term_type=OntologyTermType.ANY)
    print(f"{mappings_efo_cache}\n")

    # Test mapping a list of terms to EFO loaded from a URL
    print("Test mapping a list of terms to EFO loaded from a URL...")
    mappings_efo_url = text2term.map_terms(["asthma", "disease location", "food allergy"], target_ontology=efo_url,
                                           term_type=OntologyTermType.ANY)
    print(f"{mappings_efo_url}\n")

    # Test that mapping to cached ontology is the same as to ontology loaded from its URL
    print("Test that mapping to cached ontology is the same as to ontology loaded from its URL...")
    mappings_match = test_df_equals(drop_source_term_ids(mappings_efo_cache),
                                    drop_source_term_ids(mappings_efo_url))
    print(f"...{mappings_match}")

    # Test mapping a list of terms to cached EFO using Jaro-Winkler syntactic similarity metric
    print("Test mapping a list of terms to cached EFO using Jaro-Winkler syntactic similarity metric...")
    df1 = text2term.map_terms(["asthma", "disease location", "food allergy"], "EFO", min_score=.8,
                              mapper=text2term.Mapper.JARO_WINKLER, excl_deprecated=True, use_cache=True,
                              term_type=OntologyTermType.ANY)
    print(f"{df1}\n")

    # Test mapping a list of terms to EFO by specifying the ontology acronym, which gets resolved by bioregistry
    print("Test mapping a list of terms to EFO by specifying the ontology acronym, which gets resolved by bioregistry")
    df2 = text2term.map_terms(["contains", "asthma"], "EFO", term_type=OntologyTermType.CLASS)
    print(f"{df2}\n")

    # TAGGED TERMS
    # Test mapping a dictionary of tagged terms to cached EFO, and include unmapped terms in the output
    print("Test mapping a dictionary of tagged terms to cached EFO, and include unmapped terms in the output...")
    df3 = text2term.map_terms(
        {"asthma": "disease", "allergy": ["ignore", "response"], "protein level": ["measurement"], "isdjfnsdfwd": None},
        target_ontology="EFO", excl_deprecated=True, use_cache=True, incl_unmapped=True)
    print(f"{df3}\n")

    # Test processing tagged terms where the tags are provided in a file
    print("Test processing tagged terms where the tags are provided in a file...")
    tagged_terms = text2term.preprocess_tagged_terms("simple_preprocess.txt")
    df4 = text2term.map_terms(tagged_terms, target_ontology="EFO", use_cache=True, incl_unmapped=True)
    print(f"{df4}\n")

    # MAPPING TO PROPERTIES
    # Test mapping a list of properties to EFO loaded from a URL and restrict search to properties
    print("Test mapping a list of properties to EFO loaded from a URL and restrict search to properties...")
    df5 = text2term.map_terms(source_terms=["contains", "location"], target_ontology=efo_url,
                              term_type=OntologyTermType.PROPERTY)
    print(f"{df5}\n")

    # Test mapping a list of properties to EFO loaded from cache and restrict search to properties
    print("Test mapping a list of properties to EFO loaded from cache and restrict search to properties...")
    df6 = text2term.map_terms(source_terms=["contains", "location"], target_ontology="EFO", use_cache=True,
                              term_type=OntologyTermType.PROPERTY)
    print(f"{df6}\n")

    # Test that mapping to properties in cached ontology is the same as to ontology loaded from its URL
    properties_df_match = test_df_equals(drop_source_term_ids(df5), drop_source_term_ids(df6))
    print(f"...{properties_df_match}")

    # Test mapping a list of terms to multiple ontologies using the Zooma mapper
    print("Test mapping a list of terms to multiple ontologies using the Zooma mapper...")
    df_zooma = text2term.map_terms(["asthma", "location", "food allergy"], target_ontology="EFO,NCIT",
                                   mapper=Mapper.ZOOMA, term_type=OntologyTermType.ANY)
    print(f"{df_zooma}\n")

    # Test mapping a list of terms to multiple ontologies using the BioPortal Annotator mapper
    print("Test mapping a list of terms to multiple ontologies using the BioPortal Annotator mapper...")
    df_bioportal = text2term.map_terms(["asthma", "location", "food allergy"], target_ontology="EFO,NCIT",
                                       mapper=Mapper.BIOPORTAL, term_type=OntologyTermType.ANY)
    print(f"{df_bioportal}\n")


def drop_source_term_ids(df):
    return df.drop('Source Term ID', axis=1)


def test_df_equals(df, expected_df):
    pd.testing.assert_frame_equal(df, expected_df, check_names=False, check_like=True)
    return True


if __name__ == '__main__':
    run_tests()
