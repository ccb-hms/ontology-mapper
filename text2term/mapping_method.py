"""Provides MappingMethod enum"""

from enum import Enum


class MappingMethod(Enum):
    LEVENSHTEIN = 'levenshtein'
    JARO = 'jaro'
    JARO_WINKLER = 'jarowinkler'
    JACCARD = 'jaccard'
    FUZZY = 'fuzzy'
    FUZZY_WEIGHTED = 'fuzzyw'
    TFIDF = 'tfidf'
    ZOOMA = 'zooma'
    BIOPORTAL = 'bioportal'
