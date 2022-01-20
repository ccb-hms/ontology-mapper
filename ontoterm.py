class OntologyTerm:
    """
    Represents an ontology class or individual. In the case of an individual 'children' is always empty and
    'parents' specifies the individual's types.
    """
    def __init__(self, iri, labels, ontology_iri, parents=(), children=(), siblings=()):
        self._iri = iri
        self._labels = labels
        self._ontology_iri = ontology_iri
        self._parents = parents
        self._children = children
        self._siblings = siblings

    @property
    def iri(self):
        return self._iri

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels

    @property
    def ontology_iri(self):
        return self._ontology_iri

    @property
    def parents(self):
        return self._parents

    @property
    def children(self):
        return self._children

    @property
    def siblings(self):
        return self._siblings

    @property
    def label(self):
        """Return a single label for this term if one exists, otherwise return empty string"""
        if len(self.labels) > 0:
            return self.labels[0]
        else:
            return ""

    def __eq__(self, other):
        if isinstance(other, OntologyTerm):
            return self._iri == other._iri
        return False

    def __hash__(self):
        return hash(str(self._iri))
