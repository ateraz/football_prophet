from __future__ import division

import collections

import config


class BaseFeature(object):

    registry = collections.OrderedDict()

    UNKNOWN = -1

    name = None

    def evaluate(self, game):
        raise NotImplementedError


def feature(cls):
    BaseFeature.registry[cls.__name__] = cls()
    return cls


class HomeTeamMixin(object):

    def get_team(self, game):
        return game.home_team

class AwayTeamMixin(object):

    def get_team(self, game):
        return game.away_team


class LastSeasonPlace(BaseFeature):

    def evaluate(self, game):
        season = game.season
        seasons = season.tournament.seasons
        season_index = seasons.index(season)
        if not season_index:
            return self.UNKNOWN

        team = self.get_team(game)
        standings = seasons[season_index-1].standings
        # if team just started, put it in last place in previous season
        return standings.index(team) + 1 if team in standings else config.NUMBER_OF_TEAMS


class TeamResult(BaseFeature):

    WIN = 2
    DRAFT = 1
    LOSE = 0

    def get_scored(self, game):
        raise NotImplementedError

    def evaluate(self, game):
        if game.home_scored == game.away_scored:
            return self.DRAFT
        elif self.get_scored(game) == max(game.home_scored, game.away_scored):
            return self.WIN
        return self.LOSE


class HomeTeamResult(TeamResult):

    def get_scored(self, game):
        return game.home_scored


class AwayTeamResult(TeamResult):

    def get_scored(self, game):
        return game.away_scored


class LastGamesResult(BaseFeature):

    games_count = None
    target_result = None

    def get_team(self, game):
        raise NotImplementedError

    def evaluate(self, game):
        team = self.get_team(game)
        game_index = team.games.index(game)
        if game_index < self.games_count:
            return self.UNKNOWN

        target_games_count = 0
        last_games = team.games[game_index - self.games_count:game_index]
        for game in last_games:
            if game.home_team == team:
                game_result = HomeTeamResult().evaluate(game)
            else:
                game_result = AwayTeamResult().evaluate(game)
            if game_result == self.target_result:
                target_games_count += 1
        return target_games_count / self.games_count


class LastGamesWon(LastGamesResult):

    target_result = TeamResult.WIN


class LastGamesLost(LastGamesResult):

    target_result = TeamResult.LOSE


class LastGameResult(LastGamesResult):

    games_count = 1


class LastThreeGamesResult(LastGamesResult):

    games_count = 3


class LastFiveGamesResult(LastGamesResult):

    games_count = 5


class LastTenGamesResult(LastGamesResult):

    games_count = 10


@feature
class HomeTeamLastSeasonPlace(HomeTeamMixin, LastSeasonPlace):
    pass

@feature
class AwayTeamLastSeasonPlace(AwayTeamMixin, LastSeasonPlace):
    pass


@feature
class HomeTeamLastGameWon(HomeTeamMixin, LastGameResult, LastGamesWon):
    pass

@feature
class HomeTeamLastGameLost(HomeTeamMixin, LastGameResult, LastGamesLost):
    pass

@feature
class AwayTeamLastGameWon(AwayTeamMixin, LastGameResult, LastGamesWon):
    pass

@feature
class AwayTeamLastGameLost(AwayTeamMixin, LastGameResult, LastGamesLost):
    pass


@feature
class HomeTeamLastThreeGamesWon(HomeTeamMixin, LastThreeGamesResult, LastGamesWon):
    pass

@feature
class HomeTeamLastThreeGamesLost(HomeTeamMixin, LastThreeGamesResult, LastGamesLost):
    pass

@feature
class AwayTeamLastThreeGameWon(AwayTeamMixin, LastThreeGamesResult, LastGamesWon):
    pass

@feature
class AwayTeamLastThreeGameLost(AwayTeamMixin, LastThreeGamesResult, LastGamesLost):
    pass


@feature
class HomeTeamLastFiveGamesWon(HomeTeamMixin, LastFiveGamesResult, LastGamesWon):
    pass

@feature
class HomeTeamLastFiveGamesLost(HomeTeamMixin, LastFiveGamesResult, LastGamesLost):
    pass

@feature
class AwayTeamLastFiveGameWon(AwayTeamMixin, LastFiveGamesResult, LastGamesWon):
    pass

@feature
class AwayTeamLastFiveGameLost(AwayTeamMixin, LastFiveGamesResult, LastGamesLost):
    pass
