"""Provides SimilarityMetric enum"""

from enum import Enum


class SimilarityMetric(Enum):
    LEVENSHTEIN = 'leven'
    JARO = 'jaro'
    JARO_WINKLER = 'jarowinkler'
    JACCARD = 'jaccard'
    FUZZY = 'fuzzy'
    FUZZY_WEIGHTED = 'fuzzyw'
