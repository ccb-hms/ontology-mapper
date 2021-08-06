"""Provides TFIDFMapper class"""

import logging
import re
import time
import ontoutils
import numpy as np
import pandas as pd
import sparse_dot_topn.sparse_dot_topn as ct
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from ontotermcollector import OntologyTermCollector


class TFIDFMapper:

    def __init__(self, source_terms, target_ontology):
        """
        :param source_terms: List of source terms to be mapped with ontology terms
        :param target_ontology: IRI of the ontology to be mapped against (e.g., path in the local file system, URL)
        """
        self.logger = ontoutils.get_logger(__name__, logging.INFO)
        self.source_terms = source_terms
        self.target_ontology = target_ontology

    def map(self, max_labels=20, max_mappings=3, min_score=0, incl_individuals=False):
        """
        Main match function. Default settings return only the top candidate for every source string.
        :param max_labels: The maximum number of top candidate labels that should be considered
        :param max_mappings: The maximum number of (top scoring) ontology term mappings that should be returned
        :param incl_individuals: Consider individuals (as well as classes) as candidate term mappings
        :param min_score: The lower-bound threshold for keeping a candidate term mapping, between 0-1.
                            Default set to 0, so consider all candidates
        """
        terms = OntologyTermCollector().get_ontology_terms(self.target_ontology, include_individuals=incl_individuals)
        target_labels, target_terms = self._get_target_labels_terms(terms)
        self.logger.info("Mapping source terms...")
        start = time.time()
        results_mtx = self._sparse_dot_top(self._tokenize(target_labels), target_labels, max_labels, min_score)
        results_df = self._get_matches_df(results_mtx, max_mappings, target_terms)
        end = time.time()
        self.logger.info('done (mapping time: %.2fs seconds)', end-start)
        return results_df

    def _preprocess(self, text):
        """
        Preprocesses a given string by converting to lower case, removing non-word characters and stop words
        :param text: Text to be normalized
        :return: Normalized string
        """
        text = text.lower()
        text = re.sub('\\W', ' ', text)
        text = re.sub('\\s+(in|the|any|all|for|and|or|dx|on|fh|tx|only|qnorm|w)\\s+', ' ', text)
        text = re.sub(' +', ' ', text).strip()
        return text

    def _tokenize(self, target_labels, analyzer='char_wb', n=3):
        """
        Tokenizes the (source) input strings and the target  based on the selected analyzer
        :param target_labels: List of labels from ontology terms to be matched against
        :param analyzer: Type of analyzer ('char_wb', 'word')
        :param n: The gram length n (when using n-gram analyzer)
        :return TF-IDF Vectorizer
        """
        # Create count vectorizer and fit it on both lists to get vocabulary
        count_vectorizer = CountVectorizer(preprocessor=self._preprocess, analyzer=analyzer, ngram_range=(n, n))
        vocabulary = count_vectorizer.fit(self.source_terms + target_labels).vocabulary_

        # Create tf-idf vectorizer
        return TfidfVectorizer(vocabulary=vocabulary, analyzer=analyzer, ngram_range=(n, n))

    def _sparse_dot_top(self, vectorizer, target_labels, max_labels, min_score):
        """ https://gist.github.com/ymwdalex/5c363ddc1af447a9ff0b58ba14828fd6#file-awesome_sparse_dot_top-py """
        src_mtx = vectorizer.fit_transform(self.source_terms).tocsr()
        tgt_mtx = vectorizer.fit_transform(target_labels).transpose().tocsr()
        x, _ = src_mtx.shape
        _, y = tgt_mtx.shape
        idx_dtype = np.int32
        nnz_max = x * max_labels
        indptr = np.zeros(x + 1, dtype=idx_dtype)
        indices = np.zeros(nnz_max, dtype=idx_dtype)
        data = np.zeros(nnz_max, dtype=src_mtx.dtype)
        ct.sparse_dot_topn(
            x, y, np.asarray(src_mtx.indptr, dtype=idx_dtype),
            np.asarray(src_mtx.indices, dtype=idx_dtype),
            src_mtx.data,
            np.asarray(tgt_mtx.indptr, dtype=idx_dtype),
            np.asarray(tgt_mtx.indices, dtype=idx_dtype),
            tgt_mtx.data,
            max_labels,
            min_score,
            indptr, indices, data)
        return csr_matrix((data, indices, indptr), shape=(x, y))

    def _get_matches_df(self, results_mtx, max_matches, target_terms):
        """ Build dataframe for results """
        coo_mtx = results_mtx.tocoo()
        mappings_list = []
        last_source_string = ""
        candidate_target_terms = set()
        for row, col, score in zip(coo_mtx.row, coo_mtx.col, coo_mtx.data):
            source_term = self.source_terms[row]
            onto_term = target_terms[col]
            if source_term == last_source_string:
                if len(candidate_target_terms) == max_matches:
                    continue
            else:
                last_source_string = source_term
                candidate_target_terms.clear()
            if onto_term.iri not in candidate_target_terms:
                mappings_list.append((source_term, onto_term.label(), onto_term.iri, onto_term.ontology_iri, score))
            candidate_target_terms.add(onto_term.iri)
        col_names = ['Source Term', 'Mapped Term Label', 'Mapped Term Identifier', 'Ontology', 'Score']
        return pd.DataFrame(mappings_list, columns=col_names)

    def _get_target_labels_terms(self, ontology_terms):
        """Convenience method to obtain lists of labels and terms to enable retrieving terms from their labels"""
        target_labels, target_terms = [], []
        for term in ontology_terms:
            for label in term.labels:
                target_labels.append(label)
                target_terms.append(term)
        return target_labels, target_terms
