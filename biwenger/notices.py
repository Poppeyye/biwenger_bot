class Notice:
    def template(self):
        """message template"""
        pass

    def show(self, data):
        """prompt message"""
        pass


class MarketNotice(Notice):
    def template(self):
        return "*Actualización diaria del mercado: *"

    def show(self, data):
        prompted = []
        for log in data:
            message = [log["name"], "por", str(log["price"]), "euros"]
            if "is_high_cost" in log.keys():
                message.append("y aparece en el top 20 + caros del mercado")
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
                message = [mov["name"], "ficha por", str(mov["to"]["name"]), "por ", str(mov["amount"]) + " euros ",
                           str(mov["amount"]-mov["price"]), "euros de diferencia sobre mercado"]
                prompted.append(" ".join(message))
        prompted.insert(0, self.template())
        return "\n".join(prompted)
