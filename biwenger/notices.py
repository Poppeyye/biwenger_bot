from datetime import datetime, date, timedelta
from enum import Enum
from typing import List, Dict


class Notice:
    """
    Notice class displays a custom message for any of the functionalities defined in the app.
    You can create any notice by extending this class
    """

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
            return '\U00002197'
        elif t == 0.0:
            return '\U000027A1'
        else:
            return '\U00002B07'

    def show(self, data):
        prompted = []
        temp = self.template()
        if data[0]['user'] is None:
            temp = temp + " *FREE AGENTS* \n"  # edit template message if <free> flag is activated
        for log in data:
            if self.is_last_day_notice(log):
                user = log['user']['name'] if log['user'] is not None else 'Mercado'

                points_last = sum([p for p in log['fitness'] if isinstance(p, int)])
                pos = log['position']
                message = [f'*{user}*', 'vende a', f'[{log["name"]} ({Position(pos).name})]({log["url"]})', 'por',
                           "{:,}€".format((log["price"])), "\n",
                           f'_% Minutes Played_: {log["per_min_played"]}\n',
                           f'_Matches not played_: {log["matches_bench"]}\n',
                           f'_Total points_: {str(log["points"])}\n',
                           f'_Last 5d sum_: {str(points_last)}\n',
                           f'_Price trend 5d_: {log["price_increment"]}%',
                           self.trend_emote(log["price_increment"]) + '\n',
                           f'*2021/2022 Stats:*\n',
                           f'_Total points_: {log["total_points_last"]}\n',
                           f'_Matches played_: {log["matches_played_last"]}\n'
                           f' _Relative Avg points_: {log["avg_points_per_match"]}\n',
                           f'_Absolute avg points_: {log["avg_total_points"]}\n']
                if "is_high_cost" in log.keys():
                    message.append("y aparece en el *top 20 + caros* del mercado\n")
                if "statusInfo" in log.keys():
                    message.append(' '.join([u'\U0001F915', 'Estado:', log["statusInfo"], '\n']))
                prompted.append(" ".join(message))
        prompted.insert(0, temp)
        return "\n".join(prompted)


class TransfersNotice(Notice):
    def template(self):
        return f"*Últimos movimientos del mercado {date.today().strftime('%Y-%m-%d')}*: \n"

    def show(self, data):
        prompted = []
        for day in data:
            for mov in day['content']:
                message = []
                if "to" in mov.keys():
                    if int(mov["amount"]) > 12000000:
                        message.append(u'\U0001F525')
                    if mov['mov_type'] == 'clause':
                        message.append(" ".join(["\U0001F400", "*Clausulazo!*", "la rata de",
                                                 f'*{str(mov["to"]["name"])}*', "ha robado a", f'*{mov["name"]}*',
                                                 "por", "{:,}€".format((mov["amount"])),
                                                 str(int((mov["amount"] - mov["price"]) * 100 / mov['price'])),
                                                 "% de diferencia sobre su valor. \n"]))
                    else:
                        message.append(" ".join([f'*{mov["name"]}*', "ficha por", f'*{str(mov["to"]["name"])}*', "por",
                                                 "{:,}€".format((mov["amount"])),
                                                 str(int((mov["amount"] - mov["price"]) * 100 / mov['price'])),
                                                 "% de diferencia sobre "
                                                 "mercado desde hoy. \n"]))

                    if "statusInfo" in mov.keys():
                        message.append(" ".join([u'\U0001F915', 'Duda por:', mov["statusInfo"], '\n']))
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


class RoundsNotice(Notice):

    def show(self, data):
        if isinstance(data, str):
            return "*¡Jornada en curso!*" + '\U0001f340'
        elif isinstance(data, dict):
            days_left = self.days_diff(data['date'])
            if days_left < timedelta(hours=24):
                blog_url = data['blog'] if 'blog' in data else ''
                return " ".join(["\U000026BD", "*Hoy empieza la jornada!*", "\U000026BD\n",
                                 "Consulta aquí las alineaciones probables -> ",
                                 f'[{data["name"]}]({blog_url})'])
            else:
                format_date = str(self.format_timedelta(days_left))
                return '\U000023F1' + "*Tiempo hasta la siguiente jornada*: " + format_date

    @staticmethod
    def days_diff(d):
        days = (datetime.utcfromtimestamp(d) + timedelta(hours=2)) - datetime.today()
        return days

    @staticmethod
    def format_timedelta(delta: timedelta) -> str:
        """Formats a timedelta duration to [N days] %H:%M:%S format"""
        seconds = int(delta.total_seconds())

        secs_in_a_day = 86400
        secs_in_a_hour = 3600
        secs_in_a_min = 60

        days, seconds = divmod(seconds, secs_in_a_day)
        hours, seconds = divmod(seconds, secs_in_a_hour)
        minutes, seconds = divmod(seconds, secs_in_a_min)

        time_fmt = f"{hours:02d}:{minutes:02d}"

        if days > 0:
            suffix = "s" if days > 1 else ""
            return f"{days} día{suffix} {time_fmt}"

        return time_fmt


class Position(Enum):
    PT = 1
    DF = 2
    MC = 3
    DL = 4
