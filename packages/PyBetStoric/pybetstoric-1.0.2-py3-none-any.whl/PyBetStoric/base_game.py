from .client import StatisticHistoryClient

class BaseGame:
    def __init__(self, client: StatisticHistoryClient):
        self.client = client

    def _parse_history(self, data: dict, fields: list = None, number_of_games: int = 100):
        history = data.get("history", [])
        if not history:
            return []

        resultados = []
        for idx, game in enumerate(history[:number_of_games], start=1):
            rodada = {field: game.get(field) for field in fields} if fields else dict(game)
            rodada["Rodada"] = idx
            resultados.append(rodada)

        return resultados

    def _get_game_history(self, table_id: str, fields: list, number_of_games: int = 100):
        if not isinstance(number_of_games, int) or number_of_games < 1:
            raise ValueError("number_of_games deve ser um inteiro positivo")
        
        if number_of_games > 500:
            raise ValueError("number_of_games não pode ser maior que 500")
        
        if fields is not None and not isinstance(fields, list):
            raise TypeError("fields deve ser uma lista ou None")
        
        data = self.client.get_history(table_id, number_of_games)
        return self._parse_history(data, fields=fields, number_of_games=number_of_games)