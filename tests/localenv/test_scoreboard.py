from localenv.localenv import LocalEnv
from localenv.player import Player
from serializer import JsonSerializer

le = LocalEnv()

lesomras = Player("lesomras")
le.scoreboard.add_scoreboard("scoreboard").players_add(lesomras, 120)
le.tag.tag_add(lesomras, "operator")

JsonSerializer.dump(le.scoreboard.serialize(), ".data/entity.json")
