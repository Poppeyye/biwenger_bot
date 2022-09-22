from typing import List

import pandas as pd
import plotly.express as px


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
        fig = px.scatter(df, x="succesful_passes", y="per_min_played", color="name",
                         facet_col="name", title="Using update_xaxes() With A Plotly Express Figure")

        fig.update_xaxes(showgrid=False)

        fig.show()