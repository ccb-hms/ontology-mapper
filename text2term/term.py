"""Provides OntologyTerm class and OntologyTermType string enumeration"""

from enum import Enum


class OntologyTermType(str, Enum):
    CLASS = "class"
    PROPERTY = "property"
    ANY = "any"


class OntologyTerm:

    def __init__(self, iri, labels, definitions=(), synonyms=(), parents=(), children=(), instances=(), restrictions=(),
                 deprecated=False, term_type=OntologyTermType.CLASS):
        """
        Constructor for a succinct representation of an ontology term
        :param iri: IRI of the ontology term
        :param labels: Set of human-readable labels for the term (e.g., rdfs:label, skos:prefLabel)
        :param definitions: Set of textual definitions of the term
        :param synonyms: Set of synonyms of the term (e.g., alternative labels)
        :param parents: Dictionary containing the IRIs of parent terms (superclasses) and their label(s)
        :param children: Dictionary containing the IRIs of child terms (subclasses) and their label(s)
        :param instances: Dictionary containing the IRIs of instances of the term (rdf:type) and their label(s)
        :param restrictions: Dictionary containing complex class restrictions (such as located_in.Hand) on this term
        :param deprecated: true if term is stated to be owl:deprecated, false otherwise
        :param term_type: Type of term: class or property
        """
        self._iri = iri
        self._labels = labels
        self._synonyms = synonyms
        self._definitions = definitions
        self._parents = parents
        self._children = children
        self._instances = instances
        self._restrictions = restrictions
        self._deprecated = deprecated
        self._term_type = term_type

    @property
    def iri(self):
        """
        Returns the IRI of this term
        :return: str
        """
        return self._iri

    @property
    def labels(self):
        """
        Returns the set of human-readable labels for the term specified using rdfs:label or skos:prefLabel properties
        :return: set
        """
        return self._labels

    @property
    def definitions(self):
        """
        Returns the set of textual definitions of the term specified using either the skos:definition or the
         IAO:0000115 ('definition') annotation properties
        :return: set
        """
        return self._definitions

    @property
    def synonyms(self):
        """
        Returns the set of synonyms of the term specified using obo:hasExactSynonym or ncit:P90 properties
        :return: set
        """
        return self._synonyms

    @property
    def parents(self):
        """
        Returns a dictionary containing the IRIs of parent terms as keys, and their respective labels as values
        :return: dict
        """
        return self._parents

    @property
    def children(self):
        """
        Returns a dictionary containing the IRIs of child terms as keys, and their respective labels as values
        :return: dict
        """
        return self._children

    @property
    def instances(self):
        """
        Returns a dictionary containing the IRIs of instance terms as keys, and their respective labels as values
        :return: dict
        """
        return self._instances

    @property
    def restrictions(self):
        """
        Returns a dictionary containing the IRIs of properties as keys, and the respective fillers as values
        For example, for a restriction such as ':has_disease_location :pancreas', the dictionary would have:
        {':has_disease_location': ':pancreas'}
        For nested expressions such as 'has_disease_location (:pancreas or :liver);, the dictionary would have a string
        representation of that expression (using owlready2s to_str):
        {':has_disease_location': ':pancreas | :liver'}
        :return: dict
        """
        return self._restrictions

    @property
    def label(self):
        """
        Returns a single label for this term
        :return: str
        """
        return next(iter(self.labels))

    @property
    def deprecated(self):
        """
        Returns true if this term is stated to be 'owl:deprecated True', false otherwise
        :return: bool
        """
        return self._deprecated

    @property
    def term_type(self):
        """
        Returns the ontology term type specified using OntologyTermType enum
        :return: OntologyTermType
        """
        return self._term_type

    def __eq__(self, other):
        if isinstance(other, OntologyTerm):
            return self._iri == other._iri
        return False

    def __hash__(self):
        return hash(str(self._iri))

    def __str__(self):
        return "Ontology Term: " + self.iri + ", Type: " + self.term_type + ", Labels: " + str(self.labels) + \
               ", Synonyms: " + str(self.synonyms) + ", Definitions: " + str(self.definitions) + \
               ", Parents: " + str(self.parents) + ", Children: " + str(self.children) + \
               ", Instances: " + str(self.instances) + ", Restrictions: " + str(self.restrictions)
