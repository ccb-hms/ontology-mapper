"""Provides ZoomaMapper class"""

import json
import logging
import time
import requests
from text2term import onto_utils
from text2term.term_mapping import TermMappingCollection, TermMapping


class ZoomaMapper:

    def __init__(self):
        self.logger = onto_utils.get_logger(__name__, logging.INFO)
        self.url = "http://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate"

    def map(self, source_terms, source_terms_ids, ontologies, max_mappings=3, api_params=()):
        """
        Find and return ontology mappings through the Zooma Web service
        :param source_terms: Collection of source terms to map to target ontologies
        :param source_terms_ids: List of identifiers for the given source terms
        :param ontologies: Comma-separated list of ontology acronyms (eg 'HP,EFO') or 'all' to search all ontologies
        :param max_mappings: The maximum number of (top scoring) ontology term mappings that should be returned
        :param api_params: Additional Zooma API-specific parameters to include in the request
        """
        self.logger.info("Mapping %i source terms against ontologies: %s...", len(source_terms), ontologies)
        start = time.time()
        mappings = []
        for term, term_id in zip(source_terms, source_terms_ids):
            mappings.extend(self._map_term(term, term_id, ontologies, max_mappings, api_params))
        self.logger.info('done (mapping time: %.2fs seconds)', time.time()-start)
        return TermMappingCollection(mappings).mappings_df()

    def _map_term(self, source_term, source_term_id, ontologies, max_mappings, api_params):
        # see https://www.ebi.ac.uk/spot/zooma/docs/api for details of API parameters
        params = {
            "propertyValue": onto_utils.normalize(source_term),
            "filter": "required:[gwas,cttv,atlas,eva-clinvar,sysmicro],ontologies:[" + ontologies + "]"
        }
        if len(api_params) > 0:
            params.update(api_params)
        self.logger.debug("API parameters: " + str(params))
        mappings = []
        self.logger.debug("Searching for ontology terms to match: " + source_term)
        response = self._do_get_request(self.url, params=params)
        if response is not None:
            self.logger.debug("...found " + str(len(response)) + " mappings")
            for mapping in response:
                if len(mappings) < max_mappings:
                    mappings.append(self._mapping_details(source_term, source_term_id, mapping))
        return mappings

    def _mapping_details(self, source_term, source_term_id, mapping_response):
        # get ontology term label
        ann_class = mapping_response["annotatedProperty"]
        term_label = ann_class["propertyValue"]

        # get ontology term IRI
        tags = mapping_response["semanticTags"]
        term_iri = tags[0]

        mapping_score = self._mapping_score(mapping_response["confidence"])
        return TermMapping(source_term, source_term_id, term_label, term_iri, mapping_score)

    def _mapping_score(self, confidence):
        """Represent numerically the mapping confidence categories returned by Zooma (high, good, medium or low)"""
        if confidence == "HIGH":
            return 1.0
        elif confidence == "GOOD":
            return 0.75
        elif confidence == "MEDIUM":
            return 0.5
        elif confidence == "LOW":
            return 0.25
        else:
            return 0

    def _do_get_request(self, request_url, params=None):
        response = requests.get(request_url, params=params, verify=True)
        if response.ok:
            json_resp = json.loads(response.content)
            if len(json_resp) > 0:
                return json_resp
            else:
                self.logger.info("Empty response for input: " + request_url + " with parameters " + str(params))
        else:
            json_resp = json.loads(response.content)
            self.logger.error(response.reason + ":" + request_url + ". " + json_resp["errors"][0])
