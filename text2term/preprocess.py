import re
import os
from enum import Enum

class DupSetting(Enum):
	NO_REM = 0
	REM_BEFORE = 1
	REM_AFTER = 2
	REM_BOTH = 3

def preprocess_file(file_path, template_path, output_file="", blacklist_path="", \
	                blacklist_char='', rem_duplicates=DupSetting.NO_REM):
	terms = _get_values(file_path)
	processed_terms = preprocess_terms(terms, template_path, output_file=output_file, \
					blacklist_path=blacklist_path, blacklist_char=blacklist_char, \
					rem_duplicates=rem_duplicates)

	return processed_terms

def preprocess_terms(terms, template_path, output_file="", blacklist_path="", \
	                 blacklist_char='', rem_duplicates=DupSetting.NO_REM):
	# Remove duplicate terms, if settings indicate
	if rem_duplicates == DupSetting.REM_BEFORE or rem_duplicates == DupSetting.REM_BOTH:
		terms = _remove_duplicates(terms)

	# Form the templates as regular expressions
	template_strings = _get_values(template_path)
	template_strings.append("(.*)")
	templates = _make_regex_list(template_strings)

	# Create the blacklist, if it exists
	blacklist = []
	if blacklist_path != "":
		blacklist_strings = _get_values(blacklist_path)
		blacklist = _make_regex_list(blacklist_strings)

	# Checks all terms against each blacklist then template
	processed_terms = []
	for term in terms:
		blacklisted = False
		for banned in blacklist:
			match = banned.fullmatch(term)
			if match:
				if blacklist_char != '':
					processed_terms.append(blacklist_char)
				blacklisted = True
				break
		if blacklisted:
			continue
		for template in templates:
			match = template.fullmatch(term)
			if match:
				combined_matches = ' '.join(map(str, match.groups()))
				if combined_matches:
					processed_terms.append(combined_matches)
					break

	if rem_duplicates == DupSetting.REM_AFTER or rem_duplicates == DupSetting.REM_BOTH:
		processed_terms = _remove_duplicates(processed_terms)

	if output_file != "":
		with open(output_file, 'w') as fp:
			fp.write('\n'.join(processed_terms))
	return processed_terms

def _get_values(path):
	return open(path).read().splitlines()

def _make_regex_list(strings):
	regexes = []
	for string in strings:
		regexes.append(re.compile(string))
	return regexes

def _remove_duplicates(list):
	return [*set(list)]
