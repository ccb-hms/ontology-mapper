import logging
import time
import nlu
from scipy import sparse

import ontoutils
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class BioBertMapper:
    """
    Requires Java 8 and Python <3.9  (as of 1/22)
    See Colab notebook for environment instructions:
    https://colab.research.google.com/drive/1p98xNY6La0rc4CJ3tYyLxsJ2vx_dHzFq
    """

    def __init__(self, target_ontology_terms):
        """
        :param target_ontology_terms: Collection of ontology terms to be mapped against
        """
        self.logger = ontoutils.get_logger(__name__, logging.INFO)
        self.target_labels, self.target_terms = self._get_target_labels_terms(target_ontology_terms)
        self.biobert = self.load_biobert()

    def load_biobert(self):
        # Load BioBERT model (for sentence-type embeddings)
        self.logger.info("Loading BioBERT model...")
        start = time.time()
        biobert = nlu.load('en.embed_sentence.biobert.pmc_base_cased')
        end = time.time()
        self.logger.info('done (BioBERT loading time: %.2fs seconds)', end - start)
        return biobert

    def map(self, source_terms, max_mappings=3, min_score=0.3):
        """
        Main mapping function. Default settings return only the top candidate for every source string.
        :param source_terms: List of source terms to be mapped with ontology terms
        :param max_mappings: The maximum number of (top scoring) ontology term mappings that should be returned
        :param min_score: The lower-bound threshold for keeping a candidate term mapping, between 0-1.
                            Default set to 0, so consider all candidates
        """
        self.logger.info("Mapping %i source terms...", len(source_terms))
        start = time.time()
        source_terms = ontoutils.normalize_list(source_terms)

        # Generate embeddings for source and target terms
        self.logger.info("...Generating embeddings for source and target terms")
        src_terms_embeddings = self.get_biobert_embeddings(source_terms)
        tgt_terms_embeddings = self.get_biobert_embeddings(self.target_labels)

        # Compute cosine similarity between source and target term embeddings
        self.logger.info("...Computing cosine similarity between source and target term embeddings")
        results = cosine_similarity(src_terms_embeddings, tgt_terms_embeddings)
        results_mtx = sparse.csr_matrix(results)

        # Create and return a data frame of the top matches with at least the specified min score
        self.logger.info("...Building results data frame")
        results_df = self._get_top_n_matches(results_mtx, source_terms, self.target_terms, max_mappings, min_score)
        end = time.time()
        self.logger.info('done (mapping time: %.2fs seconds)', end-start)
        return results_df

    def get_biobert_embeddings(self, strings):
        embedding_list = []
        for string in strings:
            self.logger.debug("...Generating embedding for: %s", string)
            embedding_list.append(self.get_biobert_embedding(string))
        return embedding_list

    def get_biobert_embedding(self, string):
        embedding = self.biobert.predict(string, output_level='sentence', get_embeddings=True)
        return embedding.sentence_embedding_biobert.values[0]

    def _get_matches(self, results_mtx, source_terms, target_terms, min_score):
        """ Build dataframe for results """
        coo_mtx = results_mtx.tocoo()
        mappings_list = set()
        for row, col, score in zip(coo_mtx.row, coo_mtx.col, coo_mtx.data):
            if score >= min_score:
                source_term = source_terms[row]
                onto_term = target_terms[col]
                mappings_list.add((source_term, onto_term.label, onto_term.iri, score))
        col_names = ['Source Term', 'Mapped Term Label', 'Mapped Term IRI', 'Score']
        results_df = pd.DataFrame(mappings_list, columns=col_names)
        results_df.set_index(['Source Term'], inplace=True)
        results_df.sort_values(['Score'], ascending=False, inplace=True)
        results_df.sort_index(inplace=True)
        return results_df

    def _get_top_n_matches(self, results_mtx, source_terms, target_terms, max_mappings, min_score):
        matches_df = self._get_matches(results_mtx, source_terms, target_terms, min_score)
        matches_df = matches_df.groupby('Source Term')
        return matches_df.head(max_mappings)

    def _get_target_labels_terms(self, ontology_terms):
        """Convenience method to obtain lists of labels and terms to enable retrieving terms from their labels"""
        target_labels, target_terms = [], []
        for term in ontology_terms:
            for label in term.labels:
                target_labels.append(label)
                target_terms.append(term)
        return target_labels, target_terms
