"""Provides SyntacticMapper class"""

import logging
import time
import nltk
import rapidfuzz
from tqdm import tqdm
from text2term import onto_utils
from text2term.similarity_metric import SimilarityMetric
from text2term.term_mapping import TermMapping, TermMappingCollection


class SyntacticMapper:

    def __init__(self, target_ontology_terms):
        """
        :param target_ontology_terms: Collection of ontology terms to be mapped against
        """
        self.logger = onto_utils.get_logger(__name__, logging.INFO)
        self.target_ontology_terms = target_ontology_terms

    def map(self, source_terms, similarity_metric=SimilarityMetric.JARO_WINKLER, max_mappings=3):
        """
        :param source_terms: List of source terms to be mapped with ontology terms
        :param similarity_metric: Similarity metric to be used for matching
        :param max_mappings: Maximum number of (top scoring) ontology term mappings that should be returned
        """
        self.logger.info("Mapping %i source terms...", len(source_terms))
        start = time.time()
        mappings = []
        for input_term in tqdm(source_terms):
            matches = self._map(input_term, similarity_metric, max_mappings)
            mappings.extend(matches)
        end = time.time()
        self.logger.info('done (mapping time: %.2fs seconds)', end - start)
        return TermMappingCollection(mappings).mappings_df()

    def _map(self, source_term, similarity_metric, max_matches=3):
        self.logger.debug("Matching %s...", source_term)
        term_matches = []
        for term in self.target_ontology_terms:
            highest_similarity = 0.0
            for target_name in self._term_names(term):
                similarity = self.compare(source_term, target_name, similarity_metric)
                self.logger.debug("%s -> %s (%.2f)", source_term, target_name, similarity)
                if similarity > highest_similarity:
                    highest_similarity = similarity
            term_matches.append(TermMapping(source_term, term.label, term.iri, term.ontology_iri, highest_similarity))
        matches_sorted = sorted(term_matches, key=lambda x: x.mapping_score, reverse=True)
        del matches_sorted[max_matches:]
        return matches_sorted

    def _term_names(self, ontology_term):
        lbls_syns = []
        lbls_syns.extend(ontology_term.labels)
        lbls_syns.extend(ontology_term.synonyms)
        return lbls_syns

    def compare(self, s1, s2, similarity_metric):
        """
        Compare the given strings s1 and s2 with respect to the specified string similarity metric
        :param s1: source string
        :param s2: target string
        :param similarity_metric: String similarity metric to be used (see supported metrics in `SimilarityMetric`)
        """
        if similarity_metric == SimilarityMetric.LEVENSHTEIN:
            return self.compare_levenshtein(s1, s2)
        elif similarity_metric == SimilarityMetric.JARO:
            return self.compare_jaro(s1, s2)
        elif similarity_metric == SimilarityMetric.JARO_WINKLER:
            return self.compare_jarowinkler(s1, s2)
        elif similarity_metric == SimilarityMetric.FUZZY:
            return self.compare_fuzzy(s1, s2)
        elif similarity_metric == SimilarityMetric.FUZZY_WEIGHTED:
            return self.compare_fuzzy_weighted(s1, s2)
        elif similarity_metric == SimilarityMetric.JACCARD:
            return self.compare_jaccard(s1, s2)
        else:
            self.logger.error("Unsupported similarity metric: %s", similarity_metric)

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

    def compare_fuzzy(self, s1, s2):
        """
        Calculates the normalized Indel distance between s1 and s2.
        See: https://maxbachmann.github.io/RapidFuzz/Usage/fuzz.html#ratio
        :return similarity between s1 and s2 as a float between 0 and 1
        """
        similarity = rapidfuzz.fuzz.ratio(s1, s2)/100
        return similarity

    def compare_fuzzy_weighted(self, s1, s2):
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
