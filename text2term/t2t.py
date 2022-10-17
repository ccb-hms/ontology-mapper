"""Provides Text2Term class"""

import os
import json
import pickle
import time
import datetime
import onto_utils
import pandas as pd
from mapper import Mapper
from term_collector import OntologyTermCollector
from term_graph_generator import TermGraphGenerator
from bioportal_mapper import BioPortalAnnotatorMapper
from syntactic_mapper import SyntacticMapper
from tfidf_mapper import TFIDFMapper
from zooma_mapper import ZoomaMapper
from term_encoder import TermEncoder


class Text2Term:
    """ Main class in text2term package """

    def __init__(self):
        pass

    def map_file(self, input_file, target_ontology, base_iris=(), csv_columns=(), excl_deprecated=False, max_mappings=3,
                 mapper=Mapper.TFIDF, min_score=0.3, output_file='', save_graphs=False, save_mappings=False,
                 separator=','):
        """
        Map the terms in the given input file to the specified target ontology.

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
        source_terms, source_terms_ids = self._load_data(input_file, csv_columns, separator)
        return self.map(source_terms, target_ontology, source_terms_ids=source_terms_ids, base_iris=base_iris,
                        excl_deprecated=excl_deprecated, max_mappings=max_mappings, mapper=mapper, min_score=min_score,
                        output_file=output_file, save_graphs=save_graphs, save_mappings=save_mappings)

    def map(self, source_terms, target_ontology, base_iris=(), excl_deprecated=False, max_mappings=3, min_score=0.3,
            mapper=Mapper.TFIDF, output_file='', save_graphs=False, save_mappings=False, source_terms_ids=()):
        """
        Map the terms in the given list to the specified target ontology.

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
            target_terms = self._load_ontology(target_ontology, base_iris, excl_deprecated)
        mappings_df = self._do_mapping(source_terms, source_terms_ids, target_terms, mapper, max_mappings, min_score)
        if save_mappings:
            self._save_mappings(mappings_df, output_file)
        if save_graphs:
            self._save_graphs(target_terms, output_file)
        return mappings_df

    def cache_ontology_set(self, ontology_registry_path):
        registry = pd.read_csv(ontology_registry_path)
        for index, row in registry.iterrows():
            self.cache_ontology(row.url, row.acronym)

    def cache_ontology(self, ontology_url, ontology_acronym, base_iris=()):
        ontology_terms = self._load_ontology(ontology_url, base_iris, exclude_deprecated=False)
        cache_dir = "cache/" + ontology_acronym + "/"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        self.serialize_ontology_json(ontology_terms, ontology_acronym, cache_dir)

        self.serialize_ontology_pickle(ontology_terms, ontology_acronym, cache_dir)

        self._save_graphs(ontology_terms, output_file=cache_dir + ontology_acronym)
        ontology_terms.clear()

    def serialize_ontology_pickle(self, ontology_terms, ontology_acronym, cache_dir):
        start = time.time()
        with open(cache_dir + ontology_acronym + "-term-details.pickle", 'wb+') as out_file:
            pickle.dump(ontology_terms, out_file)
        end = time.time()
        print("Ontology-Term-Details Pickle serialization time: " + str(end - start))

    def serialize_ontology_json(self, ontology_terms, ontology_acronym, cache_dir):
        start = time.time()
        term_dicts = [t.__dict__ for t in ontology_terms.values()]
        with open(cache_dir + ontology_acronym + "-term-details.json", 'w+') as json_file:
            json.dump(term_dicts, json_file, indent=2, cls=TermEncoder)
        end = time.time()
        print("Ontology-Term-Details JSON serialization time: " + str(end - start))

    def _load_data(self, input_file_path, csv_column_names, separator):
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

    def _load_ontology(self, ontology, iris, exclude_deprecated):
        term_collector = OntologyTermCollector()
        onto_terms = term_collector.get_ontology_terms(ontology, base_iris=iris, exclude_deprecated=exclude_deprecated)
        if len(onto_terms) == 0:
            raise RuntimeError("Could not find any terms in the given ontology.")
        return onto_terms

    def _do_mapping(self, source_terms, source_term_ids, ontology_terms, mapper, max_mappings, min_score):
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

    def _save_mappings(self, mappings, output_file):
        if os.path.dirname(output_file):  # create output directories if needed
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        mappings.to_csv(output_file, index=False)

    def _save_graphs(self, terms, output_file):
        term_graphs = TermGraphGenerator(terms).graphs_dicts()
        with open(output_file + "-term-graphs.json", 'w') as json_file:
            json.dump(term_graphs, json_file, indent=2)
