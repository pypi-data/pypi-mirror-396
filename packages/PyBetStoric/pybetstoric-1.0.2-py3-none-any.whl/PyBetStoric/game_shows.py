from .base_game import BaseGame

class GameShows(BaseGame):
    def get_sweet_bonanza_candyland(self, number_of_games: int = 100):
        table_id = "pbvzrfk1fyft4dwe"
        fields = ["gameResult", "multiplier", "payout", "sugarbomb", "rc", "sbmul"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_24d_spin(self, number_of_games: int = 100):
        table_id = "24dspin000000001"
        fields = ["winningNumber", "resultDesc", "color", "even", "red"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_mega_roulette_3000(self, number_of_games: int = 100):
        table_id = "megaroulette3k01"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_sic_bo(self, number_of_games: int = 100):
        table_id = "sba71kkmr2ssba71"
        fields = ["die1", "die2", "die3", "megaWinFlag", "maxMegaMul"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_indonesian_mega_sic_bo(self, number_of_games: int = 100):
        table_id = "megasicboauto001"
        fields = ["die1", "die2", "die3", "megaWinFlag", "maxMegaMul"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_mega_sic_bac(self, number_of_games: int = 100):
        table_id = "a10megasicbaca10"
        fields = ["firstDouble", "secondDouble", "triple", "quad", "result", "p1", "p2", "b1", "b2"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_auto_mega_roulette(self, number_of_games: int = 100):
        table_id = "1hl323e1lxuqdrkr"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_lucky_6_roulette(self, number_of_games: int = 100):
        table_id = "lucky6roulettea3"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_mega_roulette(self, number_of_games: int = 100):
        table_id = "1hl65ce1lxuqdrkr"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_football_blitz_top_card(self, number_of_games: int = 100):
        table_id = "ge49e4os88bp4bi6"
        fields = ["gameResult", "desc", "result", "cardDiff"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_fortune_roulette(self, number_of_games: int = 100):
        table_id = "megaroulettbba91"
        fields = ["gameResult", "powerUpThresholdReached", "frWinType", "frMul", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_powerup_roulette(self, number_of_games: int = 100):
        table_id = "powruprw1qm3xc25"
        fields = ["gameResult", "powerUpList", "powerUpMultipliers", "resultMultiplier", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_brasileira_mega_roleta(self, number_of_games: int = 100):
        table_id = "mrbras531mrbr532"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_money_time(self, number_of_games: int = 100):
        table_id = "moneytime2500002"
        fields = ["gameResult", "multiplierValue", "boosterMultiplier"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_dice_city(self, number_of_games: int = 100):
        table_id = "boomorbustccny01"
        fields = ["gameResult", "rc", "boosterMul"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_mega_wheel(self, number_of_games: int = 100):
        table_id = "md500q83g7cdefw1"
        fields = ["gameResult", "multiplier", "jackpotwheel", "rngSlot"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_treasure_island(self, number_of_games: int = 100):
        table_id = "treasureadvgt001"
        fields = ["gameResult", "rc", "betCodePayoffMap", "boosterMul", "payoutMul", "finalMul", "boosterWin", "bingoBallCount", "minMul", "maxMul", "blmDiceTotal", "bonusGame"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_turkish_mega_roulette(self, number_of_games: int = 100):
        table_id = "megar0ul3tt3trk1"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)
