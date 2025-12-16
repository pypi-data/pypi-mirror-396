from typing import Union
from .session import PragmaticLiveSession
from .client import StatisticHistoryClient, PragmaticClient
from .generic_client import GenericClient
from .jogos_brasileiros import JogosBrasileiros
from .roleta import Roleta
from .game_shows import GameShows
from .bacara import Bacara
from .jogos_asiaticos import JogosAsiaticos
from .crash import Crash

class Games:
    def __init__(self, client_or_jsessionid: Union[PragmaticClient, str]):
        if isinstance(client_or_jsessionid, PragmaticClient):
            client = _PragmaticClientWrapper(client_or_jsessionid)
        else:
            client = StatisticHistoryClient(PragmaticLiveSession(), client_or_jsessionid)

        self.generic = GenericClient(client)
        self.jogos_brasileiros = JogosBrasileiros(client)
        self.roleta = Roleta(client)
        self.game_shows = GameShows(client)
        self.bacara = Bacara(client)
        self.jogos_asiaticos = JogosAsiaticos(client)
        self.crash = Crash(client)


class _PragmaticClientWrapper:
    def __init__(self, pragmatic_client: PragmaticClient):
        self._pragmatic_client = pragmatic_client
        self.session = pragmatic_client._session
        self.jsessionid = pragmatic_client.get_jsessionid()
    
    def get_history(self, table_id: str, number_of_games: int = 100):
        return self._pragmatic_client.get_history(table_id, number_of_games)