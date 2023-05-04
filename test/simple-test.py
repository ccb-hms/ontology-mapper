import text2term
import bioregistry

def main():
	efo = "http://www.ebi.ac.uk/efo/efo.owl#"
	pizza = "https://protege.stanford.edu/ontologies/pizza/pizza.owl"
	ncit = "http://purl.obolibrary.org/obo/ncit/releases/2022-08-19/ncit.owl"
	# print(bioregistry.get_owl_download("eFo"))
	# if not text2term.cache_exists("EFO"):
	# 	cached_onto = text2term.cache_ontology("EFO")
	# 	# df = cached_onto.map_terms(["asthma", "disease location", "obsolete food allergy"], excl_deprecated=True, term_type="classes")
	# 	print("Cache exists:", cached_onto.cache_exists())
	# df = text2term.map_terms(["asthma", "disease location", "obsolete food allergy"], "EFO", excl_deprecated=True, use_cache=True, term_type="classes")
	df = text2term.map_terms(["contains", "asthma"], "EFO", term_type="classes")
	print(df.to_string())

if __name__ == '__main__':
	main()