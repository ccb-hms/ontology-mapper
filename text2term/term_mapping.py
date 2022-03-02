"""Provides TermMapping and TermMappingCollection classes"""

import pandas as pd


class TermMapping:
    SRC_TERM = "Source Term"
    TGT_TERM_LBL = "Mapped Term Label"
    TGT_TERM_IRI = "Mapped Term IRI"
    TGT_TERM_ONT_IRI = "Mapped Ontology IRI"
    MAPPING_SCORE = "Mapping Score"

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
            self.SRC_TERM: self.source_term,
            self.TGT_TERM_LBL: self.mapped_term_label,
            self.TGT_TERM_IRI: self.mapped_term_iri,
            self.TGT_TERM_ONT_IRI: self.mapped_ontology_iri,
            self.MAPPING_SCORE: self.mapping_score
        }

    def __eq__(self, other):
        if isinstance(other, TermMapping):
            return self.source_term == other.source_term and self.mapped_term_iri == other.mapped_term_iri
        return False

    def __str__(self):
        return self.source_term + " -> " + self._mapped_term_label + " (" + self.mapped_term_iri + ")"


class TermMappingCollection:

    def __init__(self, mappings):
        self._mappings = mappings

    @property
    def mappings(self):
        return self._mappings

    def mappings_df(self):
        return pd.DataFrame([m.to_dict() for m in self.mappings])
