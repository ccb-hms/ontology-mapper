import logging
import onto_utils
from owlready2 import *
from term import OntologyTerm


class OntologyTermCollector:

    def __init__(self, ontology_iri):
        """"
        :param ontology_iri: IRI of the ontology (e.g., path of ontology document in the local file system, URL)
        """
        self.logger = onto_utils.get_logger(__name__, logging.INFO)
        self.ontology_iri = ontology_iri

    def get_ontology_terms(self, base_iris=(), use_reasoning=False, exclude_deprecated=True, include_individuals=False):
        """
        Collect the terms described in the ontology at the specified IRI
        :param base_iris: Limit ontology term collection to terms whose IRIs start with any IRI given in this tuple
        :param use_reasoning: Use a reasoner to compute inferred class hierarchy and individual types
        :param exclude_deprecated: Exclude ontology terms stated as deprecated using owl:deprecated 'true'
        :param include_individuals: Include OWL ontology individuals in addition to ontology classes
        :return: Collection of ontology terms in the specified ontology
        """
        ontology = self._load_ontology(self.ontology_iri)
        if use_reasoning:
            self._classify_ontology(ontology)
        self.logger.info("Collecting ontology term details...")
        start = time.time()
        ontology_terms = []
        if len(base_iris) > 0:
            for iri in base_iris:
                query = iri + "*"
                self.logger.info("...Collecting terms with IRIs starting in: " + iri)
                iris = list(default_world.search(iri=query))
                ontology_terms.extend(self._get_ontology_terms(iris, ontology, exclude_deprecated))
        else:
            ontology_terms = self._get_ontology_terms(ontology.classes(), ontology, exclude_deprecated)
            if include_individuals:
                ontology_terms.extend(self._get_ontology_terms(ontology.individuals(), ontology, exclude_deprecated))
        end = time.time()
        self.logger.info("...done: collected %i ontology terms (collection time: %.2fs)", len(ontology_terms), end-start)
        return ontology_terms

    def _get_ontology_terms(self, term_list, ontology, exclude_deprecated):
        ontology_terms = []
        for ontology_term in term_list:
            if not isinstance(ontology_term, PropertyClass) and ontology_term is not Thing and ontology_term is not Nothing:
                if (exclude_deprecated and not deprecated[ontology_term]) or (not exclude_deprecated):
                    labels = self._get_labels(ontology_term)
                    synonyms = self._get_synonyms(ontology_term)
                    parents = self._get_parents(ontology_term)
                    children = self._get_children(ontology_term, ontology)
                    instances = self._get_instances(ontology_term, ontology)
                    definition = self._get_definition(ontology_term)
                    term_details = OntologyTerm(ontology_term.iri, labels, synonyms, definition, ontology.base_iri,
                                                parents=parents, children=children, instances=instances)
                    ontology_terms.append(term_details)
                else:
                    self.logger.debug("Excluding deprecated ontology term: %s", ontology_term.iri)
        return ontology_terms

    def _get_parents(self, ontology_term):
        parents = set()  # named/atomic superclasses except owl:Thing
        try:
            all_parents = ontology_term.is_a  # obtain all (direct and indirect) parents of this entity
            for parent in all_parents:
                # exclude OWL restrictions and owl:Thing and Self
                if isinstance(parent, ThingClass) and parent is not Thing and parent is not ontology_term:
                    parents.add(parent)
        except AttributeError as err:
            self.logger.debug(err)
        return parents

    def _get_children(self, ontology_term, ontology):
        children = set()
        try:
            children = set(ontology.get_children_of(ontology_term))
        except AttributeError as err:
            self.logger.debug(err)
        return children

    def _get_instances(self, ontology_term, ontology):
        instances = set()
        try:
            instances = set(ontology.get_instances_of(ontology_term))
        except AttributeError as err:
            self.logger.debug(err)
        return instances

    def _get_labels(self, ontology_term):
        """
        Collect the labels of the given ontology term both given by rdfs:label and skos:prefLabel
        :param ontology_term: Ontology term
        :return: Collection of labels of the ontology term
        """
        labels = set()
        for rdfs_label in self._get_rdfs_labels(ontology_term):
            labels.add(rdfs_label)
        for skos_label in self._get_skos_pref_labels(ontology_term):
            labels.add(skos_label)
        if len(labels) == 0:
            label_from_iri = onto_utils.label_from_iri(ontology_term.iri)
            self.logger.info("Ontology term %s has no labels (rdfs:label or skos:prefLabel). "
                             "Using a label based on the term IRI: %s", ontology_term.iri, label_from_iri)
            labels.add(label_from_iri)
        self.logger.debug("Collected %i labels and synonyms for %s", len(labels), ontology_term)
        return labels

    def _get_synonyms(self, ontology_term):
        """
        Collect the synonyms of the given ontology term
        :param ontology_term: Ontology term
        :return: Collection of synonyms of the ontology term
        """
        synonyms = set()
        for synonym in self._get_obo_exact_synonyms(ontology_term):
            synonyms.add(synonym)
        for nci_synonym in self._get_nci_synonyms(ontology_term):
            synonyms.add(nci_synonym)
        self.logger.debug("Collected %i synonyms for %s", len(synonyms), ontology_term)
        return synonyms

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

    def _get_definition(self, ontology_term):
        """
         Get the definition (if one exists) of the given term as specified using the skos:definition annotation property
         :param ontology_term: Ontology term to collect definition of
         :return: String value of the skos:definition annotation property assertion on the given term
         """
        definition = ""
        try:
            definition = ontology_term.definition
        except AttributeError as err:
            self.logger.debug(err)
        return definition

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
        self._log_ontology_metrics(ontology)
        self.logger.info("done (loading time: %.2fs)", end-start)
        return ontology

    def _classify_ontology(self, ontology):
        """
        Perform reasoning over the given ontology (consistency checking and classification)
        :param ontology: ontology instance
        """
        self.logger.info("Reasoning over ontology...")
        start = time.time()
        with ontology:  # entailments will be added to this ontology
            sync_reasoner(infer_property_values=True)
        end = time.time()
        self.logger.info("done (reasoning time: %.2fs)", end - start)

    def _log_ontology_metrics(self, ontology):
        self.logger.debug(" Ontology IRI: %s", ontology.base_iri)
        self.logger.debug(" Class count: %i", len(list(ontology.classes())))
        self.logger.debug(" Individual count: %i", len(list(ontology.individuals())))
        self.logger.debug(" Object property count: %i", len(list(ontology.object_properties())))
        self.logger.debug(" Data property count: %i", len(list(ontology.data_properties())))
        self.logger.debug(" Annotation property count: %i", len(list(ontology.annotation_properties())))
