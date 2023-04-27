"""Provides OntologyTerm class"""


class OntologyTerm:

    def __init__(self, iri, labels, definitions=(), synonyms=(), parents=(), children=(), instances=(), deprecated=False, termtype='class'):
        """
        Constructor for a succinct representation of an ontology term
        :param iri: IRI of the ontology term
        :param labels: Set of human-readable labels for the term (e.g., rdfs:label, skos:prefLabel)
        :param definitions: Set of textual definitions of the term
        :param synonyms: Set of synonyms of the term (e.g., alternative labels)
        :param parents: Dictionary containing the IRIs of parent terms (superclasses) and their label(s)
        :param children: Dictionary containing the IRIs of child terms (subclasses) and their label(s)
        :param instances: Dictionary containing the IRIs of instances of the term (rdf:type) and their label(s)
        """
        self._iri = iri
        self._labels = labels
        self._synonyms = synonyms
        self._definitions = definitions
        self._parents = parents
        self._children = children
        self._instances = instances
        self._deprecated = deprecated
        self._termtype = termtype

    @property
    def iri(self):
        return self._iri

    @property
    def labels(self):
        return self._labels

    @property
    def synonyms(self):
        return self._synonyms

    @property
    def definitions(self):
        return self._definitions

    @property
    def parents(self):
        return self._parents

    @property
    def children(self):
        return self._children

    @property
    def instances(self):
        return self._instances

    @property
    def label(self):
        """Return a single label for this term"""
        return next(iter(self.labels))

    @property
    def deprecated(self):
        return self._deprecated

    @property
    def termtype(self):
        return self._termtype

    def __eq__(self, other):
        if isinstance(other, OntologyTerm):
            return self._iri == other._iri
        return False

    def __hash__(self):
        return hash(str(self._iri))

    def __str__(self):
        return "Ontology Term: " + self.iri + ", Labels: " + str(self.labels) + ", Synonyms: " + \
               str(self.synonyms) + ", Definitions: " + str(self.definitions) + ", Parents: " + str(self.parents) + \
               ", Children: " + str(self.children) + ", Instances: " + str(self.instances)
