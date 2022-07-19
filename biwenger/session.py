import json
import logging as logger
from functools import lru_cache

import requests as requests

url_login = 'https://biwenger.as.com/api/v2/auth/login'
url_account = 'https://biwenger.as.com/api/v2/account'
url_players_market = 'https://biwenger.as.com/api/v2/user?fields=players(id,owner),market(*,-userID),-trophies'
url_players_league = 'https://biwenger.as.com/api/v2/players/la-liga/'
url_retire_market = "https://biwenger.as.com/api/v2/market?player="
url_add_player_market = "https://biwenger.as.com/api/v2/market"
url_all_players = "https://cf.biwenger.com/api/v2/competitions/la-liga/data?lang=es&score=5&callback=jsonp_1465365486"
url_ranking = "https://biwenger.as.com/api/v2/rounds/league"
url_player_stats = "https://biwenger.as.com/api/v2/owners/player/luis-maximiano"
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
        return market_players

    def get_all_players_in_league(self):
        _, headers = self.get_account_info()
        req = requests.get(url_all_players, headers=headers).text
        req_format = req.replace("jsonp_1465365486(","")[:-1]
        all_players = json.loads(req_format)['data']['players']
        return all_players

    def get_last_user_transfers(self):
        _, headers = self.get_account_info()
        req = requests.get(url_transfers, headers=headers).text
        req_format = req.replace("jsonp_1465365486(","")[:-1]
        all_players = json.loads(req_format)['data']['players']
        return all_players


if __name__ == '__main__':
    biwenger = BiwengerApi('alvarito174@hotmail.com', 'tomado74')
    players_mkt = biwenger.get_last_user_transfers()
