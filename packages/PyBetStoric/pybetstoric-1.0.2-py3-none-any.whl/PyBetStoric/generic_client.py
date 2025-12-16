from .client import StatisticHistoryClient

class GenericClient:
    def __init__(self, client: StatisticHistoryClient):
        self.client = client

    def get_full_history(self, table_id: str, number_of_games: int = 100):
        data = self.client.get_history(table_id, number_of_games)
        history = data.get("history", [])
        
        if not history:
            return []

        resultados = []
        for idx, game in enumerate(history[:number_of_games], start=1):
            rodada = dict(game)
            rodada["Rodada"] = idx
            resultados.append(rodada)

        return resultados

    def get_raw_response(self, table_id: str, number_of_games: int = 100):
        return self.client.get_history(table_id, number_of_games)

    def list_available_fields(self, table_id: str, sample_size: int = 1):
        data = self.client.get_history(table_id, sample_size)
        history = data.get("history", [])
        
        if not history:
            return []
        
        sample_game = history[0]
        return list(sample_game.keys())