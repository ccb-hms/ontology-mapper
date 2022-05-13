"""Provides Mapper enum"""

from enum import Enum


class Mapper(str, Enum):
    """ Enumeration of "mappers" (ie string similarity metrics and Web APIs) available """
    LEVENSHTEIN = 'levenshtein'
    JARO = 'jaro'
    JARO_WINKLER = 'jarowinkler'
    JACCARD = 'jaccard'
    FUZZY = 'fuzzy'
    FUZZY_WEIGHTED = 'fuzzyw'
    TFIDF = 'tfidf'
    ZOOMA = 'zooma'
    BIOPORTAL = 'bioportal'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
