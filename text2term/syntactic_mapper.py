"""Provides SyntacticMapper class"""

import logging
import time
import nltk
import rapidfuzz
from tqdm import tqdm
from text2term import onto_utils
from text2term.mapper import Mapper
from text2term.term_mapping import TermMapping, TermMappingCollection


class SyntacticMapper:

    def __init__(self, target_ontology_terms):
        """
        :param target_ontology_terms: Collection of ontology terms to be mapped against
        """
        self.logger = onto_utils.get_logger(__name__, logging.INFO)
        self.target_ontology_terms = target_ontology_terms

    def map(self, source_terms, source_terms_ids, mapper=Mapper.JARO_WINKLER, max_mappings=3):
        """
        :param source_terms: List of source terms to be mapped with ontology terms
        :param source_terms_ids: List of identifiers for the given source terms
        :param mapper: Mapping method to be used for matching
        :param max_mappings: Maximum number of (top scoring) ontology term mappings that should be returned
        """
        self.logger.info("Mapping %i source terms...", len(source_terms))
        start = time.time()
        mappings = []
        for term, term_id in tqdm(zip(source_terms, source_terms_ids), total=len(source_terms)):
            matches = self._map(term, term_id, mapper, max_mappings)
            mappings.extend(matches)
        end = time.time()
        self.logger.info('done (mapping time: %.2fs seconds)', end - start)
        return TermMappingCollection(mappings).mappings_df()

    def _map(self, source_term, source_term_id, mapper, max_matches=3):
        self.logger.debug("Matching %s...", source_term)
        term_matches = []
        for term in self.target_ontology_terms.values():
            highest_similarity = 0.0
            for target_name in self._term_names(term):
                similarity = self.compare(source_term, target_name, mapper)
                self.logger.debug("%s -> %s (%.2f)", source_term, target_name, similarity)
                if similarity > highest_similarity:
                    highest_similarity = similarity
            term_matches.append(TermMapping(source_term, source_term_id, term.label, term.iri, highest_similarity))
        matches_sorted = sorted(term_matches, key=lambda x: x.mapping_score, reverse=True)
        del matches_sorted[max_matches:]
        return matches_sorted

    def _term_names(self, ontology_term):
        lbls_syns = []
        lbls_syns.extend(ontology_term.labels)
        lbls_syns.extend(ontology_term.synonyms)
        return lbls_syns

    def compare(self, s1, s2, mapper):
        """
        Compare the given strings s1 and s2 with respect to the specified mapping method
        :param s1: source string
        :param s2: target string
        :param mapper: Mapping method to be used
        """
        if mapper == Mapper.LEVENSHTEIN:
            return self.compare_levenshtein(s1, s2)
        elif mapper == Mapper.JARO:
            return self.compare_jaro(s1, s2)
        elif mapper == Mapper.JARO_WINKLER:
            return self.compare_jarowinkler(s1, s2)
        elif mapper == Mapper.INDEL:
            return self.compare_indel(s1, s2)
        elif mapper == Mapper.FUZZY:
            return self.compare_fuzzy_ratio(s1, s2)
        elif mapper == Mapper.JACCARD:
            return self.compare_jaccard(s1, s2)
        else:
            raise ValueError("Unsupported mapping method: " + str(mapper))

    def compare_levenshtein(self, s1, s2):
        """
        Calculates the normalized Levenshtein distance between s1 and s2.
        :return similarity between s1 and s2 as a float between 0 and 1
        """
        similarity = rapidfuzz.string_metric.normalized_levenshtein(s1, s2)/100
        return similarity

    def compare_jaro(self, s1, s2):
        """
        Calculates the Jaro similarity between s1 and s2.
        :return similarity between s1 and s2 as a float between 0 and 1
        """
        similarity = rapidfuzz.string_metric.jaro_similarity(s1, s2)/100
        return similarity

    def compare_jarowinkler(self, s1, s2):
        """
        Calculates the Jaro-Winkler similarity between s1 and s2.
        :return similarity between s1 and s2 as a float between 0 and 1
        """
        similarity = rapidfuzz.string_metric.jaro_winkler_similarity(s1, s2)/100
        return similarity

    def compare_indel(self, s1, s2):
        """
        Calculates the normalized Indel distance between s1 and s2.
        See: https://maxbachmann.github.io/RapidFuzz/Usage/fuzz.html#ratio
        :return similarity between s1 and s2 as a float between 0 and 1
        """
        similarity = rapidfuzz.fuzz.ratio(s1, s2)/100
        return similarity

    def compare_fuzzy_ratio(self, s1, s2):
        """
        Calculates a weighted ratio between s1 and s2 based on rapidfuzz's fuzzy ratio algorithms.
        See: https://maxbachmann.github.io/RapidFuzz/Usage/fuzz.html#wratio
        :return similarity between s1 and s2 as a float between 0 and 1
        """
        similarity = rapidfuzz.fuzz.WRatio(s1, s2)/100
        return similarity

    def compare_jaccard(self, s1, s2):
        """
        Calculates a Jaccard-based similarity between s1 and s2.
        :return similarity between s1 and s2 as a float between 0 and 1
        """
        similarity = 1-nltk.jaccard_distance(set(s1), set(s2))
        return similarity
