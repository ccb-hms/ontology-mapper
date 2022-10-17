import json
import pickle
import time
from t2t import Text2Term

t2t = Text2Term()

# Cache a single ontology
t2t.cache_ontology("https://github.com/EBISPOT/efo/releases/download/v3.46.0/efo.owl", "EFO_TEST")

# Cache all ontologies in a CSV file
# t2t.cache_ontology_set(ontology_registry_path="/Users/rsgoncalves/Documents/Workspace/text2term/text2term/resources/ontologies.csv")

# Deserialize a cached ontology to get the ontology-terms dictionary needed for mapping
start = time.time()
# terms = json.load(open("cache/EFO_TEST/EFO_TEST-term-details.json", "rb"))
terms = pickle.load(open("cache/EFO_TEST/EFO_TEST-term-details.pickle", "rb"))
end = time.time()
print("Deserialization time: " + str(end-start))
print(str(len(terms)))
for term_iri, term_obj in terms.items():
    print(term_iri)
    print(term_obj)
    break
