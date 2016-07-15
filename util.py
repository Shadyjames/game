class defaultdict(dict):
	def __init__(self, default_factory):
		self.default_factory = default_factory
	def __getitem__(self, key, default=None):
		if key not in self:
			return self.default_factory(key)
		else:
			return super(defaultdict, self)[key]