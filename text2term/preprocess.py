import re
import os

def preprocess_file(file_path, template_path):
	terms = _get_values(file_path)
	processed_terms = preprocess_terms(terms, template_path)

	filename, file_extension = os.path.splitext(file_path)
	output_file = filename + "-preprocessed.txt"
	with open(output_file, 'w') as fp:
		fp.write('\n'.join(processed_terms))

def preprocess_terms(terms, template_path):
	template_strings = _get_values(template_path)
	template_strings.append("(.*)")

	# Form the templates as regular expressions
	templates = []
	for template_string in template_strings:
		templates.append(re.compile(template_string))

	# Checks all terms against each template
	processed_terms = []
	for term in terms:
		for template in templates:
			match = template.fullmatch(term)
			if match:
				combined_matches = ' '.join(map(str, match.groups()))
				if combined_matches:
					processed_terms.append(combined_matches)
					break
	return processed_terms

def _get_values(path):
	return open(path).read().splitlines()