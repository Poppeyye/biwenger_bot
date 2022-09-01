import json
import logging as logger
import os
from functools import lru_cache
from operator import itemgetter
from typing import List, Dict, Union

import requests_cache
import requests as requests

from biwenger.notices import Notice, MarketNotice, TransfersNotice, MatchNotice, RoundsNotice

url_login = 'https://biwenger.as.com/api/v2/auth/login'
url_account = 'https://biwenger.as.com/api/v2/account'
url_players_market = 'https://biwenger.as.com/api/v2/user?fields=players(id,owner),market(*,-userID),-trophies'
url_players_league = 'https://biwenger.as.com/api/v2/players/la-liga/'
url_retire_market = "https://biwenger.as.com/api/v2/market?player="
url_add_player_market = "https://biwenger.as.com/api/v2/market"
url_all_players = "https://cf.biwenger.com/api/v2/competitions/la-liga/data?lang=es&score=5&callback=jsonp_1465365486"
url_ranking = "https://biwenger.as.com/api/v2/rounds/league"
url_movement_notice = "https://biwenger.as.com/api/v2/league/742220/board?type=playerMovements,teamMovements&limit=8"
url_transfers = "https://biwenger.as.com/api/v2/league/742220/board?type=transfer,market"


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

    def get_players_in_market(self, free: bool) -> list:
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
        if free:
            market_players = [p for p in market_players if p['user'] is None]
        else:
            market_players = [p for p in market_players if p['user'] is not None]
        all_players = self.get_all_players_in_league()
        for offer in market_players:
            p = offer['player']['id']
            try:
                player = all_players[str(p)]
                offer.update(player)
                offer.update(self.get_player_extended_information(str(p)))
            except:
                print('Player not found')
            if self._is_high_cost_player(p):
                offer.update({"is_high_cost": self._is_high_cost_player(p)})
            full_market_info.append(offer)
        return [f for f in full_market_info if len(f) > 5]

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

        req = requests.get(url_all_players, headers=headers).text
        req_format = req.replace("jsonp_1465365486(", "")[:-1]
        all_players = json.loads(req_format)['data']['players']
        return all_players

    def get_next_round_time(self) -> Union[str, dict]:
        _, headers = self.get_account_info()
        req = requests.get(url_all_players, headers=headers).text
        req_format = req.replace("jsonp_1465365486(", "")[:-1]
        data = json.loads(req_format)['data']
        events = data['events']
        rounds = data['season']['rounds']
        if 'active' in [r['status'] for r in rounds]:
            return "active"
        else:
            next_round = [r for r in rounds if r['id'] == events[0]['round']['id']][0]
            next_round.update({'date': events[0]['date']})
            return next_round

    def get_last_user_transfers(self) -> List[Dict]:
        _, headers = self.get_account_info()
        transfers = requests.get(url_transfers, headers=headers).text
        movs = []
        all_players = self.get_all_players_in_league()
        for day in json.loads(transfers)['data']:
            content = day["content"]
            for mov in content:
                try:
                    info_player = all_players[str(mov["player"])]
                    mov_type = mov['type'] if 'type' in mov else 'transfer'
                    mov.update(info_player)
                    mov.update({'mov_type': mov_type})
                except:
                    print(f'Player {mov["player"]} not found')
            content = list(filter(lambda x: len(x) > 4, content))
            movs.append({'date': day['date'], 'content': content})
        return movs

    def get_player_extended_information(self, id_player: str):
        url_player_info = f"https://biwenger.as.com/api/v2/players/la-liga/{id_player}?" \
                          f"https://cf.biwenger.com/api/v2/players/la-liga/{id_player}?" \
                          "lang=es&fields=*,team,fitness,reports(points,home,events,status(status,statusInfo)," \
                          "match(*,round,home,away),star),prices,competition,seasons,news,threads&callback=jsonp_1505664437"
        _, headers = self.get_account_info()
        info = requests.get(url_player_info, headers=headers).text
        info_format = json.loads(info)['data']
        sofascore_url = info_format['partner']['2']["url"]
        canonical_url = info_format['canonicalURL']
        url = sofascore_url if sofascore_url != 'https://www.sofascore.com' else canonical_url
        last_5_prices = [price[1] for price in info_format['prices'][-5:]]
        last_season = [s for s in info_format['seasons'] if s['id'] == '2022' and s['name'] ==
                       'Temporada 2021/2022']
        if not last_season:
            last_season = {'games': 0, 'points': '0'}
        else:
            last_season = last_season[0]
        if 'competition' in last_season:  # bug in the game, avoid segunda división players appear in stats
            last_season['games'] = 0
        matches_last_season = last_season['games'] if 'games' in last_season \
                                                      and isinstance(last_season['games'], int) else 0
        points_last_season = last_season['points'] if 'points' in last_season \
                                                      and isinstance(last_season['points'], str) else '0'
        try:
            real_avg_points = float(points_last_season) / float(matches_last_season)
        except:
            real_avg_points = 0.0
        try:
            price_variance = ((last_5_prices[4] - last_5_prices[0]) / last_5_prices[0]) * 100
        except:
            price_variance = 0.0
        avg_points_total = float(points_last_season) / 34
        return {"url": url,
                "price_increment": "{:.2f}".format(price_variance),
                "avg_points_per_match": "{:.2f}".format(real_avg_points),
                "avg_total_points": "{:.2f}".format(avg_points_total),
                "total_points_last": str(points_last_season),
                "matches_played_last": matches_last_season}

    def get_matches_info(self):
        url_matches = 'https://cf.biwenger.com/api/v2/rounds/la-liga?score=5&lang=es&v=619&callback=jsonp_190019889'
        _, headers = self.get_account_info()

        req = requests.get(url_matches, headers=headers).text
        req_format = req.replace("jsonp_190019889(", "")[:-1]
        matches = json.loads(req_format)
        return matches['data']


if __name__ == '__main__':
    biwenger = BiwengerApi('alvarito174@hotmail.com', os.getenv("USER_PASS"))
    print(RoundsNotice().show(biwenger.get_next_round_time()))
    print(TransfersNotice().show(biwenger.get_last_user_transfers()))




