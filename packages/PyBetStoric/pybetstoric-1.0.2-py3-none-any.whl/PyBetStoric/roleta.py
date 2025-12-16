from .base_game import BaseGame

class Roleta(BaseGame):
    def get_mega_wheel(self, number_of_games: int = 100):
        table_id = "md500q83g7cdefw1"
        fields = ["gameResult", "multiplier", "jackpotwheel", "rngSlot"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_mega_roulette_3000(self, number_of_games: int = 100):
        table_id = "megaroulette3k01"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_mega_roulette(self, number_of_games: int = 100):
        table_id = "1hl65ce1lxuqdrkr"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_auto_mega_roulette(self, number_of_games: int = 100):
        table_id = "1hl323e1lxuqdrkr"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_turkish_mega_roulette(self, number_of_games: int = 100):
        table_id = "megar0ul3tt3trk1"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_brasileira_roleta(self, number_of_games: int = 100):
        table_id = "rwbrzportrwa16rg"
        fields = ["gameResult", "megaSlots", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_brasileira_mega_roleta(self, number_of_games: int = 100):
        table_id = "mrbras531mrbr532"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_roulette_1(self, number_of_games: int = 100):
        table_id = "g03y1t9vvuhrfytl"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_roulette_2_extra_time(self, number_of_games: int = 100):
        table_id = "5kvxlw4c1qm3xcyn"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_roulette_3(self, number_of_games: int = 100):
        table_id = "chroma229rwltr22"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_speed_auto_roulette(self, number_of_games: int = 100):
        table_id = "autorwra311autor"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_speed_roulette_1(self, number_of_games: int = 100):
        table_id = "fl9knouu0yjez2wi"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_speed_roulette_2(self, number_of_games: int = 100):
        table_id = "r20speedrtwo201s"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_auto_roulette(self, number_of_games: int = 100):
        table_id = "5bzl2835s5ruvweg"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_vip_auto_roulette(self, number_of_games: int = 100):
        table_id = "ar25vipautorw251"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)
    
    def get_vip_roulette(self, number_of_games: int = 100):
        table_id = "geogamingh2rw545"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_roullete_macao(self, number_of_games: int = 100):
        table_id = "yqpz3ichst2xg439"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_lucky_6_roulette(self, number_of_games: int = 100):
        table_id = "lucky6roulettea3"
        fields = ["gameResult", "megaSlots", "megaPayouts", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_immersive_roulette_deluxe(self, number_of_games: int = 100):
        table_id = "25irclas25imrcrw"
        fields = ["gameResult", "powerUpList", "powerUpMultipliers", "resultMultiplier", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_fortune_roulette(self, number_of_games: int = 100):
        table_id = "megaroulettbba91"
        fields = ["gameResult", "powerUpThresholdReached", "frWinType", "frMul", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_powerup_roulette(self, number_of_games: int = 100):
        table_id = "powruprw1qm3xc25"
        fields = ["gameResult", "powerUpList", "powerUpMultipliers", "resultMultiplier", "powerUpThresholdReached", "fortuneRoulette", "powerUpRoulette", "megaRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)
    
    def get_prive_lounge_roulette(self, number_of_games: int = 100):
        table_id = "privroulettegt01"
        fields = ["gameResult", "privateRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_prive_lounge_roulette_deluxe(self, number_of_games: int = 100):
        table_id = "privroudeluxgt01"
        fields = ["gameResult", "privateRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_french_roulette_la_partage(self, number_of_games: int = 100):
        table_id = "frenchroulette01"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_roulette_italia_tricolore(self, number_of_games: int = 100):
        table_id = "v1c52fgw7yy02upz"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_korean_roulette(self, number_of_games: int = 100):
        table_id = "381rwkr381korean"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_thai_roulette(self, number_of_games: int = 100):
        table_id = "thairwa13generw1"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)
    
    def get_american_roulette(self, number_of_games: int = 100):
        table_id = "americanroule296"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_vietnamese_roulette(self, number_of_games: int = 100):
        table_id = "vietnamr32genric"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_russian_roulette(self, number_of_games: int = 100):
        table_id = "t4jzencinod6iqwi"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_german_roulette(self, number_of_games: int = 100):
        table_id = "s2x6b4jdeqza2ge2"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_roulette_latina(self, number_of_games: int = 100):
        table_id = "roulerw234rwl292"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_turkish_roulette(self, number_of_games: int = 100):
        table_id = "p8l1j84prrmxzyic"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_roumanian_roulette(self, number_of_games: int = 100):
        table_id = "romania233rwl291"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)

    def get_speed_roulette_latina(self, number_of_games: int = 100):
        table_id = "cosproulttf8s6sr"
        fields = ["gameResult", "powerUpThresholdReached", "fortuneRoulette", "megaRoulette", "powerUpRoulette"]
        return self._get_game_history(table_id, fields, number_of_games)
