"""Provides BioPortalAnnotatorMapper class"""

import json
import logging
import time
import requests
from text2term.term_mapping import TermMapping, TermMappingCollection
from text2term import onto_utils


class BioPortalAnnotatorMapper:

    def __init__(self, bp_api_key):
        """
        :param bp_api_key: BioPortal API key
        """
        self.logger = onto_utils.get_logger(__name__, logging.INFO)
        self.url = "http://data.bioontology.org/annotator"
        self.bp_api_key = bp_api_key

    def map(self, source_terms, source_terms_ids, ontologies, max_mappings=3, api_params=()):
        """
        Find and return ontology mappings through the BioPortal Annotator Web service
        :param source_terms: Collection of source terms to map to target ontologies
        :param source_terms_ids: List of identifiers for the given source terms
        :param ontologies: Comma-separated list of ontology acronyms (eg 'HP,EFO') or 'all' to search all ontologies.
            The ontology names accepted must match the names used in BioPortal. Here are some known ontologies:
            GO, UBERON, "CL" for Cell Ontology, MESH, SNOMEDCT, FMA, NCIT, EFO, DOID, MONDO, "PR" for Protein Ontology,
            "HP" for Human Phenotype Ontology
        :param max_mappings: The maximum number of (top scoring) ontology term mappings that should be returned
        :param api_params: Additional BioPortal Annotator-specific parameters to include in the request
        """
        self.logger.info("Mapping %i source terms against ontologies: %s...", len(source_terms), ontologies)
        start = time.time()
        mappings = []
        for term, term_id in zip(source_terms, source_terms_ids):
            mappings.extend(self._map_term(term, term_id, ontologies, max_mappings, api_params))
        self.logger.info('done (mapping time: %.2fs seconds)', time.time()-start)
        return TermMappingCollection(mappings).mappings_df()

    def _map_term(self, source_term, source_term_id, ontologies, max_mappings, api_params):
        params = {
            "text": onto_utils.normalize(source_term),
            "longest_only": "true",
            "expand_mappings": "true",
            "ontologies": ontologies
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

    def _mapping_details(self, source_term, source_term_id, mapping):
        ann_class = mapping["annotatedClass"]
        term_iri = ann_class["@id"]
        term_link_bp = ann_class["links"]["self"]
        term_label = self.get_term_details(term_link_bp)
        return TermMapping(source_term, source_term_id, term_label, term_iri, 1)

    def get_term_details(self, term_iri):
        response = self._do_get_request(term_iri)
        term_label = ""
        if response is not None:
            term_label = onto_utils.remove_quotes(response["prefLabel"])
        return term_label

    def _do_get_request(self, request_url, params=None):
        headers = {
            "Authorization": "apiKey token=" + self.bp_api_key,
        }
        response = requests.get(request_url, params=params, headers=headers, verify=True)
        if response.ok:
            json_resp = json.loads(response.content)
            if len(json_resp) > 0:
                return json_resp
            else:
                self.logger.info("Empty response for input: " + request_url + " with parameters " + str(params))
        elif response.status_code == 429:  # API is throttling requests
            self.logger.info(response.reason + ". Status code: " + str(response.status_code) + ". Waiting 15 seconds.")
            time.sleep(15)
            return self._do_get_request(request_url, params)
        else:
            json_resp = json.loads(response.content)
            self.logger.error(response.reason + ":" + request_url + ". " + json_resp["errors"][0])
