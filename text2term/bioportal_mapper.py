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

    def map(self, source_terms, ontologies, max_mappings=3, api_params=()):
        """
        Find and return ontology mappings through the BioPortal Annotator Web service
        :param source_terms: Collection of source terms to map to target ontologies
        :param ontologies: String with a comma-separated list of ontology acronyms (eg "HP,EFO")
        :param max_mappings: The maximum number of (top scoring) ontology term mappings that should be returned
        :param api_params: Additional BioPortal Annotator-specific parameters to include in the request
        """
        self.logger.info("Mapping %i source terms against ontologies: %s...", len(source_terms), ontologies)
        start = time.time()
        mappings = []
        for term in source_terms:
            mappings.extend(self._map_term(term, ontologies, max_mappings, api_params))
        self.logger.info('done (mapping time: %.2fs seconds)', time.time()-start)
        return TermMappingCollection(mappings).mappings_df()

    def _map_term(self, source_term, ontologies, max_mappings, api_params):
        params = {
            "text": source_term,
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
                    mappings.append(self._mapping_details(source_term, mapping).as_term_mapping())
        return mappings

    def _mapping_details(self, text, annotation):
        ann_class = annotation["annotatedClass"]
        term_iri = ann_class["@id"]
        term_link_bp = ann_class["links"]["self"]
        onto_iri = ann_class["links"]["ontology"]
        onto_name = onto_utils.curie_from_iri(term_iri)
        bp_link = ann_class["links"]["ui"]
        match_type = annotation["annotations"][0]["matchType"]
        term_name, term_definition, ancestors = self.get_term_details(term_link_bp)
        return BioPortalMapping(text, term_name, term_iri, term_definition, ancestors, onto_iri, onto_name, bp_link,
                                match_type)

    def get_term_details(self, term_iri):
        response = self._do_get_request(term_iri)
        term_name, term_definition = "", ""
        ancestors = []
        if response is not None:
            term_name = onto_utils.remove_quotes(response["prefLabel"])
            if len(response["definition"]) > 0:
                term_definition = response["definition"][0]
                term_definition = onto_utils.remove_quotes(term_definition)
            ancestors_link = response["links"]["ancestors"]
            ancestors = self._get_ancestors(ancestors_link)
        return term_name, term_definition, ancestors

    def _get_ancestors(self, term_ancestors_bp_link):
        response = self._do_get_request(term_ancestors_bp_link)
        ancestors = []
        if response is not None:
            for ancestor in response:
                if ancestor is not None:
                    ancestor_name = ancestor["prefLabel"]
                    ancestors.append(ancestor_name)
        ancestors = list(dict.fromkeys(ancestors))  # remove duplicate ancestors
        return ancestors

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


class BioPortalMapping:

    def __init__(self, original_text, term_name, term_iri, term_definition, term_ancestors, ontology_iri, ontology_name,
                 bioportal_link, match_type):
        self.original_text = original_text
        self.term_name = term_name
        self.term_iri = term_iri
        self.term_definition = term_definition
        self.term_ancestors = term_ancestors
        self.ontology_iri = ontology_iri
        self.ontology_name = ontology_name
        self.bioportal_link = bioportal_link
        self.match_type = match_type

    def as_term_mapping(self):
        return TermMapping(self.original_text, self.term_name, self.term_iri, self.ontology_iri, self.mapping_score)

    @property
    def mapping_score(self):
        return 1  # if SYN|PREF
