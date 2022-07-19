class Notice:
    def template(self):
        """message template"""
        pass

    def show(self, data):
        """prompt message"""
        pass


class MarketNotice(Notice):
    def template(self):
        return "Actualización diaria del mercado: "

    def show(self, data):
        prompted = []
        for log in data:
            prompted.append(" ".join([log["name"], "por", str(log["price"]), "euros"]))
        prompted.insert(0, self.template())
        return "\n".join(prompted)
