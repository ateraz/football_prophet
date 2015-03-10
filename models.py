import os
import re

import config
import utils
from features import BaseFeature, NotEnoughDataException


class Tournament(object):

    registry = {}

    @classmethod
    def get_all(cls):
        tournaments = []
        return [cls(name) for name in utils.get_dirs(config.DATA_ROOT)]

    def __init__(self, name):
        self.registry[name] = self
        self.name = name
        self.seasons = self.get_seasons()

    def get_seasons(self):
        path = os.path.join(config.DATA_ROOT, self.name)
        return [Season(name, self) for name in utils.get_dirs(path)]


class Season(object):

    registry = {}

    def __init__(self, name, tournament):
        self.registry[name] = self
        self.name = name
        self.tournament = tournament
        self.standings = self.get_standings()
        self.games = self.get_games()

    def get_standings(self):
        standings_file = os.path.join(
            config.DATA_ROOT,
            self.tournament.name,
            self.name,
            config.STANDINGS_FILE
        )
        regex = r'(?<=\d\.\s)[\w\s]+?(?=\s+\d)'
        with open(standings_file, 'r') as f:
            return [Team.get_team(name) for name in re.findall(regex, f.read())[:config.NUMBER_OF_TEAMS]]

    def get_games(self):
        matches_file = os.path.join(
            config.DATA_ROOT,
            self.tournament.name,
            self.name,
            config.MATCHES_FILE
        )
        regex = r'([\-\d]+),([\w\s]+),([\w\s]+),(\d+)-(\d+),'
        with open(matches_file, 'r') as f:
            return [Game(*game, season=self) for game in re.findall(regex, f.read())]


class Team(object):

    registry = {}

    @classmethod
    def get_team(cls, name):
        team = cls.registry.get(name, None)
        if not team:
            team = cls(name)
        return team

    def __init__(self, name):
        self.name = name
        self.games = []
        self.home_games = []
        self.away_games = []

        self.registry[name] = self

    def add_game(self, game):
        self.games.append(game)
        if game.home_team == self:
            self.home_games.append(game)
        else:
            self.away_games.append(game)


class Game(object):

    all_games = []

    def __init__(self, date, home_team, away_team, home_scored, away_scored, season):
        self.date = date
        self.home_team = Team.get_team(home_team)
        self.away_team = Team.get_team(away_team)
        self.home_scored = int(home_scored)
        self.away_scored = int(away_scored)
        self.season = season

        self.all_games.append(self)
        self.home_team.add_game(self)
        self.away_team.add_game(self)

    def get_features(self):
        return tuple(feature.evaluate(self) for feature in BaseFeature.registry.values())

    def get_result(self):
        return (
            self.home_scored > self.away_scored,
            self.home_scored == self.away_scored,
            self.home_scored < self.away_scored
        )

    @classmethod
    def get_training_examples(cls):
        features = []
        results = []
        for game in cls.all_games:
            try:
                features.append(game.get_features())
            except NotEnoughDataException:
                pass
            else:
                results.append(game.get_result())
        return features, results
