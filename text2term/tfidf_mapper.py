"""Provides TFIDFMapper class"""

import logging
import time
import sparse_dot_topn as ct
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from text2term import onto_utils
from text2term.term_mapping import TermMapping, TermMappingCollection


class TFIDFMapper:

    def __init__(self, target_ontology_terms):
        """
        :param target_ontology_terms: Collection of ontology terms to be mapped against
        """
        self.logger = onto_utils.get_logger(__name__, logging.INFO)
        self.target_ontology_terms = target_ontology_terms
        self.target_labels, self.target_terms = self._get_target_labels_terms(target_ontology_terms)

    def map(self, source_terms, source_terms_ids, max_mappings=3, min_score=0.3):
        """
        Main mapping function. Default settings return only the top candidate for every source string.
        :param source_terms: List of source terms to be mapped with ontology terms
        :param source_terms_ids: List of identifiers for the given source terms
        :param max_mappings: The maximum number of (top scoring) ontology term mappings that should be returned
        :param min_score: The lower-bound threshold for keeping a candidate term mapping, between 0-1.
                            Default set to 0, so consider all candidates
        """
        self.logger.info("Mapping %i source terms...", len(source_terms))
        self.logger.info("...against %i ontology terms (%i labels/synonyms)", len(self.target_ontology_terms), len(self.target_labels))
        start = time.time()
        source_terms_norm = onto_utils.normalize_list(source_terms)
        vectorizer = self._tokenize(source_terms_norm, self.target_labels)
        results_mtx = self._sparse_dot_top(vectorizer, source_terms_norm, self.target_labels, min_score)
        results_df = self._get_mappings(results_mtx, max_mappings, source_terms, source_terms_ids, self.target_terms)
        end = time.time()
        self.logger.info("...done (mapping time: %.2fs seconds)", end-start)
        return results_df

    def _tokenize(self, source_terms, target_labels, analyzer='char_wb', n=3):
        """
        Tokenizes the (source) input strings and the target labels based on the selected analyzer
        :param source_terms: List of source terms to be matched
        :param target_labels: List of labels from ontology terms to be matched against
        :param analyzer: Type of analyzer ('char_wb', 'word')
        :param n: The gram length n (when using n-gram analyzer)
        :return TF-IDF Vectorizer
        """
        # Create count vectorizer and fit it on both lists to get vocabulary
        count_vectorizer = CountVectorizer(analyzer=analyzer, ngram_range=(n, n))
        vocabulary = count_vectorizer.fit(source_terms + target_labels).vocabulary_
        return TfidfVectorizer(vocabulary=vocabulary, analyzer=analyzer, ngram_range=(n, n))

    def _sparse_dot_top(self, vectorizer, source_terms, target_labels, min_score):
        src_mtx = vectorizer.fit_transform(source_terms).tocsr()
        tgt_mtx = vectorizer.fit_transform(target_labels).transpose().tocsr()
        # 'ntop' specifies the maximum number of labels/synonyms that should be considered
        # multiple labels/synonyms in the 'ntop' matches may be from the same ontology term
        return ct.awesome_cossim_topn(src_mtx, tgt_mtx, ntop=50, lower_bound=min_score)

    def _get_mappings(self, results_mtx, max_mappings, source_terms, source_terms_ids, target_terms):
        """ Build and return dataframe for mapping results along with term graphs for the obtained mappings """
        coo_mtx = results_mtx.tocoo()
        mappings = []
        last_source_term = ""
        top_mappings = set()
        for row, col, score in zip(coo_mtx.row, coo_mtx.col, coo_mtx.data):
            source_term = source_terms[row]
            source_term_id = source_terms_ids[row]
            onto_term = target_terms[col]
            self.logger.debug("Source term: %s maps to %s (%f)", source_term, onto_term.label, score)
            if source_term == last_source_term:
                if len(top_mappings) == max_mappings:
                    continue
            else:
                last_source_term = source_term
                top_mappings.clear()
            if onto_term.iri not in top_mappings:
                mappings.append(TermMapping(source_term, source_term_id, onto_term.label, onto_term.iri, score))
                top_mappings.add(onto_term.iri)
        return TermMappingCollection(mappings).mappings_df()

    def _get_target_labels_terms(self, ontology_terms):
        """Get lists of labels and terms to enable retrieving terms from their labels"""
        target_labels, target_terms = [], []
        for term in ontology_terms.values():
            for label in term.labels:
                target_labels.append(label)
                target_terms.append(term)
            for synonym in term.synonyms:
                target_labels.append(synonym)
                target_terms.append(term)
        return target_labels, target_terms
