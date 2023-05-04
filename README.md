# *text2term* ontology mapper
A tool for mapping free-text descriptions of (biomedical) entities to controlled terms in ontologies. 

## Installation
Install package using **pip**:

```
pip install text2term
```
## Examples
### Programmatic
```python
import text2term
import pandas

df1 = text2term.map_file("test/unstruct_terms.txt", "http://www.ebi.ac.uk/efo/efo.owl")
df2 = text2term.map_terms(["asthma", "acute bronchitis"], "http://www.ebi.ac.uk/efo/efo.owl")
```
Below is an example of caching, assuming the same imports as above:
```python
text2term.cache_ontology("http://www.ebi.ac.uk/efo/efo.owl", "EFO")
df1 = text2term.map_file("test/unstruct_terms.txt", "EFO", use_cache=True)
df2 = text2term.map_terms(["asthma", "acute bronchitis"], "EFO", use_cache=True)
text2term.clear_cache("EFO")
```

### Command Line
The basic use of the tool requires a `source` file containing a list of terms to map to the given `target` ontology:  
`python text2term -s test/unstruct_terms.txt -t http://www.ebi.ac.uk/efo/efo.owl`

Specify an output file where the mappings should be saved using `-o`:  
`python text2term -s test/unstruct_terms.txt -t efo.owl -o /Documents/my-mappings.csv`

Set the minimum acceptable similarity score for mapping each given term to an ontology term using `-min`:  
`python text2term -s test/unstruct_terms.txt -t efo.owl -min 0.8`  
The mapped terms returned will have been determined to be 0.8 similar to their source terms in a 0-1 scale.  

Exclude deprecated ontology terms (declared as such via *owl:deprecated true*) using `-d`:  
`python text2term -s test/unstruct_terms.txt -t efo.owl -d`

Limit search to only terms whose IRIs start with any IRI given in a list specified using `-iris`:  
`python text2term.py -s test/unstruct_terms.txt -t efo.owl -iris http://www.ebi.ac.uk/efo/EFO,http://purl.obolibrary.org/obo/HP`  
Here, because EFO reuses terms from other ontologies such as HP and GO, the HP terms would be included but the GO terms would be excluded.

Use the cache on the command line, first by flagging it, then in the future using the acronym:
`python text2term -s test/unstruct_terms.txt -t http://www.ebi.ac.uk/efo/efo.owl -c EFO`
Then, after running this, the following command is equivalent:
`python text2term -s test/unstruct_terms.txt -t EFO`

## Programmatic Usage
The tool can be executed in Python with any of the three following functions:

```python
text2term.map_file(input_file='/some/file.txt', 
                   target_ontology='http://some.ontology/v1.owl',
                   base_iris=(),
                   csv_columns=(), 
                   excl_deprecated=False, 
                   max_mappings=3, 
                   mapper=Mapper.TFIDF,
                   min_score=0.3, 
                   output_file='', 
                   save_graphs=False, 
                   save_mappings=False, 
                   separator=',', 
                   use_cache=False,
                   term_type='classes')
```
or
```python
text2term.map_terms(source_terms=['term one', 'term two'],
                    target_ontology='http://some.ontology/v1.owl',
                    base_iris=(),
                    excl_deprecated=False,
                    max_mappings=3,
                    min_score=0.3,
                    mapper=Mapper.TFIDF,
                    output_file='',
                    save_graphs=False,
                    save_mappings=False,
                    source_terms_ids=(),
                    use_cache=False,
                    term_type='classes')
```
or
```python
text2term.map_tagged_terms(tagged_terms_dict={'term one': ["tag 1", "tag 2"]},
                    target_ontology='http://some.ontology/v1.owl',
                    base_iris=(),
                    excl_deprecated=False,
                    max_mappings=3,
                    min_score=0.3,
                    mapper=Mapper.TFIDF,
                    output_file='',
                    save_graphs=False,
                    save_mappings=False,
                    source_terms_ids=(),
                    use_cache=False,
                    term_type='classes')
```

### Arguments
For `map_file`, the first argument 'input_file' specifies a path to a file containing the terms to be mapped. It also has a `csv_column` argument that allows the user to specify a column to map if a csv is passed in as the input file. 
For `map_terms`, the first argument 'source_terms' takes in a list of the terms to be mapped.
For `map_tagged_terms`, everything is the same as `map_terms` except the first argument is either a dictionary of terms to a list of tags, or a list of TaggedTerm objects (see below). Currently, the tags do not affect the mapping in any way, but they are added to the output dataframe at the end of the process.

All other arguments are the same, and have the same functionality:

`target_ontology` : str
    Path or URL of 'target' ontology to map the source terms to. When the chosen mapper is BioPortal or Zooma,
    provide a comma-separated list of ontology acronyms (eg 'EFO,HPO') or write 'all' to search all ontologies
    As of version 2.3.0, passing a recognized acronym to `target_ontology` will generate the download link automatically. This is done using the `bioregistry` python package.

`base_iris` : tuple
    Map only to ontology terms whose IRIs start with one of the strings given in this tuple, for example:
    ('http://www.ebi.ac.uk/efo','http://purl.obolibrary.org/obo/HP')

`source_terms_ids` : tuple
    Collection of identifiers for the given source terms
    WARNING: While this is still available for the tagged term function, it is worth noting that dictionaries do not necessarily preserve order, so it is not recommended. If using the TaggedTerm object, the source terms can be attached there to guarantee order.

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

`use_cache` : bool
    Use the cache for the ontology. More details are below.

`term_type` : str
    Determines whether the ontology should be parsed for its classes (ThingClass), properties (PropertyClass), or both. Possible values are ['classes', 'properties', 'both']. If it does not match one of these values, the program will throw a ValueError.

All default values, if they exist, can be seen above.

### Return Value
Both functions return the same value:

`df` : Data frame containing the generated ontology mappings

### Ontology Caching
As of version 1.1.0, users can cache ontologies that they want to use regularly or quickly. Programmatically, there are two steps to using the cache: creating the cache, then accessing it. First, the user can cache ontologies using either of two functions:

```python
cache_ontology(ontology_url, ontology_acronym="", base_iris=())
```

```python
cache_ontology_set(ontology_registry_path)
```

The first of these will cache a single ontology from a URL or file path, with it being referenced by an acronym that will be used to reference it later. If no acronym is given, it will use the URL as the cache name. An example can be found above.
The second function allows the user to cache several ontologies at once by referencing a CSV file of the format:
`acronym,version,url`. An example is provided in `resources/ontologies.csv`

Once an ontology has been cached by either function, it is stored in a cache folder locally, and thus can be referenced even in different Python instances.
As of version 2.3.0, the `cache_ontology` function also returns an object that can be used to call any of the `map` functions, as well as `clear_cache` and `cache_exists`. These have the same arguments, except `ontology_target` is not specified and there is no `use_cache` option, as it is always True.

NOTE: Due to how ontologies are processed in memory, `cache_ontology_set` must be used to cache multiple ontologies in a single Python instance. If `cache_ontology` is used multiple times in one instance, the behavior is undefined and may cause visible or invisible errors.

After an ontology is cached, the user can access the cache by using the assigned acronym in the place of `target_ontology` and setting the `use_cache` flag to `True`.
To clear the cache, one can call:
`clear_cache(ontology_acronym='')`
If no arguments are specified, the entire cache will be cleared. Otherwise, only the ontology with the given acronym will be cleared.
Finally, `cache_exists(ontology_acronym='')` is a simple function that returns `True` if the given acronym exists in the cache, and `False` otherwise. It is worth noting that while ontology URLs can repeat, acronyms must be distinct in a given environment.

### Input Preprocessing
As of version 1.2.0, text2term includes regex-based preprocessing functionality for input terms. Specifically, these functions take the input terms and a collection of (user-defined) regular expressions, then match each term to each regular expression to simplify the input term.

Like the "map" functions above, the two functions differ on whether the input is a file or a list of strings:
```python
preprocess_file(file_path, template_path, output_file='', blocklist_path='', blocklist_char='', rem_duplicates=False)
```
```python
preprocess_terms(terms, template_path, output_file='', blocklist_path='', blocklist_char='', rem_duplicates=False)
``` 
```python
preprocess_tagged_terms(file_path, template_path='', blocklist_path='', blocklist_char='', rem_duplicates=False, separator=';:;')
```

In all cases, the regex templates and blocklist must be stored in a newline-separated file. If an output file is specified, the preprocessed strings are written to that file and the list of preprocessed strings is returned.

The blocklist functionality allows the user to specify another regex file. If any terms match any regex in blocklist, they are removed from the terms, or, if a blocklist character is specified, replaced with that character for placeholding. 
NOTE: As of version 2.1.0, the arguments were changed to "blocklist" from "blacklist". Backwards compatibility is currently supported, but will likely be discontinued at the next major release.

The Remove Duplicates `rem_duplicates` functionality will remove all duplicate terms after processing, if set to `True`. 
WARNING: Removing duplicates at any point does not guarantee which original term is kept. This is particularly important if original terms have different tags, so user caution is advised.

The functions `preprocess_file()` and `preprocess_terms()` both return a dictionary where the keys are the original terms and the values are the preprocessed terms.
The `preprocess_tagged_terms()` function returns a list of TaggedTerm items with the following function contracts:
```python
def __init__(self, term=None, tags=[], original_term=None, source_term_id=None)
def add_tags(self, new_tags)
def update_term(self, term)
def update_source_term_id(self, source_term_id)
def get_original_term(self)
def get_term(self)
def get_tags(self)
def get_source_term_id(self)
```
As mentioned in the mapping section above, this can then be passed directly to map_tagged_terms(), allowing for easy programmatic usage. Note that this allows multiple of the same preprocessed term with different tags. 

**Note on NA values in input**: As of v2.0.3, when the input to text2term is a table file, any rows that contain `NA` values in the specified term column, or in the term ID column (if provided), will be ignored.

## Command Line Usage

After installation, execute the tool from a command line as follows:

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

`-c STORE_IN_CACHE` Using this flag followed by the acronym the ontology should be stored as, the program will same the target ontology to the cache. After that, referencing the acronym in `target` will reference the cache. Examples are above.
