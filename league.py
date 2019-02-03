class League(object):
	def __init__(self, title: str):
		self.teams = set()
		self.title = title

	def __str__(self):
		s = "{}:\n".format(self.title)
		for team in self.teams:
			s += "{}\n".format(team)
		return s