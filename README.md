# ontology-mapper

A tool to map unstructured terms to ontology terms. Usage:

 `t2t.py -s SOURCE -t TARGET [-o OUTPUT] [-top TOP_MAPPINGS] [-min MIN_SCORE] [-i INCL_INDIVIDUALS]`

`-s SOURCE` Input file containing list of 'source' terms to map to ontology terms (one per line).

`-t TARGET` Path or URL of 'target' ontology to map the source terms to.

`-o OUTPUT` Path to desired output file for the mappings.

`-top TOP_MAPPINGS` Maximum number of top-ranked mappings returned per source term.

`-min MIN_SCORE` Minimum score [0,1] for the mappings (0=dissimilar, 1=exact match).

`-i INCL_INDIVIDUALS` Include ontology individuals in addition to classes.

For example:

`python3 t2t.py -s /Documents/unstruct_terms.txt -t https://github.com/EBISPOT/efo/releases/download/current/efo.owl`

