import argparse
import datetime
import json
import os
import sys
import onto_utils
from term_collector import OntologyTermCollector
from term_graph_generator import TermGraphGenerator
from tfidf_mapper import TFIDFMapper


def get_arguments():
    timestamp = datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    output_file_name = "t2t-mappings-" + timestamp + ".csv"
    parser = argparse.ArgumentParser(description="A tool to map unstructured terms to ontology terms")
    parser.add_argument("-s", "--source", required=True, type=str,
                        help="Input file containing list of 'source' terms to map to ontology terms (one per line)")
    parser.add_argument("-t", "--target", required=True, type=str,
                        help="Path or URL of 'target' ontology to map the source terms to")
    parser.add_argument("-o", "--output", required=False, type=str, default=output_file_name,
                        help="Path to desired output file for the mappings (default=current working directory)")
    parser.add_argument("-csv", "--csv_input", required=False, type=str, default=(),
                        help="Specifies that the input is a CSV file—This should be followed by the name of the column "
                             "that contains the terms to map, optionally followed by the name of the column that "
                             "contains identifiers for the terms (eg 'my_terms,my_term_ids')")
    parser.add_argument("-top", "--top_mappings", required=False, type=int, default=3,
                        help="Maximum number of top-ranked mappings returned per source term (default=3)")
    parser.add_argument("-min", "--min_score", required=False, type=float, default=0.5,
                        help="Minimum score [0,1] for the mappings (0=dissimilar, 1=exact match; default=0.5)")
    parser.add_argument("-iris", "--base_iris", required=False, type=str, default=(),
                        help="Map only to terms whose IRIs start with any IRI given in this comma-separated list")
    parser.add_argument("-d", "--excl_deprecated", required=False, default=False, action="store_true",
                        help="Exclude terms stated as deprecated via owl:deprecated")
    parser.add_argument("-g", "--save_term_graphs", required=False, default=False, action="store_true",
                        help="Save the graphs representing the neighborhood of each ontology term")
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

    csv_column_names = arguments.csv_input
    if len(csv_column_names) > 0:
        csv_column_names = tuple(csv_column_names.split(','))

    return source_file, target_file, out_file, arguments.top_mappings, arguments.min_score, iris, csv_column_names, \
        arguments.excl_deprecated, arguments.save_term_graphs


def process_source_file(input_file_path, csv_column_names):
    if len(csv_column_names) >= 1:
        term_id_col_name = ""
        if len(csv_column_names) == 2:
            term_id_col_name = csv_column_names[1]
        terms, term_ids = onto_utils.parse_csv_file(input_file_path,
                                                    term_column_name=csv_column_names[0],
                                                    term_id_column_name=term_id_col_name)
    else:
        terms = onto_utils.parse_list_file(input_file_path)
        term_ids = onto_utils.generate_iris(len(terms))
    return terms, term_ids


def process_target_ontology(ontology, iris, exclude_deprecated, save_term_graphs):
    term_collector = OntologyTermCollector(ontology)
    onto_terms = term_collector.get_ontology_terms(base_iris=iris, exclude_deprecated=exclude_deprecated)
    if len(onto_terms) == 0:
        raise RuntimeError("Could not find any terms in the given ontology.")
    if save_term_graphs:
        term_graphs = TermGraphGenerator().graphs_dicts(onto_terms)
        with open(output_file + "-term-graphs.json", 'w') as json_file:
            json.dump(term_graphs, json_file, indent=2)
    return onto_terms


def do_mapping(source_input_terms, source_input_term_ids, ontology_terms, max_mappings_per_term,
               min_mapping_score, mappings_output_file):
    mapper = TFIDFMapper(ontology_terms)
    mappings_df = mapper.map(source_input_terms, source_input_term_ids,
                             max_mappings=max_mappings_per_term,
                             min_score=min_mapping_score)
    mappings_df.to_csv(mappings_output_file, index=False)


if __name__ == "__main__":
    input_file, target_ontology, output_file, max_mappings, min_score, base_iris, \
        csv_columns, excl_deprecated, save_graphs = get_arguments()
    source_terms, source_term_ids = process_source_file(input_file, csv_columns)
    target_terms = process_target_ontology(target_ontology, base_iris, excl_deprecated, save_graphs)
    do_mapping(source_terms, source_term_ids, target_terms, max_mappings, min_score, output_file)
