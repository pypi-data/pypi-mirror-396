from .base_game import BaseGame

class Crash(BaseGame):
    def get_spaceman(self, number_of_games: int = 100):
        table_id = "spacemanyxe123nh"
        fields = ["gameResult"]
        return self._get_game_history(table_id, fields, number_of_games)