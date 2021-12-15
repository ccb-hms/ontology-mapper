from owlready2 import Thing, ThingClass
from ontotermgraph import OntologyTermGraph, Node, Edge


class OntologyTerm:
    """
    Represents an ontology class or individual. In the case of an individual 'children' is always empty and
    'parents' specifies the individual's types.
    """
    def __init__(self, iri, labels, synonyms, definition, ontology_iri, parents=(), children=(), instances=()):
        self._iri = iri
        self._labels = labels
        self._synonyms = synonyms
        self._definition = definition
        self._ontology_iri = ontology_iri
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
    def ontology_iri(self):
        return self._ontology_iri

    @property
    def parents(self):
        return self._parents

    @property
    def children(self):
        return self._children

    @property
    def instances(self):
        return self._instances

    def graph(self):
        nodes, edges = set(), set()
        nodes.add(Node(self.iri, self.label))
        for child in self.children:
            nodes.add(Node(child.iri, child.label[0]))
            edges.add(Edge(child.iri, self.iri, IS_A))
        for parent in self.parents:
            nodes.add(Node(parent.iri, parent.label[0]))
            edges.add(Edge(self.iri, parent.iri, IS_A))
            self._ancestors(parent, nodes, edges)
        for instance in self.instances:
            nodes.add(Node(instance.iri, instance.label[0]))
            edges.add(Edge(instance.iri, self.iri, INSTANCE_OF))
        return OntologyTermGraph(self.iri, nodes, edges)

    def _ancestors(self, node, nodes, edges):
        for ancestor in node.is_a:
            if ancestor is not Thing and isinstance(ancestor, ThingClass):
                nodes.add(Node(ancestor.iri, ancestor.label[0]))
                edges.add(Edge(node.iri, ancestor.iri, IS_A))
                self._ancestors(ancestor, nodes, edges)

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

    def __str__(self):
        return "Ontology Term IRI: " + self.iri + ", Labels: " + str(self.labels) + ", Synonyms: " + \
               str(self.synonyms) + ", Definition: " + str(self.definition) + ", Parents: " + str(self.parents) + \
               ", Children: " + str(self.children) + ", Instances: " + str(self.instances) + ", Term graph: " + \
               str(self.graph().graph_dict())


INSTANCE_OF = "INSTANCE_OF"
IS_A = "IS_A"
