import logging
import time
import ontoutils
from owlready2 import *
from ontoterm import OntologyTerm


class OntologyTermCollector:

    def __init__(self, ontology_iri):
        """"
        :param ontology_iri: IRI of the ontology (e.g., path of ontology document in the local file system, URL)
        """
        self.logger = ontoutils.get_logger(__name__, logging.INFO)
        self.ontology_iri = ontology_iri

    def get_ontology_terms(self, base_iri=None, use_reasoning=False, ignore_deprecated=True, include_individuals=False):
        """
        Collect the terms described in the ontology at the specified IRI
        :param base_iri: When provided, ontology term collection is restricted to terms whose IRIs start with this.
        :param use_reasoning: Use a reasoner to compute inferred parents of classes (and individuals) in the ontology
        :param ignore_deprecated: Ignore ontology terms stated as deprecated using owl:deprecated 'true'
        :param include_individuals: True if OWL individuals should also be included, False otherwise and by default
        :return: Collection of ontology terms in the specified ontology
        """
        ontology = self._load_ontology(self.ontology_iri)
        if use_reasoning:
            self._classify_ontology(ontology)
        self.logger.info("Collecting ontology term details...")
        start = time.time()
        if base_iri is not None:
            # Collect only the ontology terms with IRIs that start with the given 'base_iri'
            query = base_iri + "*"
            iris = list(default_world.search(iri=query))
            ontology_terms = self._get_ontology_terms(iris, ontology.base_iri, ignore_deprecated)
        else:
            ontology_terms = self._get_ontology_terms(ontology.classes(), ontology.base_iri, ignore_deprecated)
            if include_individuals:
                ontology_terms.extend(self._get_ontology_terms(ontology.individuals(), ontology.base_iri, ignore_deprecated))
        end = time.time()
        self.logger.info("done: collected %i ontology terms (collection time: %.2fs)", len(ontology_terms), end-start)
        return ontology_terms

    def _get_ontology_terms(self, entities, onto_base_iri, ignore_deprecated):
        ontology_terms = []
        for owl_entity in entities:
            if (ignore_deprecated and not deprecated[owl_entity]) or (not ignore_deprecated):
                labels = self._get_labels_and_synonyms(owl_entity)
                if len(labels) > 0:
                    all_parents = self._get_parents(owl_entity)
                    named_parents = []  # collection of named/atomic superclasses except owl:Thing
                    for parent in all_parents:
                        if parent.__class__ is ThingClass and parent is not Thing:  # Ignore OWL restrictions and owl:Thing
                            named_parents.append(parent)
                    ontology_terms.append(OntologyTerm(owl_entity.iri, labels, onto_base_iri, parents=named_parents))
            else:
                self.logger.debug("Ignoring deprecated ontology term: %s", owl_entity.iri)
        return ontology_terms

    def _get_parents(self, ontology_term):
        parents = []
        try:
            parents = ontology_term.INDIRECT_is_a  # obtain all (direct and indirect) parents of this entity
        except AttributeError as err:
            self.logger.debug(err)
        return parents

    def _get_labels_and_synonyms(self, ontology_term):
        """
        Collect the labels and synonyms of the given ontology term
        :param ontology_term: Ontology term
        :return: Collection of labels and synonyms of the ontology term
        """
        labels = []
        for rdfs_label in self._get_rdfs_labels(ontology_term):
            labels.append(rdfs_label) if rdfs_label not in labels else labels
        for skos_label in self._get_skos_pref_labels(ontology_term):
            labels.append(skos_label) if skos_label not in labels else labels
        for synonym in self._get_obo_exact_synonyms(ontology_term):
            labels.append(synonym) if synonym not in labels else labels
        for nci_synonym in self._get_nci_synonyms(ontology_term):
            labels.append(nci_synonym) if nci_synonym not in labels else labels
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
        self.logger.info("Loading ontology %s...", ontology_iri)
        start = time.time()
        ontology = get_ontology(ontology_iri).load()
        end = time.time()
        self.logger.info("done (loading time: %.2fs)", end-start)
        self._log_ontology_metrics(ontology)
        return ontology

    def _classify_ontology(self, ontology):
        self.logger.info("Reasoning over ontology...")
        start = time.time()
        with ontology:
            sync_reasoner(infer_property_values=True)
        end = time.time()
        self.logger.info("done (reasoning time: %.2fs)", end - start)

    def _log_ontology_metrics(self, ontology):
        self.logger.debug(" Ontology IRI: %s", ontology.base_iri)
        self.logger.debug("  Class count: %i", len(list(ontology.classes())))
        self.logger.debug("  Individual count: %i", len(list(ontology.individuals())))
        self.logger.debug("  Object property count: %i", len(list(ontology.object_properties())))
        self.logger.debug("  Data property count: %i", len(list(ontology.data_properties())))
        self.logger.debug("  Annotation property count: %i", len(list(ontology.annotation_properties())))
