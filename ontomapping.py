"""Provides TermMapping and TermMappingCollection classes"""

import pandas as pd


class TermMapping:

    def __init__(self, source_term, mapped_term_label, mapped_term_iri, mapped_ontology_iri, mapping_score):
        self._source_term = source_term
        self._mapped_term_label = mapped_term_label
        self._mapped_term_iri = mapped_term_iri
        self._mapped_ontology_iri = mapped_ontology_iri
        self._mapping_score = mapping_score

    @property
    def source_term(self):
        return self._source_term

    @property
    def mapped_term_label(self):
        return self._mapped_term_label

    @property
    def mapped_term_iri(self):
        return self._mapped_term_iri

    @property
    def mapped_ontology_iri(self):
        return self._mapped_ontology_iri

    @property
    def mapping_score(self):
        return self._mapping_score

    def to_dict(self):
        return {
            'Source Term': self.source_term,
            'Mapped Term Label': self.mapped_term_label,
            'Mapped Term IRI': self.mapped_term_iri,
            'Mapped Ontology IRI': self.mapped_ontology_iri,
            'Mapping Score': self.mapping_score
        }

    def __eq__(self, other):
        if isinstance(other, TermMapping):
            return self.source_term == other.source_term and self.mapped_term_iri == other.mapped_term_iri
        return False

    def __str__(self):
        return "Mapping: " + self.source_term + " -> " + self._mapped_term_label + \
               " (" + self.mapped_term_iri + ")"


class TermMappingCollection:

    def __init__(self, mappings):
        self._mappings = mappings

    @property
    def mappings(self):
        return self._mappings

    def mappings_df(self):
        return pd.DataFrame([m.to_dict() for m in self.mappings])
