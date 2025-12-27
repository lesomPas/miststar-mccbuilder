# create by lesomras on 2025-12-22

from miststar.internal.exceptions import UnsupportedException, MissingException, MalformedException
from miststar.internal.simple_uuid import new_uuid, UUIDSpace


class Player(object):
    __slots__ = ("player_name", "uuid")

    def __init__(self, player_name: str) -> None:
        if not isinstance(player_name, str):
            raise UnsupportedException(f"'player_name' must be a str, but received {type(player_name)}.")

        self.player_name = player_name
        self.uuid = new_uuid()


class LocalPlayers(object):
    def __init__(self) -> None:
        self.uuid_mapping: dict[str, str] = {}
        self.player_mapping: dict[str, Player] = {}

    def add_player(self, player: Player) -> None:
        if not isinstance(player, Player):
            raise UnsupportedException(f"'player' must be a Player, but received {type(player)}")
        if self.has_player_name(player.player_name):
            raise MalformedException(f"player name {player.player_name} already exists in this local players.")

        self.uuid_mapping[player.player_name] = player.uuid
        self.player_mapping[player.uuid] = player

    def has_player_name(self, player_name: str) -> bool:
        return player_name in self.uuid_mapping
