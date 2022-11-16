# text2term ontology mapper

A tool for mapping free-text descriptions of (biomedical) entities to controlled terms in an ontology. 

## Programmatic Usage
Install package using **pip**:

`pip install text2term`

The tool can be executed in Python with either of the two following functions:
`text2term.map_files(input_file, target_ontology, base_iris=(), csv_columns=(), excl_deprecated=False, max_mappings=3, mapper=Mapper.TFIDF,min_score=0.3, output_file='', save_graphs=False, save_mappings=False, separator=',', use_cache=False)`

or

`map_terms(source_terms, target_ontology, base_iris=(), excl_deprecated=False, max_mappings=3, min_score=0.3, mapper=Mapper.TFIDF, output_file='', save_graphs=False, save_mappings=False, source_terms_ids=(), use_cache=False)`

### Arguments
For `map_files`, the first argument 'input_file' specifies a path to a file containing the names of every term that needs to be mapped. For `map_terms`, The first argument 'source_terms' takes in a list of the terms to be mapped.

All other arguments are the same, and have the same functionality:

`target_ontology` : str
    Path or URL of 'target' ontology to map the source terms to. When the chosen mapper is BioPortal or Zooma,
    provide a comma-separated list of ontology acronyms (eg 'EFO,HPO') or write 'all' to search all ontologies

`base_iris` : tuple
    Map only to ontology terms whose IRIs start with one of the strings given in this tuple, for example:
    ('http://www.ebi.ac.uk/efo','http://purl.obolibrary.org/obo/HP')

`source_terms_ids` : tuple
    Collection of identifiers for the given source terms

`excl_deprecated` : bool
    Exclude ontology terms stated as deprecated via `owl:deprecated true`

`mapper` : mapper.Mapper
    Method used to compare source terms with ontology terms. One of: levenshtein, jaro, jarowinkler, jaccard, fuzzy, tfidf, zooma, bioportal
    These can be initialized by invoking mapper.Mapper e.g. `mapper.Mapper.TFIDF`

`max_mappings` : int
    Maximum number of top-ranked mappings returned per source term

`min_score` : float
    Minimum similarity score [0,1] for the mappings (1=exact match)

`output_file` : str
    Path to desired output file for the mappings

`save_graphs` : bool
    Save vis.js graphs representing the neighborhood of each ontology term

`save_mappings` : bool
    Save the generated mappings to a file (specified by `output_file`) 

All default values, if they exist, can be seen above.

### Return Value
Both functions return the same value:

`df` : Data frame containing the generated ontology mappings

### Caching
As of version 1.1.0, users can now cache ontologies that they want to use regularly or quickly. Programatically, there are two steps to using the cache: creating the cache, then accessing it. First, the user can cache ontologies using either of two functions:

`cache_ontology(ontology_url, ontology_acronym, base_iris=())`
Or
`cache_ontology_set(ontology_registry_path)`

The first of these will cache a single ontology from a URL or file path, with it being referenced by an acronym that will be used to reference it later. An example can be found below.
The second function allows the user to cache several ontologies at once by referencing a CSV file of the format:
`acronym,name,version,date,url,comments`

Once an ontology has been cached by either function, it is stored in a cache folder locally, and thus can be referenced even in different Python instances.

NOTE: Due to how ontologies are processed in memory, `cache_ontology_set` must be used to cache multiple ontologies in a single Python instance. If `cache_ontology` is used multiple times in one instance, the behavior is undefined and may cause visible or invisible errors.

After an ontology is cached, the user can access the cache by using the assigned acronym in the place of `target_ontology` and setting the `use_cache` flag to `True`.
To clear the cache, one can call:
`clear_cache(ontology_acronym='')`
If no arguments are specified, the entire cache will be cleared. Otherwise, only the ontology with the given acronym will be cleared.
Finally, `cache_exists(ontology_acronym)` is a simple program that returns `True` if the given acronym exists in the cache, and `False` otherwise. It is worth noting that while ontology URLs can repeat, acronyms must be distinct in a given environment.

## Command Line Usage

Install package using **pip**:

`pip install .`

Execute the tool as follows:

`python text2term -s SOURCE -t TARGET [-o OUTPUT] [-m MAPPER] [-csv CSV_INPUT] [-top TOP_MAPPINGS] [-min MIN_SCORE] [-iris BASE_IRIS] [-d EXCL_DEPRECATED] [-g SAVE_TERM_GRAPHS]`

To display a help message with descriptions of tool arguments do:

`python text2term -h` or `python text2term --help`

### Required arguments
`-s SOURCE` Input file containing 'source' terms to map to ontology terms (list of terms or CSV file).

`-t TARGET` Path or URL of 'target' ontology to map source terms to. When the chosen mapper is BioPortal or Zooma, provide a comma-separated list of acronyms (eg 'EFO,HPO') or write `'all'` to search all ontologies.

### Optional arguments

`-o OUTPUT` Path to desired output file for the mappings.

`-m MAPPER` Method used to compare source terms with ontology terms. One of: *levenshtein, jaro, jarowinkler, jaccard, indel, fuzzy, tfidf, zooma, bioportal*.

`-csv CSV_INPUT` Indicates a CSV format input—follow with the name of the column containing terms to map, optionally followed by the name of the column containing identifiers for the terms (eg 'my terms,my term ids').

`-top TOP_MAPPINGS` Maximum number of top-ranked mappings returned per source term.

`-min MIN_SCORE` Minimum similarity score [0,1] for the mappings (1=exact match).

`-iris BASE_IRIS` Map only to ontology terms whose IRIs start with a value given in this comma-separated list (eg 'http://www.ebi.ac.uk/efo,http://purl.obolibrary.org/obo/HP)').

`-d EXCL_DEPRECATED` Exclude ontology terms stated as deprecated via `owl:deprecated true`.

`-g SAVE_TERM_GRAPHS` Save [vis.js](https://visjs.org) graphs representing the neighborhood of each ontology term.

`-c STORE_IN_CACHE` Using this flag followed by the acronym the ontology should be stored as, the program will same the target ontology to the cache. After that, referencing the acronym in `target` will reference the cache. Examples are below.

## Examples
### Programmatic
```
import text2term
import pandas

df1 = text2term.map_file(unstruct_terms.txt, "http://www.ebi.ac.uk/efo/efo.owl")
df2 = text2term.map_terms(["asthma", "colon cancer"], "http://www.ebi.ac.uk/efo/efo.owl")
```
Below is an example of caching, assuming the same imports as above:
```
text2term.cache_ontology("http://www.ebi.ac.uk/efo/efo.owl", "EFO")
df1 = text2term.map_file(unstruct_terms.txt, "EFO", use_cache=True)
df2 = text2term.map_terms(["asthma", "colon cancer"], "EFO", use_cache=True)
text2term.clear_cache("EFO")
```

### Command Line
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

Use the cache on the command line, first by flagging it, then in the future using the acronym:
`python text2term -s unstruct_terms.txt -t http://www.ebi.ac.uk/efo/efo.owl -c EFO`
Then, after running this, the following command is equivalent:
`python text2term -s unstruct_terms.txt -t EFO`
