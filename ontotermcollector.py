import logging
import time

import ontoutils
from owlready2 import *
from ontoterm import OntologyTerm


class OntologyTermCollector:

    def __init__(self):
        self.logger = ontoutils.get_logger(__name__, logging.INFO)

    def get_ontology_terms(self, ontology_iri, include_individuals=False):
        """
        Collect the terms described in the ontology at the specified IRI
        :param ontology_iri: IRI of the ontology (e.g., path of ontology document in the local file system, URL)
        :param include_individuals: True if OWL individuals should also be included, False otherwise and by default
        :return: Collection of ontology terms in the specified ontology
        """
        ontology_terms = []
        ontology = self._load_ontology(ontology_iri)
        self.logger.info("Collecting ontology term relationships (eg, labels, synonyms)")
        start = time.time()
        for onto_class in ontology.classes():
            labels = self._get_labels_and_synonyms(onto_class)
            ontology_terms.append(OntologyTerm(onto_class.iri, labels, ontology.base_iri))
        if include_individuals:
            for onto_individual in ontology.individuals():
                labels = self._get_labels_and_synonyms(onto_individual)
                ontology_terms.append(OntologyTerm(onto_individual.iri(), labels, ontology.base_iri))
        end = time.time()
        self.logger.info("done: collected %i ontology terms (collection time: %.2fs)", len(ontology_terms), end-start)
        return ontology_terms

    def _get_labels_and_synonyms(self, ontology_term):
        """
        Collect the labels and synonyms of the given ontology term
        :param ontology_term: Ontology term
        :return: Collection of labels and synonyms of the ontology term
        """
        labels = []
        for rdfs_label in self._get_rdfs_labels(ontology_term):
            labels.append(rdfs_label)
        for skos_label in self._get_skos_pref_labels(ontology_term):
            labels.append(skos_label)
        for synonym in self._get_obo_exact_synonyms(ontology_term):
            labels.append(synonym)
        for nci_synonym in self._get_nci_synonyms(ontology_term):
            labels.append(nci_synonym)
        self.logger.debug("Collected %i labels and synonyms for %s", len(labels), ontology_term)
        return labels

    def _get_rdfs_labels(self, ontology_term):
        """
        Collect labels of the given term that are specified using the standard rdfs:label annotation property
        :param ontology_term: Ontology term to collect labels from
        :return: Collection of RDFS labels
        """
        rdfs_labels = []
        try:
            for rdfs_label in ontology_term.label:
                rdfs_labels.append(rdfs_label)
        except AttributeError as err:
            self.logger.debug(err)
        return rdfs_labels

    def _get_skos_pref_labels(self, ontology_term):
        """
        Collect labels of the given term that are specified using the skos:prefLabel annotation property
        :param ontology_term: Ontology term to collect labels from
        :return: Collection of SKOS preferred labels
        """
        skos_labels = []
        try:
            for skos_pref_label in ontology_term.prefLabel:
                skos_labels.append(skos_pref_label)
        except AttributeError as err:
            self.logger.debug(err)
        return skos_labels

    def _get_obo_exact_synonyms(self, ontology_term):
        """
        Collect synonyms of the given term that are specified using the annotation property used by DOID, MONDO, EFO,
        HPO, and other OBO ontologies: <http://www.geneontology.org/formats/oboInOwl#hasExactSynonym>.
        :param ontology_term: Ontology term to collect synonyms from
        :return: Collection of synonyms
        """
        synonyms = []
        try:
            for synonym in ontology_term.hasExactSynonym:
                synonyms.append(synonym)
        except AttributeError as err:
            self.logger.debug(err)
        return synonyms

    def _get_nci_synonyms(self, ontology_term):
        """
        Collect synonyms of the given term that are specified using the NCI Thesaurus annotation property:
         <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#P90>.
        :param ontology_term: Ontology term to collect synonyms from
        :return: Collection of synonyms
        """
        nci_synonyms = []
        try:
            for synonym in ontology_term.P90:
                nci_synonyms.append(synonym)
        except AttributeError as err:
            self.logger.debug(err)
        return nci_synonyms

    def _load_ontology(self, ontology_iri):
        """
        Load the ontology at the specified IRI.
        :param ontology_iri: IRI of the ontology (e.g., path of ontology document in the local file system, URL)
        :return: Ontology document
        """
        start = time.time()
        self.logger.info("Loading ontology %s...", ontology_iri)
        ontology = get_ontology(ontology_iri).load()
        end = time.time()
        self.logger.info("done (loading time: %.2fs)", end-start)
        self._log_ontology_metrics(ontology)
        return ontology

    def _log_ontology_metrics(self, ontology):
        self.logger.debug(" Ontology IRI: %s", ontology.base_iri)
        self.logger.debug("  Class count: %i", len(list(ontology.classes())))
        self.logger.debug("  Individual count: %i", len(list(ontology.individuals())))
        self.logger.debug("  Object property count: %i", len(list(ontology.object_properties())))
        self.logger.debug("  Data property count: %i", len(list(ontology.data_properties())))
        self.logger.debug("  Annotation property count: %i", len(list(ontology.annotation_properties())))
