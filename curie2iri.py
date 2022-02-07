import datetime
import logging
import ssl
import sys
import urllib.request
from urllib.error import HTTPError
import pandas as pd
import onto_utils

ssl._create_default_https_context = ssl._create_stdlib_context


class OntoTag2Iri:

    def __init__(self):
        self.logger = onto_utils.get_logger(__name__, logging.INFO)

    def get_iris(self, source_tags, resolve_iri):
        iri_mappings = []
        for source_tag in source_tags:
            source_tag, iri, iri_resolves = self.get_iri(source_tag, resolve_iri)
            iri_mappings.append((source_tag, iri, iri_resolves))
        return iri_mappings

    def get_iri(self, source_tag, resolve_iri):
        iri = source_tag
        iri_resolves = False
        if len(source_tag) > 0 and source_tag != "NA":
            if ":" in source_tag:
                iri = self.remove_whitespace(iri)
                onto_name = iri.split(":")[0]
                term_name = iri.replace(":", "_")
                full_iri = self._get_iri(onto_name, term_name)
                iri = full_iri if len(full_iri) > 0 else iri
            elif "_" in source_tag:
                iri = self.remove_whitespace(iri)
                ont_name = iri.split("_")[0]
                full_iri = self._get_iri(ont_name, iri)
                iri = full_iri if len(full_iri) > 0 else iri
            if source_tag != iri:
                iri_resolves = self.resolves(iri) if resolve_iri else iri_resolves
            else:
                self.logger.info("Unable to find suitable IRI for: %s", source_tag)
        return source_tag, iri, iri_resolves

    def _get_iri(self, ont_name, term_name):
        iri = ''
        if ont_name in onto_utils.ONTOLOGY_IRIS:
            if ont_name == 'ORPHA':
                iri = onto_utils.ONTOLOGY_IRIS.get(ont_name) + term_name.replace('ORPHA_', 'Orphanet_')
            elif ont_name == 'SNOMED' or ont_name == 'OMIM':
                iri = onto_utils.ONTOLOGY_IRIS.get(ont_name) + term_name.replace(ont_name + '_', '')
            else:
                iri = onto_utils.ONTOLOGY_IRIS.get(ont_name) + term_name
        return iri

    def remove_whitespace(self, string):
        return string.replace(' ', '')

    def resolves(self, iri):
        resolves = False
        try:
            status_code = urllib.request.urlopen(iri).getcode()
            resolves = status_code == 200
        except HTTPError as err:
            self.logger.debug(err)
        if not resolves:
            self.logger.info("IRI does not resolve: %s", iri)
        return resolves

    def get_iris_df_for_file(self, input_file, resolve_iri):
        iris_file = self.get_iris(onto_utils.parse_list_file(input_file), resolve_iri=resolve_iri)
        out_col_names = ['source_tag', 'target_iri', 'iri_resolves']
        return pd.DataFrame(iris_file, columns=out_col_names)


if __name__ == "__main__":
    tag2iri = OntoTag2Iri()
    if len(sys.argv) > 1:
        input_tag_list_file = sys.argv[1]
        output_file = "tag2iri-" + datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S") + ".csv"
        output_df = tag2iri.get_iris_df_for_file(input_tag_list_file, resolve_iri=True)
        output_df.to_csv(output_file, index=False)
    else:
        print("Provide input file with tags to convert to IRIs")
