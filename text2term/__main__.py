import argparse
import os
import sys
from t2t import map_file
from mapper import Mapper

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A tool for mapping free-text descriptions of (biomedical) '
                                                 'entities to controlled terms in an ontology')
    parser.add_argument("-s", "--source", required=True, type=str,
                        help="Input file containing 'source' terms to map to ontology terms (list of terms or CSV file)")
    parser.add_argument("-t", "--target", required=True, type=str,
                        help="Path or URL of 'target' ontology to map source terms to. When the chosen mapper is "
                             "BioPortal or Zooma, provide a comma-separated list of acronyms (eg 'EFO,HPO') or write "
                             "'all' to search all ontologies")
    parser.add_argument("-o", "--output", required=False, type=str, default="",
                        help="Path to desired output file for the mappings (default=current working directory)")
    parser.add_argument("-m", "--mapper", required=False, type=str, default="tfidf",
                        help="Method used to compare source terms with ontology terms. One of: " + str(Mapper.list()) +
                             " (default=tfidf)")
    parser.add_argument("-csv", "--csv_input", required=False, type=str, default=(),
                        help="Specifies that the input is a CSV file—This should be followed by the name of the column "
                             "that contains the terms to map, optionally followed by the name of the column that "
                             "contains identifiers for the terms (eg 'my_terms,my_term_ids')")
    parser.add_argument("-sep", "--separator", required=False, type=str, default=',',
                        help="Specifies the cell separator to be used when reading a non-comma-separated tabular file")
    parser.add_argument("-top", "--top_mappings", required=False, type=int, default=3,
                        help="Maximum number of top-ranked mappings returned per source term (default=3)")
    parser.add_argument("-min", "--min_score", required=False, type=float, default=0.5,
                        help="Minimum similarity score [0,1] for the mappings (1=exact match; default=0.5)")
    parser.add_argument("-iris", "--base_iris", required=False, type=str, default=(),
                        help="Map only to ontology terms whose IRIs start with a value given in this comma-separated "
                             "list (eg 'http://www.ebi.ac.uk/efo,http://purl.obolibrary.org/obo/HP)')")
    parser.add_argument("-d", "--excl_deprecated", required=False, default=False, action="store_true",
                        help="Exclude ontology terms stated as deprecated via `owl:deprecated true` (default=False)")
    parser.add_argument("-g", "--save_term_graphs", required=False, default=False, action="store_true",
                        help="Save vis.js graphs representing the neighborhood of each ontology term (default=False)")

    # TODO mapping to a cached ontology should be possible through the command-line interface
    parser.add_argument("-rc", "--read_from_cache", required=False, default=False, action="store_true",
                        help="Load the target ontology from local cache")
    # TODO writing to cache is an entirely different operation (mapping has 2 required arguments, caching has none)...
    parser.add_argument("-wc", "--write_cache", required=False, default=False, action="store_true",
                        help="Write a local cache of ontology term details from the ontologies specified in the file: "
                             "'resources/ontologies.csv' for faster performance when mapping terms to those ontologies")
    arguments = parser.parse_args()
    if not os.path.exists(arguments.source):
        parser.error("The file '{}' does not exist".format(arguments.source))
        sys.exit(1)
    mapper = Mapper(arguments.mapper)
    iris = arguments.base_iris
    if len(iris) > 0:
        iris = tuple(iris.split(','))
    csv_columns = arguments.csv_input
    if len(csv_columns) > 0:
        csv_columns = tuple(csv_columns.split(','))
    map_file(arguments.source, arguments.target, output_file=arguments.output, csv_columns=csv_columns,
                         excl_deprecated=arguments.excl_deprecated, mapper=mapper, max_mappings=arguments.top_mappings,
                         min_score=arguments.min_score, base_iris=iris, save_graphs=arguments.save_term_graphs,
                         save_mappings=True, separator=arguments.separator)
