from text2term import onto_utils
from text2term.term_graph import TermGraph, Node, Edge
from owlready2 import Thing, ThingClass


class TermGraphGenerator:

    def __init__(self):
        pass

    def graph(self, term):
        """ Build and return a graph representing the neighborhood of an ontology term. """
        nodes, edges = set(), set()
        nodes.add(Node(term.iri, term.label))
        self._add_superclasses(term, nodes, edges)
        self._add_subclasses(term, term.children, nodes, edges)
        self._add_instances(term, term.instances, nodes, edges)
        return TermGraph(term.iri, nodes, edges)

    def _add_superclasses(self, term, nodes, edges):
        for parent in term.parents:
            self._add_node(parent, nodes)
            edges.add(Edge(term.iri, parent.iri, Edge.IS_A))
            self._add_ancestors(parent, nodes, edges)

    def _add_ancestors(self, node, nodes, edges):
        for ancestor in node.is_a:
            if ancestor is not Thing and isinstance(ancestor, ThingClass):
                self._add_node(ancestor, nodes)
                edges.add(Edge(node.iri, ancestor.iri, Edge.IS_A))
                self._add_ancestors(ancestor, nodes, edges)

    def _add_children(self, term, children, edge_type, nodes, edges):
        for child in children:
            self._add_node(child, nodes)
            edges.add(Edge(child.iri, term.iri, edge_type))

    def _add_subclasses(self, term, subclasses, nodes, edges):
        self._add_children(term, subclasses, Edge.IS_A, nodes, edges)

    def _add_instances(self, term, instances, nodes, edges):
        self._add_children(term, instances, Edge.INSTANCE_OF, nodes, edges)

    def _add_node(self, term, term_set):
        if len(term.label) == 0:
            label = onto_utils.label_from_iri(term.iri)
        else:
            label = term.label[0]
        term_set.add(Node(term.iri, label))

    def graphs_dicts(self, terms):
        """Convenience function to get a list of all term graphs' dictionary representations"""
        graph_dicts = []
        for term in terms:
            graph_dicts.append(self.graph(term).as_dict())
        return graph_dicts
