from .base_game import BaseGame

class JogosAsiaticos(BaseGame):
    def get_speed_baccarat_1(self, number_of_games: int = 100):
        table_id = "pwnhicogrzeodk79"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_dragon_tiger(self, number_of_games: int = 100):
        table_id = "drag0ntig3rsta48"
        fields = ["gameResult", "desc"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_baccarat_1(self, number_of_games: int = 100):
        table_id = "h22z8qhp17sa0vkh"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_sic_bo(self, number_of_games: int = 100):
        table_id = "sba71kkmr2ssba71"
        fields = ["die1", "die2", "die3", "megaWinFlag", "maxMegaMul"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_fortune_6_baccarat(self, number_of_games: int = 100):
        table_id = "bcpirpmfpobc1910"
        fields = ["playerHand", "bankerHand", "result", "fortune6"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_super_8_baccarat(self, number_of_games: int = 100):
        table_id = "bcpirpmfpeobc199"
        fields = ["playerHand", "bankerHand", "result", "super8"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_indonesian_mega_sic_bo(self, number_of_games: int = 100):
        table_id = "megasicboauto001"
        fields = ["die1", "die2", "die3", "megaWinFlag", "maxMegaMul"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_andar_bahar(self, number_of_games: int = 100):
        table_id = "jzbzy021lg8xy9i2"
        fields = ["result", "desc", "jokerScore", "cardValue", "andharCount", "baharCount", "jockerCount"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_squeeze_baccarat(self, number_of_games: int = 100):
        table_id = "bcadigitalsqz001"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_mega_baccarat(self, number_of_games: int = 100):
        table_id = "mbc371rpmfmbc371"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards", "d1", "d2", "sum", "mr", "mul"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_mega_sic_bac(self, number_of_games: int = 100):
        table_id = "a10megasicbaca10"
        fields = ["firstDouble", "secondDouble", "triple", "quad", "result", "p1", "p2", "b1", "b2"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_roullete_macao(self, number_of_games: int = 100):
        table_id = "yqpz3ichst2xg439"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_prive_lounge_baccarat_1(self, number_of_games: int = 100):
        table_id = "privbca51privbc1"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_korean_speed_baccarat_1(self, number_of_games: int = 100):
        table_id = "bc281koreanch281"
        fields = ["desc", "playerScore", "winningScore", "playerCards", "BankerCards"]
        return self._get_game_history(table_id, fields, number_of_games)
