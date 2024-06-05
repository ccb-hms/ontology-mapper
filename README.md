# *text2term* ontology mapper
A tool for mapping free-text descriptions of (biomedical) entities to controlled terms in ontologies. 

## Installation
Install package using **pip**:

```
pip install text2term
```
## Basic Examples

<details>
  <summary><b>Examples of Programmatic Mapping</b></summary>

### Examples of Programmatic Mapping
text2term supports mapping strings specified in multiple input formats. In the first example, we map strings in a list to an ontology specified by its URL:

```python
import text2term 
dfl = text2term.map_terms(source_terms=["asthma", "acute bronchitis"], 
                          target_ontology="http://purl.obolibrary.org/obo/mondo.owl")
```

There is also support for file-based input, for example a file containing a list of strings:
```python
dff = text2term.map_terms(source_terms="test/unstruct_terms.txt", 
                          target_ontology="http://purl.obolibrary.org/obo/mondo.owl")
```

or a table where we can specify the column of terms to map and the table value separator:
```python
dff = text2term.map_terms(source_terms="test/some_table.tsv", 
                          csv_columns=('diseases','optional_ids'), separator="\t",
                          target_ontology="http://purl.obolibrary.org/obo/mondo.owl")
```

Finally it is possible map strings in a dictionary with associated tags that are preserved in the output:
```python
dfd = text2term.map_terms(source_terms={"asthma":"disease", "acute bronchitis":["disease", "lung"]}, 
                          target_ontology="http://purl.obolibrary.org/obo/mondo.owl")
```

</details>

<details>
  <summary><b>Examples of Programmatic Caching</b></summary>

### Examples of Programmatic Caching
text2term supports caching an ontology for repeated use. Here we cache an ontology and give it a name:
```python
mondo = text2term.cache_ontology(ontology_url="http://purl.obolibrary.org/obo/mondo.owl", 
                                 ontology_acronym="MONDO")
```

The given name acts as a reference. Now we can map strings to the cached ontology by specifying as `target_ontology` the name specified above and the flag `use_cache=True`

```python
dfc = text2term.map_terms(source_terms=["asthma", "acute bronchitis"], 
                          target_ontology="MONDO", use_cache=True)
```

More succinctly, we can use the returned `OntologyCache` object `mondo` as such:
```python
dfo = mondo.map_terms(source_terms=["asthma", "acute bronchitis"])
```
</details>


<details>
  <summary><b>Examples of Command Line Interface Use</b></summary>

### Examples of Command Line Interface Use
To show a help message describing all arguments type into a terminal:
```shell
python text2term --help
```

The basic use of text2term requires a `source` file containing the terms to map to a given `target` ontology:  
```shell
python text2term -s test/unstruct_terms.txt -t http://purl.obolibrary.org/obo/mondo.owl
```

---
Map to a local ontology and specify an output file where the mappings should be saved using `-o`:  
```shell
python text2term -s test/unstruct_terms.txt -t test/mondo.owl -o test/mymappings.csv
```

---
Set the minimum acceptable similarity score for mapping each given term to an ontology term using `-min`:  
```shell
python text2term -s test/unstruct_terms.txt -t test/mondo.owl -min 0.8
```
The mapped terms returned will have been determined to be 0.8 similar to their source terms in a 0-1 scale.  

---
Exclude deprecated ontology terms (declared as such via *owl:deprecated true*) using `-d`:  
```shell
python text2term -s test/unstruct_terms.txt -t test/mondo.owl -d
```

---
Limit search to only terms whose IRIs start with any IRI given in a list specified using `-iris`:  
```shell
python text2term.py -s test/unstruct_terms.txt -t test/mondo.owl -iris http://purl.obolibrary.org/obo/mondo,http://identifiers.org/hgnc
```
While MONDO uses terms from other ontologies such as CHEBI and Uberon, the tool only considers terms whose IRIs start either with "http://purl.obolibrary.org/obo/mondo" or "http://identifiers.org/hgnc".

---
Cache an ontology for repeated use by running the tool while instructing it to cache the ontology via `-c <name>`:
```shell
python text2term -s test/unstruct_terms.txt -t http://purl.obolibrary.org/obo/mondo.owl -c MONDO
```

Now the ontology is cached and we can refer to it as the target ontology using the name given beforehand: 
```shell
python text2term -s test/unstruct_terms.txt -t MONDO
```

</details>


## Programmatic Usage
After installing and importing to a Python environment, the main function is `map_terms`:

```python
text2term.map_terms(source_terms, 
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
                   term_type=OntologyTermType.CLASS,
                   incl_unmapped=False)
```
The function returns a pandas `DataFrame` containing the generated ontology mappings.

<details>
  <summary><b>Argument Details</b></summary>

### Argument Details

`source_terms`&mdash;Strings to be mapped to an ontology, which can be specified as a:
1. list of strings
2. string containing a file path
3. dictionary of terms and associated tags, where each key is a term and the value is a list of tags
4. list of `TaggedTerm` objects
   - Tags do not affect the mapping, they are simply added to the output dataframe 
   - If a term is tagged with "Ignore", text2term will not map it
   - Unmapped terms can still be included in the output if `incl_unmapped` is True

`target_ontology`&mdash;Path, URL or name of 'target' ontology to map the source terms to. Ontology names can be given as values to `target_ontology` e.g. "EFO" or "CL"&mdash;text2term uses [bioregistry](https://bioregistry.io) to get URLs for such names. Similarly, when the target ontology has been cached, enter the name used upon caching.

When using the BioPortal or Zooma interfaces, the value for `target_ontology` should be a comma-separated list of ontology acronyms (eg 'EFO,HPO') or **'all'** to search all ontologies.

`base_iris`&mdash;Map only to ontology terms whose IRIs start with one of the strings given in this tuple

`excl_deprecated`&mdash;Exclude ontology terms stated as deprecated via `owl:deprecated true`

`source_terms_ids`&mdash;Collection of identifiers for the given source terms

`csv_column`&mdash;Specify the name of the column containing the terms to map, when the input file is a table. Optionally provide a second column name, containing the respective term identifiers

`separator`&mdash;Character that separates columns when input is a table (eg '\t' for TSV) 

`mapper`&mdash;Method used to compare source terms with ontology terms. One of `levenshtein, jaro, jarowinkler, jaccard, fuzzy, tfidf, zooma, bioportal` (see [Supported Mappers](#supported-mappers))

`max_mappings`&mdash;Maximum number of top-ranked mappings returned per source term

`min_score`&mdash;Minimum similarity score [0,1] for the mappings (1=exact match)

`save_mappings`&mdash;Save the generated mappings to a file (specified by `output_file`) 

`output_file`&mdash;Path to desired output file for the mappings dataframe

`save_graphs`&mdash;Save vis.js graphs representing the neighborhood of each ontology term

`use_cache`&mdash;Use the cache for the ontology

`term_type`&mdash;Specifies whether to map to ontology classes, properties or both. One of `class, property, any`

`incl_unmapped`&mdash;Include unmapped terms in the output. If a term has been tagged 'Ignore' or has less than the `min_score`, it is included in the output data frame

</details>

<details>
  <summary><b>Ontology Caching</b></summary>

### Ontology Caching
text2term supports caching ontologies for faster or repeated mapping to the same ontology. An ontology can be cached using the function:

```python
cache_ontology(ontology_url, ontology_acronym="", base_iris=())
```
This caches a single ontology from a URL or file path, and takes an optional acronym that will be used to reference the cached ontology later. If no acronym is given, the URL is used as the name.

It is also possible to cache multiple ontologies, whose names and URLs are specified in a table formatted as such `acronym,version,url`. An example is provided in [resources/ontologies.csv](https://github.com/ccb-hms/ontology-mapper/blob/main/text2term/resources/ontologies.csv):
```python
cache_ontology_set(ontology_registry_path)
```

Once an ontology has been cached by either function, it is stored in a cache folder locally, and thus can be referenced even in different Python instances. Users can leverage the cache by using the assigned acronym as the value for the `target_ontology` argument, and setting the `use_cache` argument to `True`.

To clear the ontology cache, the following function can be used:

```python
text2term.clear_cache(ontology_acronym='')
```

If no arguments are specified, the entire cache will be cleared. Otherwise, only the ontology with the given acronym will be cleared.
Finally, `cache_exists(ontology_acronym='')` is a simple function that returns `True` if the given acronym exists in the cache, and `False` otherwise.

**_Notes:_**
- The `cache_ontology` function returns an object that can be used to directly call the `map_terms` function, as well as `clear_cache` and `cache_exists`. These have the same arguments, except `ontology_target` is no longer specified and there is no `use_cache` option, since it is always True.
- While ontology URLs can be repeatedly used, acronyms must be distinct in a given environment.

</details>

<details>
  <summary><b>Input Preprocessing</b></summary>

### Input Preprocessing
text2term includes regular expression-based preprocessing functionality for input terms. There are functions that take the input terms and a collection of (user-defined) regular expressions, then match each term to each regular expression to simplify the input term.

```python
preprocess_terms(terms, template_path, output_file='', blocklist_path='', 
                 blocklist_char='', rem_duplicates=False)
``` 
This returns a dictionary where the keys are the original terms and the values are the preprocessed terms.

```python
preprocess_tagged_terms(file_path, template_path='', blocklist_path='', 
                        blocklist_char='', rem_duplicates=False, separator=';:;')
```

This returns a list of `TaggedTerm` objects.

The regex templates file `template_path` and the blocklist `blocklist_path` must each be a newline-separated file. If an output file is specified, the preprocessed strings are written to that file.

The blocklist functionality allows specifying another file with regular expressions that, when terms match any such regex in the blocklist, they are removed from the list of terms to map. Alternatively, if a blocklist character is specified, the input is replaced with that character. 

The `rem_duplicates` option removes all duplicate terms after processing, if set to `True`.

When the input to text2term is a table, any rows that contain `NA` values in the specified term column, or in the term ID column (if provided), will be ignored.

If an ignore tag `"ignore"` or `"Ignore"` is added to a term, that term will not be mapped to any terms in the ontology. It will only be included in the output if the `incl_unmapped` argument is True. The following values are regarded as ignore tags: `"ignore", "Ignore".

</details>

## Command Line Interface Usage

After installing, execute the tool from a command line as follows:

`python text2term [-h] -s SOURCE -t TARGET [-o OUTPUT] [-m MAPPER] [-csv CSV_INPUT] [-sep SEPARATOR] [-top TOP_MAPPINGS] [-min MIN_SCORE] [-iris BASE_IRIS] [-d] [-g] [-c STORE_IN_CACHE] [-type TERM_TYPE] [-u]`

To display a help message with descriptions of tool arguments do:

`python text2term -h` or `python text2term --help`

### Required Arguments
`-s SOURCE` Input file containing 'source' terms to map to ontology terms (list of terms or CSV file).

`-t TARGET` Path or URL of 'target' ontology to map source terms to. When the chosen mapper is BioPortal or Zooma, provide a comma-separated list of acronyms (eg 'EFO,HPO') or write `'all'` to search all ontologies.

<details>
  <summary><b>Optional Arguments</b></summary>

### Optional Arguments

`-o OUTPUT` Path to desired output file for the mappings.

`-m MAPPER` Method used to compare source terms with ontology terms. One of: *levenshtein, jaro, jarowinkler, jaccard, indel, fuzzy, tfidf, zooma, bioportal*.

`-csv CSV_INPUT` Indicates a CSV format input—follow with the name of the column containing terms to map, optionally followed by the name of the column containing identifiers for the terms (eg 'my terms,my term ids').

`-sep SEPARATOR` Specifies the cell separator to be used when reading a table

`-top TOP_MAPPINGS` Maximum number of top-ranked mappings returned per source term.

`-min MIN_SCORE` Minimum similarity score [0,1] for the mappings (1=exact match).

`-iris BASE_IRIS` Map only to ontology terms whose IRIs start with a value given in this comma-separated list (eg 'http://www.ebi.ac.uk/efo,http://purl.obolibrary.org/obo/HP)').

`-d` Exclude ontology terms stated as deprecated via `owl:deprecated true`.

`-g` Save [vis.js](https://visjs.org) graphs representing the neighborhood of each ontology term.

`-c STORE_IN_CACHE` Cache the target ontology using the name given here.

`-type TERM_TYPE` Specify whether to map to ontology classes, properties, or both

`-u` Include all unmapped terms in the output

</details>


## Supported Mappers 

The mapping score of each mapping indicates how similar an input term is to an ontology term (via its labels or synonyms). The mapping scores generated by text2term are the result of applying one of the following _mappers_:

**TF-IDF-based mapper**&mdash;[TF-IDF](https://en.wikipedia.org/wiki/Tf–idf) is a statistical measure often used in information retrieval that measures how important a word is to a document in a corpus of documents. We first generate TF-IDF-based vectors of the source terms and of labels and synonyms of ontology terms. Then we compute the [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) between vectors to determine how similar a source term is to a target term (label or synonym).

**Syntactic distance-based mappers**&mdash;text2term provides support for commonly used and popular syntactic (edit) distance metrics: Levenshtein, Jaro, Jaro-Winkler, Jaccard, and Indel. We use the [nltk](https://pypi.org/project/nltk/) package to compute Jaccard distances and [rapidfuzz](https://pypi.org/project/rapidfuzz/) to compute all others.  

**BioPortal Web API-based mapper**&mdash;uses an interface to the [BioPortal Annotator](https://bioportal.bioontology.org/annotator) that we built to allow mapping terms in bulk to ontologies in the [BioPortal](https://bioportal.bioontology.org) repository.

> [!WARNING]
> There are no scores associated with BioPortal annotations, so the score of all mappings is always 1

**Zooma Web API-based mapper**&mdash;uses a [Zooma](https://www.ebi.ac.uk/spot/zooma/) interface that we built to allow mapping terms in bulk to ontologies in the [Ontology Lookup Service (OLS)](https://www.ebi.ac.uk/ols4) repository. 

> [!IMPORTANT]
> When using the BioPortal or Zooma interfaces, make sure to specify the target ontology name(s) as they appear in BioPortal or OLS, respectively

> [!NOTE]
> Syntactic distance-based mappers and Web API-based mappers perform slowly (much slower than the TF-IDF mapper). The former because they do pairwise comparisons between each input string and each ontology term label/synonym. In the Web API-based approaches there are networking and API load overheads