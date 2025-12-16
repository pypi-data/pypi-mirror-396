from .base_game import BaseGame

class JogosBrasileiros(BaseGame):
    def get_brasileira_roleta(self, number_of_games: int = 100):
        table_id = "rwbrzportrwa16rg"
        fields = ["gameResult", "megaSlots", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_brasileira_mega_roleta(self, number_of_games: int = 100):
        table_id = "mrbras531mrbr532"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_football_blitz_top_card(self, number_of_games: int = 100):
        table_id = "ge49e4os88bp4bi6"
        fields = ["gameResult", "desc", "result", "cardDiff"]
        return self._get_game_history(table_id, fields, number_of_games)
    
    def get_speed_baccarat_brasileiro_1(self, number_of_games: int = 100):
        table_id = "bcpirpmfpeobc193"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_speed_baccarat_brasileiro_2(self, number_of_games: int = 100):
        table_id = "m88hicogrzeod202"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_speed_baccarat_brasileiro_3(self, number_of_games: int = 100):
        table_id = "cbcf6qas8fscb221"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_speed_baccarat_brasileiro_4(self, number_of_games: int = 100):
        table_id = "cbcf6qas8fscb224"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_baccarat_brasileiro_1(self, number_of_games: int = 100):
        table_id = "cbcf6qas8fscb222"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_turbo_baccarat_brasileiro_1(self, number_of_games: int = 100):
        table_id = "bcpirpmfpeobc192"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)