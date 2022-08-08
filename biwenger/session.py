import json
import logging as logger
from functools import lru_cache
from operator import itemgetter
from typing import List, Dict

import requests_cache
import requests as requests

from biwenger.notices import Notice, MarketNotice, TransfersNotice

url_login = 'https://biwenger.as.com/api/v2/auth/login'
url_account = 'https://biwenger.as.com/api/v2/account'
url_players_market = 'https://biwenger.as.com/api/v2/user?fields=players(id,owner),market(*,-userID),-trophies'
url_players_league = 'https://biwenger.as.com/api/v2/players/la-liga/'
url_retire_market = "https://biwenger.as.com/api/v2/market?player="
url_add_player_market = "https://biwenger.as.com/api/v2/market"
url_all_players = "https://cf.biwenger.com/api/v2/competitions/la-liga/data?lang=es&score=5&callback=jsonp_1465365486"
url_ranking = "https://biwenger.as.com/api/v2/rounds/league"
url_movement_notice = "https://biwenger.as.com/api/v2/league/742220/board?type=playerMovements,teamMovements&limit=8"
url_transfers = "https://biwenger.as.com/api/v2/league/742220/board?type=transfer,market,exchange,loan,loanReturn,clauseIncrement&limit=8"


class BiwengerApi:

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.token = self._get_token()
        self.auth = 'Bearer ' + self.token

    def _get_token(self):
        logger.info("Login process")
        data = {"email": self.user, "password": self.password}
        headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*'}
        contents = requests.post(url_login, data=json.dumps(data), headers=headers).json()
        logger.info("contents: " + repr(contents))
        if "token" in contents:
            logger.info("call login ok!")
            return contents['token']
        else:
            logger.info("error in login call, status: " + contents['status'])
            return "error, status" + contents['status']

    @lru_cache(1)
    def get_account_info(self):
        headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*', 'X-Lang': 'es',
                   'Authorization': self.auth}
        result = requests.get(url_account, headers=headers).json()
        if result['status'] == 200:
            logger.info("call login ok!")
        id_league = result['data']['leagues'][1]['id']
        id_user = result['data']['leagues'][1]['user']['id']
        headers_league = {'Content-type': 'application/json', 'Accept': 'application/json, text/plain, */*',
                          'X-Lang': 'es',
                          'X-League': repr(id_league), 'X-User': repr(id_user), 'Authorization': self.auth}
        if result['status'] == 200:
            logger.info("call login ok!")
            return result, headers_league

    def get_players_in_market(self) -> list:
        """
        Get an update of the current players in market
        Returns a list of players (dicts) with some useful information
        :return:{'date': 1658207321, 'until': 1658293200, 'price': 1930000, 'player': {'id': 555}, 'user': None,
        'id': 555, 'name': 'Asenjo', 'slug': 'sergio-asenjo', 'teamID': 418, 'position': 1, 'fantasyPrice': 13000000,
        'status': 'ok', 'priceIncrement': 140000, 'playedHome': 0, 'playedAway': 0, 'fitness': [None, None, None,
        None, None], 'points': 0, 'pointsHome': 0, 'pointsAway': 0, 'pointsLastSeason': 26}
        """
        full_market_info = []
        account_info, headers = self.get_account_info()
        # league = account_info['data']['leagues'][1]  # Pick first one
        result = requests.get(url_add_player_market, headers=headers).json()
        market_players = result['data']['sales']
        # mkt_players_df = pd.DataFrame.from_dict(market_players)
        all_players = self.get_all_players_in_league()
        for offer in market_players:
            p = offer['player']['id']
            player = all_players[str(p)]
            offer.update(player)
            offer.update(self.get_player_extended_information(str(p)))
            if self._is_high_cost_player(p):
                offer.update({"is_high_cost": self._is_high_cost_player(p)})
            full_market_info.append(offer)
        return full_market_info

    def _is_high_cost_player(self, player_id) -> bool:
        all_players = self.get_all_players_in_league()
        top_n_players = sorted(list(all_players.values()), key=itemgetter('price'), reverse=True)[:20]
        for p in top_n_players:
            if int(player_id) == p['id']:
                return True
        return False

    def _is_top_player(self, player_id) -> bool:
        all_players = self.get_all_players_in_league()
        top_n_players = sorted(list(all_players.values()), key=itemgetter('points'), reverse=True)[:20]
        for p in top_n_players:
            if int(player_id) == p['id']:
                return True
        return False

    def get_all_players_in_league(self):
        _, headers = self.get_account_info()
        session = requests_cache.CachedSession('cache-requests', cache_control=True)

        req = session.get(url_all_players, headers=headers).text
        req_format = req.replace("jsonp_1465365486(", "")[:-1]
        all_players = json.loads(req_format)['data']['players']
        return all_players

    def get_last_user_transfers(self) -> List[List[Dict]]:
        _, headers = self.get_account_info()
        transfers = requests.get(url_transfers, headers=headers).text
        movs = []
        all_players = self.get_all_players_in_league()
        for day in json.loads(transfers)['data']:
            content = day["content"]
            for mov in content:
                try:
                    info_player = all_players[str(mov["player"])]
                    mov.update(info_player)
                except:
                    print(f'Player {mov["player"]} not found')
            content = list(filter(lambda x: len(x) > 4, content))
            movs.append(content)
        return movs

    def get_player_extended_information(self, id_player: str):
        url_player_info = f"https://biwenger.as.com/api/v2/players/la-liga/{id_player}?" \
                          f"https://cf.biwenger.com/api/v2/players/la-liga/{id_player}?" \
                          "lang=es&fields=*,team,fitness,reports(points,home,events,status(status,statusInfo)," \
                          "match(*,round,home,away),star),prices,competition,seasons,news,threads&callback=jsonp_1505664437"
        _, headers = self.get_account_info()
        session = requests_cache.CachedSession('extended_info', cache_control=True)
        info = session.get(url_player_info, headers=headers).text
        info_format = json.loads(info)['data']

        return {"url": info_format['partner']['2']["url"]}


if __name__ == '__main__':
    biwenger = BiwengerApi('alvarito174@hotmail.com', 'tomado74')

    print(MarketNotice().show(biwenger.get_players_in_market()))
    print(TransfersNotice().show(biwenger.get_last_user_transfers()))
