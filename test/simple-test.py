import text2term

def main():
	efo = "http://www.ebi.ac.uk/efo/efo.owl#"
	pizza = "https://protege.stanford.edu/ontologies/pizza/pizza.owl"
	ncit = "http://purl.obolibrary.org/obo/ncit/releases/2022-08-19/ncit.owl"
	if not text2term.cache_exists("EFO"):
		text2term.cache_ontology(efo, "EFO")
	df = text2term.map_terms(["asthma", "disease location", "obsolete food allergy"], "EFO", excl_deprecated=True, use_cache=True, term_type="classes")
	# df = text2term.map_terms(["contains", "asthma"], efo, term_type="classes")
	print(df.to_string())

if __name__ == '__main__':
	main()