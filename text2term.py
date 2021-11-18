import argparse
import datetime
import os
import sys
import ontoutils
from ontotermcollector import OntologyTermCollector
from newmapper import TFIDFMapper
from biobert import biobert_mapper

def get_arguments():
    timestamp = datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    output_file_name = "t2t-out-" + timestamp + ".csv"
    parser = argparse.ArgumentParser(description="A tool to map unstructured terms to ontology terms")
    parser.add_argument("-s", "--source", required=True, type=str,
                        help="Input file containing list of 'source' terms to map to ontology terms (one per line)")
    parser.add_argument("-t", "--target", required=True, type=str,
                        help="Path or URL of 'target' ontology to map the source terms to")
    parser.add_argument("-o", "--output", required=False, type=str, default=output_file_name,
                        help="Path to desired output file for the mappings (default=current working directory)")
    parser.add_argument("-top", "--top_mappings", required=False, type=int, default=3,
                        help="Maximum number of top-ranked mappings returned per source term (default=3)")
    parser.add_argument("-min", "--min_score", required=False, type=float, default=0.5,
                        help="Minimum score [0,1] for the mappings (0=dissimilar, 1=exact match; default=0.5)")
    parser.add_argument("-iri", "--base_iri", required=False, type=str,
                        help="Restricts ontology term mapping to those terms whose IRIs start with the given base IRI")
    parser.add_argument("-d", "--excl_deprecated", required=False, default=False, action="store_true",
                        help="Exclude terms stated as deprecated via owl:deprecated")
    parser.add_argument("-i", "--incl_individuals", required=False, default=False, action="store_true",
                        help="Include ontology individuals in addition to classes")
    arguments = parser.parse_args()

    source_file, target_file, out_file = arguments.source, arguments.target, arguments.output
    if not os.path.exists(source_file):
        parser.error("The file '{}' does not exist".format(source_file))
        sys.exit(1)

    # create output directories if needed
    if os.path.dirname(out_file):
        os.makedirs(os.path.dirname(out_file), exist_ok=True)

    return source_file, target_file, out_file, arguments.top_mappings, arguments.min_score, arguments.base_iri, \
        arguments.excl_deprecated, arguments.incl_individuals


# if __name__ == "__main__":

    # input_file, target_ontology, output_file, max_mappings, min_score, base_iri, excl_deprecated, incl_individuals = get_arguments()
    # source_terms = ontoutils.parse_list_file(input_file)
    # biobert_mapper(source_terms)
    # term_collector = OntologyTermCollector(target_ontology)
    # onto_terms = term_collector.get_ontology_terms(base_iri=base_iri,
    #                                                exclude_deprecated=excl_deprecated,
    #                                                include_individuals=incl_individuals)
    # mapper = TFIDFMapper(onto_terms)
    # mappings_df = mapper.map(source_terms, max_mappings=max_mappings, min_score=min_score)
    # mappings_df.to_csv(output_file, index=False)
if __name__ == "__main__":
    # input_file, target_ontology, output_file, max_mappings, min_score, base_iri, excl_deprecated, incl_individuals = get_arguments()
    # source_terms = ontoutils.parse_list_file(input_file)
    # biobert_mapper(source_terms)
    

    input_file, target_ontology, output_file, max_mappings, min_score, base_iri, excl_deprecated, incl_individuals = get_arguments()
    source_terms = ontoutils.parse_list_file(input_file)
    term_collector = OntologyTermCollector(target_ontology)
    onto_terms = term_collector.get_ontology_terms(base_iri=base_iri,
                                                   exclude_deprecated=excl_deprecated,
                                                   include_individuals=incl_individuals)
    mapper = TFIDFMapper(onto_terms)
    mappings_df = mapper.map(source_terms, max_mappings=max_mappings, min_score=min_score)
    mappings_df.to_csv(output_file, index=False)