import team

class Player(object):
	def __init__(self, id: str):
		self.id = id
		self.team = None

	def __str__(self):
		return self.id


def set_player_team(player: Player, team: team.Team):
	if player not in team.players:
		if player.team:
			player.team.players.discard(player)
		team.players.add(player)
		player.team = team

def unset_player_team(player: Player, team: team.Team):
	if player.team:
		player.team.players.discard(player)
		player.team = None