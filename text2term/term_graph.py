"""Provides TermGraph, Node and Edge classes"""


class TermGraph:
    """
    Represents a graph of the neighborhood of an ontology term.
    The graph includes all (direct and indirect) superclasses and all direct subclasses.
    """
    def __init__(self, term_iri, nodes, edges):
        self._term_iri = term_iri
        self._nodes = nodes
        self._edges = edges

    @property
    def term_iri(self):
        return self._term_iri

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    def as_dict(self):
        graph = {
            "iri": self.term_iri,
            "nodes": self._nodes_dict(),
            "edges": self._edges_dict()
        }
        return graph

    def _nodes_dict(self):
        nodes = []
        for node in self.nodes:
            node = {
                "id": node.identifier,
                "label": node.label
            }
            nodes.append(node)
        return nodes

    def _edges_dict(self):
        edges = []
        for edge in self.edges:
            edge = {
                "from": edge.from_node,
                "to": edge.to_node,
                "label": edge.label
            }
            edges.append(edge)
        return edges


class Node:
    """
    Represents a node corresponding to a term in an ontology term graph.
    """
    def __init__(self, identifier, label):
        self._identifier = identifier
        self._label = label

    @property
    def identifier(self):
        return self._identifier

    @property
    def label(self):
        return self._label

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.identifier == other.identifier
        return NotImplemented


class Edge:
    """
    Represents a labeled edge between two nodes in an ontology term graph.
    The 'from' and 'to' nodes are represented by their (IRI) identifiers.
    """
    def __init__(self, from_node, to_node, label):
        self._from_node = from_node
        self._to_node = to_node
        self._label = label

    @property
    def from_node(self):
        return self._from_node

    @property
    def to_node(self):
        return self._to_node

    @property
    def label(self):
        return self._label

    def __key(self):
        return self.from_node, self.to_node, self.label

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.__key() == other.__key()
        return NotImplemented

    INSTANCE_OF = "INSTANCE_OF"
    IS_A = "IS_A"
