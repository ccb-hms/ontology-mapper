import logging
from pickletools import stringnl
import time
import nlu
from scipy import sparse

import ontoutils
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from nltk import word_tokenize
import subprocess
import gensim
from owlready2 import *
from ontotermcollector import get_ontology
import re
import numpy as np

class Owl2VecMapper:
    """
    Requires Java 8 and Python <3.9  (as of 1/22)
    See Colab notebook for environment instructions:
    https://colab.research.google.com/drive/1p98xNY6La0rc4CJ3tYyLxsJ2vx_dHzFq
    """

    def __init__(self, target_ontology_terms, ontology_file):
        """
        :param target_ontology_terms: Collection of ontology terms to be mapped against
        """
        self.logger = ontoutils.get_logger(__name__, logging.INFO)
        self.target_labels, self.target_terms = self._get_target_labels_terms(target_ontology_terms)
        # TODO: Alter call to this file to pass in ontology_file too.
        self.target_ontology_file = ontology_file
        

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

        # Generate ontology file for source_terms
        ontology = ontoutils.get_ontology_from_labels(source_terms)
        ontology.save(file="source_terms_ontology.owl")
        self.source_ontology_file = "source_terms_ontology.owl"
        
        # Generate embeddings for source and target terms
        self.logger.info("...Generating embeddings for source and target terms")
        self.generate_owl2vec_embeddings("source_terms_ontology.owl", "./owl2vec_embeddings/source_embeddings")
        self.generate_owl2vec_embeddings(self.ontology_file, "./owl2vec_embeddings/target_embeddings")
        self.source_embeddings_file = "./owl2vec_embeddings/source_embeddings"
        self.target_embeddings_file = "./owl2vec_embeddings/target_embeddings"

        src_terms_embeddings = self.get_owl2vec_embeddings(source_terms, self.source_embeddings_file)
        tgt_terms_embeddings = self.get_owl2vec_embeddings(self.target_labels, self.target_embeddings_file)

        # Delete the embeddings files and source term ontology
        subprocess.call("rm source_terms_ontology.owl", shell=True)
        subprocess.call("rm ./owl2vec_embeddings/source_embeddings", shell=True)
        subprocess.call("rm ./owl2vec_embeddings/target_embeddings", shell=True)

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
    
    def generate_owl2vec_embeddings(self, onto_filename, embeddings_filename):
        subprocess.call("python3 OWL2Vec-Star/OWL2Vec_Standalone.py --config_file owl2vec_default.cfg --Embed_Out_URI no --Embed_Out_Words yes --ontology_file " + onto_filename + " --embedding_dir " + embeddings_filename, shell=True)
        self.embeddings_file = embeddings_filename
        # TODO: Confirm that python waits for this to complete before going on.

    def get_owl2vec_embeddings(self, strings, embeddings_file):
        embedding_list = []
        for string in strings:
            self.logger.debug("...Generating embedding for: %s", string)
            embedding_list.append(self.get_owl2vec_embedding(string, embeddings_file))
        return embedding_list
        # # TODO: Confirm what to return here with Rafael and adjust accordingly
        model = gensim.models.Word2Vec.load(embeddings_file)
        onto = get_ontology(onto_file).load()
        classes = list(onto.classes())
        df = pd.DataFrame()
        for c in classes:
            label = c.label[0]
            text = ' '.join([re.sub(r'https?:\/\/.*[\r\n]*', '', w, flags=re.MULTILINE) for w in label.lower().split()])
            words = [token.lower() for token in word_tokenize(text) if token.isalpha()]
            n = 0
            word_v = np.zeros(model.vector_size)
            for word in words:
                if word in model.wv.index_to_key:
                    word_v += model.wv.get_vector(word)
                    n += 1
            word_v = word_v / n if n > 0 else word_v
            embeddings_list.append(word_v)
        
        return embedding_list


    def get_owl2vec_embedding(self, string, embeddings_file):
        model = gensim.models.Word2Vec.load(embeddings_file)
        word_v = np.zeros(model.vector_size)
        if string in model.wv.index_to_key:
            word_v += model.wv.get_vector(string)

        return word_v

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
