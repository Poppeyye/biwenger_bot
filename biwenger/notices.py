class Notice:
    def template(self):
        """message template"""
        pass

    def show(self, data):
        """prompt message"""
        pass


class MarketNotice(Notice):
    def template(self):
        return "*Actualización diaria del mercado: * \n"

    def show(self, data):
        prompted = []
        for log in data:
            user = log['user'] if log['user'] is not None else 'Mercado'
            points_last = sum(filter(None, log['fitness']))
            message = [f'*{user}*', "vende a", f'*{log["name"]}*', "por", str(log["price"]), "euros.",
                       str(points_last), "puntos conseguidos en las últimas 5 jornadas que suman un total de",
                       str(log['points']), "puntos \n"]

            if "is_high_cost" in log.keys():
                message.append("y aparece en el *top 20 + caros* del mercado")
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
                if "to" in mov.keys():
                    message = [f'*{mov["name"]}*', "ficha por", str(mov["to"]["name"]), "por", str(mov["amount"]), "euros",
                               str(mov["amount"]-mov["price"]), "euros de diferencia sobre mercado desde hoy. \n"]
                    if "statusInfo" in mov.keys():
                        message.append(" ".join(["Duda por:", mov['statusInfo']]))
                    prompted.append(" ".join(message))
                elif "from" in mov.keys():
                    message = [f'*{mov["from"]["name"]}*', "ha vendido a", f'*{mov["name"]}*', "a Mercado por",
                               str(mov["amount"]), "euros,", str(mov["amount"]-mov["price"]),
                               "euros de diferencia sobre mercado desde hoy. \n"]
                    if "statusInfo" in mov.keys():
                        message.append(" ".join([u'\U0001F915', "Duda por:", mov['statusInfo'], "\n"]))
                    prompted.append(" ".join(message))
        prompted.insert(0, self.template())
        return "\n".join(prompted)
