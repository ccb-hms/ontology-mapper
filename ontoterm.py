"""Provides OntologyTerm class"""

import ontoutils
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
        """ Build and return a graph representing the neighborhood of an ontology term. """
        nodes, edges = set(), set()
        nodes.add(Node(self.iri, self.label))
        self._add_superclasses(nodes, edges)
        self._add_subclasses(self.children, nodes, edges)
        self._add_instances(self.instances, nodes, edges)
        return OntologyTermGraph(self.iri, nodes, edges)

    def _add_superclasses(self, nodes, edges):
        for parent in self.parents:
            self._add_node(parent, nodes)
            edges.add(Edge(self.iri, parent.iri, Edge.IS_A))
            self._add_ancestors(parent, nodes, edges)

    def _add_ancestors(self, node, nodes, edges):
        for ancestor in node.is_a:
            if ancestor is not Thing and isinstance(ancestor, ThingClass):
                self._add_node(ancestor, nodes)
                edges.add(Edge(node.iri, ancestor.iri, Edge.IS_A))
                self._add_ancestors(ancestor, nodes, edges)

    def _add_children(self, term_list, edge_type, nodes, edges):
        for term in term_list:
            self._add_node(term, nodes)
            edges.add(Edge(term.iri, self.iri, edge_type))

    def _add_subclasses(self, subclasses, nodes, edges):
        self._add_children(subclasses, Edge.IS_A, nodes, edges)

    def _add_instances(self, instances, nodes, edges):
        self._add_children(instances, Edge.INSTANCE_OF, nodes, edges)

    def _add_node(self, term, term_set):
        if len(term.label) == 0:
            label = ontoutils.label_from_iri(term.iri)
        else:
            label = term.label[0]
        term_set.add(Node(term.iri, label))

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
        return "Ontology Term IRI: " + self.iri + ", Labels: " + str(self.labels) + ", Synonyms: " + \
               str(self.synonyms) + ", Definition: " + str(self.definition) + ", Parents: " + str(self.parents) + \
               ", Children: " + str(self.children) + ", Instances: " + str(self.instances) + ", Term graph: " + \
               str(self.graph().graph_dict())
