from contextlib import contextmanager
import sys, os
import text2term

def main():
	try:
		with suppress_stdout():
			# Simple set up and testing
			text2term.map_terms(["fever", "headache"], "https://github.com/EBISPOT/efo/releases/download/current/efo.owl")
			text2term.cache_ontology("https://github.com/EBISPOT/efo/releases/download/current/efo.owl", "EFO")
			text2term.map_terms(["fever", "headache"], "EFO", use_cache=True)
			text2term.map_terms(["fever", "headache"], "EFO", base_iris=("www."), mapper=text2term.mapper.Mapper.levenshtein, max_mappings=4, use_cache=True)
			
			# Properties and classes tests
			text2term.map_terms(["fever", "headache"], "EFO", term_type="classes", use_cache=True)
			text2term.map_terms(["contains", "location"], "EFO", term_type="properties", use_cache=True)
			text2term.map_terms(["fever", "contains"], "EFO", term_type="both", use_cache=True)

			# Clear cache and set down
			text2term.clear_cache("EFO")
	except:
		print("ERROR")

# From https://stackoverflow.com/questions/2125702/how-to-suppress-console-output-in-python
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

if __name__ == '__main__':
	main()