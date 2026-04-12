# create by lesomras on 2025-12-22

from .scoreboard import LocalScoreboards
from .tag import LocalTags

class LocalEnv(object):
    def __init__(self) -> None:
        self.scoreboard = LocalScoreboards()
        self.sc = self.scoreboard
        self.tag = LocalTags()