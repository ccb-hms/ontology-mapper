# text2term ontology mapper

A tool for mapping (uncontrolled) terms to ontology terms to facilitate semantic integration. 

## Usage

Install package using **pip**:

`pip install .`

Execute the tool as follows:

`text2term -s SOURCE -t TARGET [-o OUTPUT] [-top TOP_MAPPINGS] [-min MIN_SCORE] [-iris BASE_IRIS] [-d EXCL_DEPRECATED] [-i INCL_INDIVIDUALS]`

To display a help message with descriptions of tool arguments do:

`text2term -h` or `text2term --help`

### Required arguments
`-s SOURCE` Input file containing 'source' terms to map to ontology terms (list of terms or CSV file).

`-t TARGET` Path or URL of 'target' ontology to map source terms to. When the chosen mapper is BioPortal or Zooma, provide a comma-separated list of acronyms (eg 'EFO,HPO') or write `'all'` to search all ontologies.

### Optional arguments

`-o OUTPUT` Path to desired output file for the mappings.

`-m MAPPER` Method used to compare source terms with ontology terms. One of: *levenshtein, jaro, jarowinkler, jaccard, fuzzy, tfidf, zooma, bioportal*.

`-csv CSV_INPUT` Indicates a CSV format input—follow with the name of the column containing terms to map, optionally followed by the name of the column containing identifiers for the terms (eg 'my terms,my term ids').

`-top TOP_MAPPINGS` Maximum number of top-ranked mappings returned per source term.

`-min MIN_SCORE` Minimum similarity score [0,1] for the mappings (1=exact match).

`-iris BASE_IRIS` Map only to ontology terms whose IRIs start with a value given in this comma-separated list (eg 'http://www.ebi.ac.uk/efo,http://purl.obolibrary.org/obo/HP)').

`-d EXCL_DEPRECATED` Exclude ontology terms stated as deprecated via `owl:deprecated true`.

`-g SAVE_TERM_GRAPHS` Save [vis.js](https://visjs.org) graphs representing the neighborhood of each ontology term.


## Examples

The basic use of the tool requires a `source` file containing a list of terms to map to the given `target` ontology:  
`python text2term -s unstruct_terms.txt -t http://www.ebi.ac.uk/efo/efo.owl`

Specify an output file where the mappings should be saved using `-o`:  
`python text2term -s unstruct_terms.txt -t efo.owl -o /Documents/my-mappings.csv`

Set the minimum acceptable similarity score for mapping each given term to an ontology term using `-min`:  
`python text2term -s unstruct_terms.txt -t efo.owl -min 0.8`  
The mapped terms returned will have been determined to be 0.8 similar to their source terms in a 0-1 scale.  

Exclude deprecated ontology terms (declared as such via *owl:deprecated true*) using `-d`:  
`python text2term -s unstruct_terms.txt -t efo.owl -d`

Limit search to only terms whose IRIs start with any IRI given in a list specified using `-iris`:  
`python text2term.py -s unstruct_terms.txt -t efo.owl -iris http://www.ebi.ac.uk/efo/EFO,http://purl.obolibrary.org/obo/HP`  
Here, because EFO reuses terms from other ontologies such as HP and GO, the HP terms would be included but the GO terms would be excluded.
