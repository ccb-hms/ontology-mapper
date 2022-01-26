import argparse
import datetime
import json
import os
import sys
import onto_utils
from term_collector import OntologyTermCollector
from tfidf_mapper import TFIDFMapper


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
    parser.add_argument("-iris", "--base_iris", required=False, type=str, default=(),
                        help="Map only to terms whose IRIs start with any IRI given in this comma-separated list")
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

    iris = arguments.base_iris
    if len(iris) > 0:
        iris = tuple(iris.split(','))
    return source_file, target_file, out_file, arguments.top_mappings, arguments.min_score, iris, \
        arguments.excl_deprecated, arguments.incl_individuals


if __name__ == "__main__":
    input_file, target_ontology, output_file, max_mappings, min_score, base_iris, excl_deprecated, incl_individuals = get_arguments()
    source_terms = onto_utils.parse_list_file(input_file)
    term_collector = OntologyTermCollector(target_ontology)
    onto_terms = term_collector.get_ontology_terms(base_iris=base_iris,
                                                   exclude_deprecated=excl_deprecated,
                                                   include_individuals=incl_individuals)
    if len(onto_terms) > 0:
        mapper = TFIDFMapper(onto_terms)
        mappings_df, term_graphs = mapper.map(source_terms, max_mappings=max_mappings, min_score=min_score)
        mappings_df.to_csv(output_file, index=False)
        with open(output_file + "-term-graphs.json", 'w') as json_file:
            json.dump(term_graphs, json_file, indent=2)
