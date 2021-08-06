import argparse
import datetime
import os
import sys
import ontoutils
from tfidfmapper import TFIDFMapper


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
    parser.add_argument("-i", "--incl_individuals", required=False, type=bool, default=False,
                        help="Include ontology individuals in addition to classes (default=False)")
    arguments = parser.parse_args()

    source_file, target_file, out_file = arguments.source, arguments.target, arguments.output
    if not os.path.exists(source_file):
        parser.error("The file '{}' does not exist".format(source_file))
        sys.exit(1)

    # create output directories if needed
    if os.path.dirname(out_file):
        os.makedirs(os.path.dirname(out_file), exist_ok=True)

    return source_file, target_file, out_file, arguments.top_mappings, arguments.min_score, arguments.incl_individuals


if __name__ == "__main__":
    source_terms_file, target_ontology, output_file, max_mappings, min_score, incl_individuals = get_arguments()
    mapper = TFIDFMapper(ontoutils.parse_list_file(source_terms_file), target_ontology)
    mappings_df = mapper.map(max_mappings=max_mappings, min_score=min_score, incl_individuals=incl_individuals)
    mappings_df.to_csv(output_file, index=False)
