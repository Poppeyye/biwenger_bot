from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class Plotter:
    def __init__(self, data: List[dict]):
        self.data = data
        self.type = type

    @staticmethod
    def append_value(dict_obj, key, value):
        if key in dict_obj:
            if not isinstance(dict_obj[key], list):
                dict_obj[key] = [dict_obj[key]]
            dict_obj[key].append(value)
        else:
            dict_obj[key] = value

    def data_of_interest(self):
        data = self.data
        doi = {}
        market_doi = []
        for player in data:
            if player['position'] != 1 and 'predictions' in player:
                [self.append_value(doi, col, player[col]) for col in ['name', 'per_min_played']]
                [self.append_value(doi, col, value) for col, value in player['predictions'].items()]
        df = pd.DataFrame.from_dict(doi)
        return df

    def line_plot(self):
        df = self.data_of_interest()

        animals=['giraffes', 'orangutans', 'monkeys']
        x = list(df.columns)
        x.pop(0)
        names = list(df['name'].values)
        lucas = df[df['name'] == "Lucas Vázquez"].values.tolist()[0]
        mojica = df[df['name'] == "Mojica"].values.tolist()[0]

        lucas.pop(0)
        fig = go.Figure(data=[
            go.Bar(name=names[0], x=x, y=lucas[:-1]),
            go.Bar(name="mojica", x=x, y=mojica[:-1])
        ])
        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_xaxes(showgrid=False)

        fig.show()