import time
from datetime import datetime, date
from typing import List


class Notice:
    def template(self):
        """message template"""
        pass

    def show(self, data):
        """prompt message"""
        pass

    @staticmethod
    def is_last_day_notice(log):
        return date.today().strftime('%Y-%m-%d') == datetime.utcfromtimestamp(log['date']).strftime('%Y-%m-%d')


class MarketNotice(Notice):
    def template(self):
        return "*Actualización diaria del mercado: * \n"

    def show(self, data):
        prompted = []
        for log in data:
            if self.is_last_day_notice(log):
                user = log['user']['name'] if log['user'] is not None else 'Mercado'
                points_last = sum(filter(None, log['fitness']))
                message = [f'*{user}*', "vende a", f'*{log["name"]}*', "por", str(log["price"]), "euros.",
                           str(points_last), "puntos conseguidos en las últimas 5 jornadas que suman un total de",
                           str(log['points']), "puntos \n"]
                if "is_high_cost" in log.keys():
                    message.append("y aparece en el *top 20 + caros* del mercado\n")
                prompted.append(" ".join(message))
        prompted.insert(0, self.template())
        return "\n".join(prompted)


class TransfersNotice(Notice):
    def template(self):
        return "*Últimos movimientos del mercado*"

    def show(self, data):
        prompted = []
        for day in data:
            for mov in day:
                if self.is_last_day_notice(day):
                    if "to" in mov.keys():
                        message = [f'*{mov["name"]}*', "ficha por", str(mov["to"]["name"]), "por", str(mov["amount"]), "euros",
                                   str(int((mov["amount"]-mov["price"])*100/mov['price'])), "% de diferencia sobre mercado desde hoy. \n"]
                        if "statusInfo" in mov.keys():
                            message.append(" ".join(["Duda por:", mov['statusInfo']]))
                        prompted.append(" ".join(message))
                    elif "from" in mov.keys():
                        message = [f'*{mov["from"]["name"]}*', "ha vendido a", f'*{mov["name"]}*', "a Mercado por",
                                   str(mov["amount"]), "euros,", str(int((mov["amount"]-mov["price"])*100/mov['price'])),
                                   "% de diferencia sobre mercado desde hoy. \n"]
                        if "statusInfo" in mov.keys():
                            message.append(" ".join([u'\U0001F915', "Duda por:", mov['statusInfo'], "\n"]))
                        prompted.append(" ".join(message))
        prompted.insert(0, self.template())
        return "\n".join(prompted)
