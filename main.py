# coding: utf-8
from player import *
from league import *
from team import *

l = League("Открытая лига")
t = Team("Высокий пинг", "0")
p = Player("1")

set_team_league(t, l)
set_player_team(p, t)