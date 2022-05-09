"""Provides OntologyTerm class"""


class OntologyTerm:

    def __init__(self, iri, labels, synonyms, definition, parents=(), children=(), instances=()):
        self._iri = iri
        self._labels = labels
        self._synonyms = synonyms
        self._definition = definition
        self._parents = parents
        self._children = children
        self._instances = instances

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
    def definition(self):
        return self._definition

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

    def __eq__(self, other):
        if isinstance(other, OntologyTerm):
            return self._iri == other._iri
        return False

    def __hash__(self):
        return hash(str(self._iri))

    def __str__(self):
        return "Ontology Term: " + self.iri + ", Labels: " + str(self.labels) + ", Synonyms: " + \
               str(self.synonyms) + ", Definition: " + str(self.definition) + ", Parents: " + str(self.parents) + \
               ", Children: " + str(self.children) + ", Instances: " + str(self.instances)
