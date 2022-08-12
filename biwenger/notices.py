import time
from datetime import datetime, date, timedelta
from enum import Enum
from typing import List, Dict


class Notice:
    def template(self):
        """message template"""
        pass

    def show(self, data):
        """prompt message"""
        pass

    @staticmethod
    def is_last_day_notice(log):
        return (date.today()).strftime('%Y-%m-%d-%h') == datetime.utcfromtimestamp(log['date']).strftime(
            '%Y-%m-%d-%h') or \
               (date.today() - timedelta(hours=9)).strftime('%Y-%m-%d-%h') == \
               datetime.utcfromtimestamp(log['date']).strftime('%Y-%m-%d-%h')


class MarketNotice(Notice):
    def template(self):
        return f"*Actualización diaria del mercado {date.today().strftime('%Y-%m-%d')}: * \n"

    @staticmethod
    def trend_emote(trend_qty: str):
        t = float(trend_qty)
        if t > 10.0:
            return 2 * '\U00002B06'
        if 10.0 > t > 5.0:
            return '\U00002B06'
        elif 5.0 > t > 0.0:
            return "\U00002197"
        elif t == 0.0:
            return "\U000027A1"
        else:
            return "\U00002B07"

    def show(self, data):
        prompted = []
        for log in data:
            if self.is_last_day_notice(log):
                user = log['user']['name'] if log['user'] is not None else 'Mercado'
                points_last = sum(filter(None, log['fitness']))
                pos = log['position']
                message = [f'*{user}*', "vende a", f'[{log["name"]} ({Position(pos).name})]({log["url"]})', "por",
                           "{:,}€".format((log["price"])), "\n",
                           f'_Total points_: {str(log["points"])}\n',
                           f'_Last 5d sum_: {str(points_last)}\n',
                           f'_Price trend 5d_: {log["price_increment"]}%',
                           self.trend_emote(log["price_increment"]) + "\n",
                           f'*2021-2022 Stats: * \n'
                           f'_Total points_: {log["total_points_last"]}\n',
                           f'_Matches played_: {log["matches_played_last"]}\n'
                           f'_Relative Avg points_: {log["avg_points_per_match"]}\n',
                           f'_Absolute avg points_: {log["avg_total_points"]}\n']
                if "is_high_cost" in log.keys():
                    message.append("y aparece en el *top 20 + caros* del mercado\n")
                if "statusInfo" in log.keys():
                    message.append(" ".join([u'\U0001F915', "Estado:", log['statusInfo'], "\n"]))
                prompted.append(" ".join(message))
        prompted.insert(0, self.template())
        return "\n".join(prompted)


class TransfersNotice(Notice):
    def template(self):
        return f"*Últimos movimientos del mercado {date.today().strftime('%Y-%m-%d')}*: \n"

    def show(self, data):
        prompted = []
        for day in data:
            if self.is_last_day_notice(day):
                for mov in day['content']:
                    message = []
                    if "to" in mov.keys():
                        if int(mov["amount"]) > 12000000:
                            message.append(u'\U0001F525')
                        message.append(" ".join([f'*{mov["name"]}*', "ficha por", f'*{str(mov["to"]["name"])}*', "por",
                                                 "{:,}€".format((mov["amount"])),
                                                 str(int((mov["amount"] - mov["price"]) * 100 / mov['price'])),
                                                 "% de diferencia sobre "
                                                 "mercado desde hoy. \n"]))

                        if "statusInfo" in mov.keys():
                            message.append(" ".join([u'\U0001F915', "Duda por:", mov['statusInfo'], "\n"]))
                        prompted.append(" ".join(message))
                    elif "from" in mov.keys():
                        message = [f'*{mov["from"]["name"]}*', "ha vendido a", f'*{mov["name"]}*', "a Mercado por",
                                   "{:,}€".format((mov["amount"])),
                                   str(int((mov["amount"] - mov["price"]) * 100 / mov['price'])),
                                   "% de diferencia sobre mercado. \n"]
                        if "statusInfo" in mov.keys():
                            message.append(" ".join([u'\U0001F915', "Duda por:", mov['statusInfo'], "\n"]))
                        prompted.append(" ".join(message))
        prompted.insert(0, self.template())
        return "\n".join(prompted)


class MatchNotice(Notice):
    def template(self):
        return "*Hoy es día de Jornada!!* " + u'\U000026BD'

    def show(self, data):
        prompted = []
        if self.is_match_day(data['games']):
            message = ['Toda la info de la jornada aquí ->', f'[{data["name"]}]({data["canonicalURL"]})']
            prompted.append(" ".join(message))

        else:
            return None
        prompted.insert(0, self.template())
        return "\n".join(prompted)

    @staticmethod
    def is_match_day(games: List[Dict]) -> bool:
        if datetime.utcfromtimestamp(games[0]['date']).strftime('%Y-%m-%d') == (date.today()).strftime('%Y-%m-%d'):
            return True
        else:
            return False


class Position(Enum):
    PT = 1
    DF = 2
    MC = 3
    DL = 4
