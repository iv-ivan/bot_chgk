class Team(object):
	def __init__(self, title: str, id: str):
		self.players = set()
		self.title = title
		self.id = id
		self.league = None
		pass


def set_team_league(team: Team, league: League):
	if team not in league.teams:
		if team.league:
			team.league.teams.remove(team)
		league.teams.add(team)
		team.league = league

def unset_team_league(team: Team, league: League):
	if team.league:
		team.league.teams.remove(league)
		team.league = None