"""Provides Mapper enum"""

from enum import Enum


class Mapper(str, Enum):
    """ Enumeration of "mappers" (ie string similarity metrics and Web APIs) available """
    LEVENSHTEIN = 'levenshtein'
    JARO = 'jaro'
    JARO_WINKLER = 'jarowinkler'
    JACCARD = 'jaccard'
    INDEL = 'indel'
    FUZZY = 'fuzzy'
    TFIDF = 'tfidf'
    ZOOMA = 'zooma'
    BIOPORTAL = 'bioportal'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
