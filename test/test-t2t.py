import text2term
from text2term import Mapper

text2term.map_file(input_file="/Users/rsgoncalves/Documents/Harvard/gwaslake/all-traits-list-July23.csv",
                   target_ontology="EFO", use_cache=True,
                   csv_columns=("trait", "trait_id"),
                   max_mappings=1,
                   min_score=0.6,
                   excl_deprecated=True,
                   separator=",",
                   save_mappings=True,
                   mapper=Mapper.TFIDF,
                   output_file="/Users/rsgoncalves/Documents/Workspace/text2term/test/output/opengwas-mappings.csv",
                   base_iris=("http://www.ebi.ac.uk/efo/", "http://purl.obolibrary.org/obo/MONDO",
                              "http://purl.obolibrary.org/obo/HP"),
                   save_graphs=False
                   )
