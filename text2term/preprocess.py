import re
import os
from enum import Enum
from .tagged_terms import TaggedTerm

def preprocess_file(file_path, template_path, output_file="", blocklist_path="", \
	                blocklist_char='', blacklist_path="", blacklist_char='', \
	                rem_duplicates=False):
	# Allows backwards compatibility to blacklist. Will eventually be deleted
	if blocklist_char == '':
		blocklist_char = blacklist_char
	if blocklist_path == "":
		blocklist_path = blacklist_path
	terms = _get_values(file_path)
	processed_terms = preprocess_terms(terms, template_path, output_file=output_file, \
					blocklist_path=blocklist_path, blocklist_char=blocklist_char, \
					rem_duplicates=rem_duplicates)

	return processed_terms

## Tags should be stored with their terms in the same line, delineated by ";:;" 
##		ex: Age when diagnosed with (.*) ;:; age,diagnosis
##		"Age when diagnosed with cancer" becomes: {"cancer", ["age", "diagnosis"]}
def preprocess_tagged_terms(file_path, template_path="", blocklist_path="", \
	                 		blocklist_char='', blacklist_path="", blacklist_char='', \
	                 		rem_duplicates=False, separator=";:;"):
	# Allows backwards compatibility to blacklist. Will eventually be deleted
	if blocklist_char == '':
		blocklist_char = blacklist_char
	if blocklist_path == "":
		blocklist_path = blacklist_path
	# Seperate tags from the terms, put in TaggedTerm and add to list
	raw_terms = _get_values(file_path)
	terms = []
	for raw_term in raw_terms:
		seperated = raw_term.split(separator)
		try:
			tags = seperated[1].split(",")
			term = TaggedTerm(original_term=seperated[0], tags=tags)
		except IndexError:
			term = TaggedTerm(original_term=raw_term)
		terms.append(term)

	# Seperate tags from templates, store together in dictionary
	templates = {}
	if template_path != "":
		raw_templates = _get_values(template_path)
		for raw_template in raw_templates:
			seperated = raw_template.split(separator)
			try:
				tags = seperated[1].split(",")
				regex_term = re.compile(seperated[0])
				templates[regex_term] = tags
			except IndexError:
				regex_term = re.compile(raw_template)
				templates[regex_term] = []
	templates[re.compile("(.*)")] = []

	# Create the blocklist, if it exists
	blocklist = []
	if blocklist_path != "":
		blocklist_strings = _get_values(blocklist_path)
		blocklist = _make_regex_list(blocklist_strings)

	processed_terms = []
	for term in terms:
		if _blocklist_term(processed_terms, term, blocklist, blocklist_char, tagged=True):
			continue
		for template, tem_tags in templates.items():
			match = template.fullmatch(term.get_original_term())
			if match:
				combined_matches = ' '.join(map(str, match.groups()))
				if combined_matches:
					_update_tagged_term(processed_terms, term, combined_matches, tem_tags)
					break

	if rem_duplicates:
		processed_terms = _remove_duplicates(processed_terms)

	return processed_terms

def preprocess_terms(terms, template_path, output_file="", blocklist_path="", \
	                 blocklist_char='', blacklist_path="", blacklist_char='', \
	                 rem_duplicates=False):
	# Allows backwards compatibility to blacklist. Will eventually be deleted
	if blocklist_char == '':
		blocklist_char = blacklist_char
	if blocklist_path == "":
		blocklist_path = blacklist_path
	# Form the templates as regular expressions
	template_strings = []
	if template_path != "":
		template_strings = _get_values(template_path)
	template_strings.append("(.*)")
	templates = _make_regex_list(template_strings)

	# Create the blocklist, if it exists
	blocklist = []
	if blocklist_path != "":
		blocklist_strings = _get_values(blocklist_path)
		blocklist = _make_regex_list(blocklist_strings)

	# Checks all terms against each blocklist then template
	processed_terms = {}
	for term in terms:
		if _blocklist_term(processed_terms, term, blocklist, blocklist_char):
			continue
		for template in templates:
			match = template.fullmatch(term)
			if match:
				combined_matches = ' '.join(map(str, match.groups()))
				if combined_matches:
					processed_terms[term] = combined_matches
					break

	if rem_duplicates:
		processed_terms = _remove_duplicates(processed_terms)

	if output_file != "":
		with open(output_file, 'w') as fp:
			fp.write('\n'.join(processed_terms.values()))
	return processed_terms

## Note: Because Python Dictionaries and Lists are passed by reference (sort of), updating the
##			dictionary/list here will update the dictionary in the caller
def _blocklist_term(processed_terms, term, blocklist, blocklist_char, tagged=False):
	for banned in blocklist:
		match = banned.fullmatch(term if type(term) is not TaggedTerm else term.get_original_term())
		if match:
			if blocklist_char != '':
				if tagged:
					_update_tagged_term(processed_terms, term, blocklist_char)
				else:
					processed_terms[term] = blocklist_char
			return True
	return False

def _update_tagged_term(processed_terms, term, new_term, tags=[]):
	term.update_term(new_term)
	term.add_tags(tags)
	processed_terms.append(term)

def _get_values(path):
	return open(path).read().splitlines()

def _make_regex_list(strings):
	regexes = []
	for string in strings:
		regexes.append(re.compile(string))
	return regexes

def _remove_duplicates(terms):
	if type(terms) is dict:
		temp = {val : key for key, val in terms.items()}
		final = {val : key for key, val in temp.items()}
	else:
		temp = []
		final = []
		for term in terms:
			if term.get_term() not in temp:
				temp.append(term.get_term())
				final.append(term)
	return final
