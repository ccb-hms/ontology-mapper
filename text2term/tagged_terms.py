
class TaggedTerm:
	def __init__(self, term=None, tags=[], original_term=None, source_term_id=None):
		self.term = term
		self.tags = tags
		self.original_term = original_term
		self.source_term_id = source_term_id

	def __repr__(self):
		return f"<TaggedTerm term:{self.term} tags:{self.tags} original_term:{self.original_term}"

	def add_tags(self, new_tags):
		self.tags = self.tags + new_tags

	def update_term(self, term):
		self.term = term

	def update_source_term_id(self, source_term_id):
		self.source_term_id = source_term_id

	def get_original_term(self):
		return self.original_term

	def get_term(self):
		return self.term

	def get_tags(self):
		return self.tags

	def get_source_term_id(self):
		return self.source_term_id
		