import league

class Team(object):
	def __init__(self, title: str, id: str):
		self.players = set()
		self.title = title
		self.id = id
		self.league = None

	def __str__(self):
		s = "{} {} - ".format(self.id, self.title)
		s_players = []
		for player in self.players:
			s_players.append(str(player))
		s += ", ".join(s_players)
		return s


def set_team_league(team: Team, league: league.League):
	if team not in league.teams:
		if team.league:
			team.league.teams.discard(team)
		league.teams.add(team)
		team.league = league

def unset_team_league(team: Team, league: league.League):
	if team.league:
		team.league.teams.discard(team)
		team.league = None