#!/usr/bin/python3

import sys
import itertools
import gspread
import getpass

class ParabellumException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class Relation:
  def __init__(self, matrix):
    self.matrix = matrix

  def score(self, p1, p2):
    return self.matrix[p1.likes(p2)][p2.likes(p1)]

class Player:
  def __init__(self, id, names, likes):
    self.id = id
    self.likes_others = {}

    index = -1
    for key in names:
      index += 1
      if (key == id):
        if likes[index] != 'X':
          raise ParabellumException("Player must have 'X' in his column")
        else:
          continue
      self.likes_others[key] = likes[index]

  def __str__(self):
    return "\n".join(["".join(["Player '", self.id, "' likes:"])] + [ "  %s: %s" % (player, self.likes_others[player]) for player in self.likes_others ])

  def likes(self, other):
    if self.likes_others[other.id] == "N":
      return 0
    elif self.likes_others[other.id] == "0":
      return 1
    elif self.likes_others[other.id] == "A":
      return 2
    else:
      raise ParabellumException("Bad likes() call on a player")

class Team:
  Size = 3

  def __init__(self, players):
    if len(players) != Team.Size:
      raise ParabellumException("Team should have size %s, not %s" % (Team.Size, len(players)))
    self.players = players

  def __str__(self):
    return " + ".join([ member.id for member in self.players])

  def score(self, relation):
    total_score = 0

    for pair in itertools.combinations(self.players, 2):
      score = relation.score(pair[0], pair[1])
      if score == 0:
        return 0
      else:
        total_score += score

    return total_score

def main(input_matrix):
  names, input_matrix = input_matrix[0], input_matrix[1:]
  if names[0] != "PLAYERS":
    raise ParabellumException("First line of input should start with 'PLAYERS'")

  players = []

  names = [ p.strip() for p in names[1:]]
  for name in names:
    player_record, input_matrix = input_matrix[0], input_matrix[1:]
    if name != player_record[0]:
      raise ParabellumException("Found record for player '%s', expected '%s" % (player_record[0], name))

    player = Player(name, names, [ l.strip() for l in player_record[1:]] )
    players.append(player)

    teams = {}
    for team_members in itertools.combinations(players, 3):
      team = Team(team_members)
      score = team.score(Relation(((0,0,0),(0,1,2),(0,2,4))))
      if score > 0:
        if score not in teams:
          teams[score] = [team]
        else:
          teams[score].append(team)

  count = 0
  for score in sorted(teams.keys(), reverse=True):
    print("Teams with score: %s/12" % score)
    for team in teams[score]:
      print("  %s" % team)
      count += 1
    if (count >= 9):
      break

if __name__ == "__main__":
  login = sys.argv[1]
  key = sys.argv[2]
  passwd = getpass.getpass()
  gc = gspread.login(login, passwd)
  sheet = gc.open_by_key(key).sheet1
  main(sheet.get_all_values())