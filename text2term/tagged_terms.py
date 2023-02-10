
class TaggedTerm:
	def __init__(self, term=None, tags=[], original_term=None):
		self.term = term
		self.tags = tags
		self.original_term = original_term

	def __repr__(self):
		return f"<TaggedTerm term:{self.term} tags:{self.tags} original_term:{self.original_term}"

	def add_tags(self, new_tags):
		self.tags = self.tags + new_tags

	def update_term(self, term):
		self.term = term

	def get_original_term(self):
		return self.original_term

	def get_term(self):
		return self.term

	def get_tags(self):
		return self.tags
		