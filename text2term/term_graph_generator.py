from text2term import onto_utils
from text2term.term_graph import TermGraph, Node, Edge

class TermGraphGenerator:

    def __init__(self, terms):
        self._terms = terms
        self._logger = onto_utils.get_logger(__name__)

    def graph(self, term):
        """ Build and return a graph representing the neighborhood of an ontology term. """
        nodes, edges = set(), set()
        nodes.add(Node(term.iri, term.label))
        self._add_superclasses(term, nodes, edges)
        self._add_subclasses(term, term.children, nodes, edges)
        self._add_instances(term, term.instances, nodes, edges)
        return TermGraph(term.iri, nodes, edges)

    def _add_superclasses(self, term, nodes, edges):
        parents = term.parents
        for parent_iri in parents:
            self._add_node(parent_iri, parents[parent_iri], nodes)
            edges.add(Edge(term.iri, parent_iri, Edge.IS_A))
            self._add_ancestors(parent_iri, nodes, edges)

    def _add_ancestors(self, node_iri, nodes, edges):
        if node_iri in self._terms:
            ancestors = self._terms[node_iri].parents
            for ancestor_iri in ancestors:
                self._add_node(ancestor_iri, ancestors[ancestor_iri], nodes)
                edges.add(Edge(node_iri, ancestor_iri, Edge.IS_A))
                self._add_ancestors(ancestor_iri, nodes, edges)
        else:
            self._logger.debug("Unable to get ancestor term %s from the ontology term details dictionary "
                               "(possibly filtered out through the `base_iris` option)", node_iri)

    def _add_children(self, term, children, edge_type, nodes, edges):
        for child_iri in children:
            self._add_node(child_iri, children[child_iri], nodes)
            edges.add(Edge(child_iri, term.iri, edge_type))

    def _add_subclasses(self, term, subclasses, nodes, edges):
        self._add_children(term, subclasses, Edge.IS_A, nodes, edges)

    def _add_instances(self, term, instances, nodes, edges):
        self._add_children(term, instances, Edge.INSTANCE_OF, nodes, edges)

    def _add_node(self, term_iri, term_label, nodes):
        if len(term_iri) > 0:
            if isinstance(term_label, list) and len(term_label) > 0:
                label = term_label[0]
            elif isinstance(term_label, str):
                label = term_label
            else:
                label = onto_utils.label_from_iri(term_iri)
            if label is not None and len(label) > 0:
                nodes.add(Node(term_iri, label))
            else:
                self._logger.debug("Label is null or empty for term " + term_iri)
        else:
            self._logger.debug("The given term has no IRI")

    def graphs_dicts(self):
        """Convenience function to get a list of all term graphs' dictionary representations"""
        graph_dicts = []
        for term in self._terms.values():
            graph_dicts.append(self.graph(term).as_dict())
        return graph_dicts
