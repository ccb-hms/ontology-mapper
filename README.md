# text2term Ontology Term Mapper

A tool to map unstructured terms to ontology terms. 

## Usage

`text2term.py -s SOURCE -t TARGET [-o OUTPUT] [-top TOP_MAPPINGS] [-min MIN_SCORE] [-iris BASE_IRIS] [-d EXCL_DEPRECATED] [-i INCL_INDIVIDUALS]`

### Required arguments
`-s SOURCE` Input file containing list of 'source' terms to map to ontology terms (one per line).

`-t TARGET` Path or URL of 'target' ontology to map the source terms to.

### Optional arguments

`-o OUTPUT` Path to desired output file for the mappings.

`-top TOP_MAPPINGS` Maximum number of top-ranked mappings returned per source term.

`-min MIN_SCORE` Minimum score [0,1] for the mappings (0=dissimilar, 1=exact match).

`-iris BASE_IRIS` Map only to terms whose IRIs start with any IRI given in this comma-separated list.

`-d EXCL_DEPRECATED` Exclude terms stated as deprecated via owl:deprecated.

`-i INCL_INDIVIDUALS` Include ontology individuals in addition to classes.

## Examples

The basic use of the tool requires a `source` file containing a list of terms to map to the given `target` ontology:  
`python text2term.py -s unstruct_terms.txt -t http://www.ebi.ac.uk/efo/efo.owl`

Specify an output file where the mappings should be saved using `-o`:  
`python text2term.py -s unstruct_terms.txt -t efo.owl -o /Documents/my-mappings.csv`

Set the minimum acceptable similarity score for mapping each given term to an ontology term using `-min`:  
`python text2term.py -s unstruct_terms.txt -t efo.owl -min 0.8`  
The mapped terms returned will have been determined to be 0.8 similar to their source terms in a 0-1 scale.  

Exclude deprecated ontology terms (declared as such via *owl:deprecated true*) using `-d`:  
`python text2term.py -s unstruct_terms.txt -t efo.owl -d`

Limit search to only terms whose IRIs start with any IRI given in a list specified using `-iris`:  
`python text2term.py -s unstruct_terms.txt -t efo.owl -iris http://www.ebi.ac.uk/efo/EFO,http://purl.obolibrary.org/obo/HP`  
Here, because EFO reuses terms from other ontologies such as HP and GO, the HP terms would be included but the GO terms would be excluded.
