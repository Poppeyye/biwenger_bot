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
                [self.append_value(doi, col, player[col]) for col in ['name', 'per_min_played', 'pendingGames']]
                [self.append_value(doi, col, value) for col, value in player['predictions'].items()]
        df = pd.DataFrame.from_dict(doi)
        return df

    def line_plot(self):
        df = self.data_of_interest()
        df['Pass accuracy'] = df.apply(lambda c: (c['succesful_passes'])/(c['succesful_passes'] + c['unsuccesful_passes']), axis=1)*100
        df["Goal probability"] = df.apply(lambda c: (c['head_goal']+c['foot_goal']), axis=1)*100
        x = ['Pass accuracy', 'Goal probability']
        names = list(df['name'].values)
        # lucas = df[df['name'] == "Lucas Vázquez"].values.tolist()[0]
        # mojica = df[df['name'] == "Mojica"].values.tolist()[0]
        fig = go.Figure()
        for name in names:
            df_name = df[df['name'] == name]
            fig.add_trace(go.Bar(name=name, x=x, y=[float(df_name['Pass accuracy'].values),
                                                    float(df_name['Goal probability'].values)]))
    # Change the bar mode
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        fig.update_layout(
            title='US Export of Plastic Scrap',
            xaxis_tickfont_size=14,
            yaxis=dict(
                title='USD (millions)',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
            barmode='group',
            bargap=0.15, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1 # gap between bars of the same location coordinate.
        )
        fig.update_xaxes(showgrid=False)
        fig.update_layout( # customize font and legend orientation & position
            font_family="Rockwell",
            legend=dict(
                title=None, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
            )
        )
        fig.add_shape( # add a horizontal "target" line
            type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
            x0=0, x1=1, xref="paper", y0=950, y1=950, yref="y"
        )
        fig.show()