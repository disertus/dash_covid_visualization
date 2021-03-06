
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from flask import Flask

server = Flask(__name__)


class Visualization:

    # Transfering data from the SQLite database into pandas dataframe
    dataframe = pd.read_csv("casualties.csv")
    dataframe = dataframe.sort_values(by=["date"])
    dataframe_reg = pd.read_csv("casualties_reg.csv")
    dataframe_reg = dataframe_reg.sort_values(by=["date"])

    # Daily stats for each category
    sick_daily = (
        dataframe.sick.iloc[-1] - dataframe.sick.iloc[-2],
        dataframe.sick.iloc[-2] - dataframe.sick.iloc[-3],
    )
    cured_daily = (
        dataframe.cured.iloc[-1] - dataframe.cured.iloc[-2],
        dataframe.cured.iloc[-2] - dataframe.cured.iloc[-3],
    )
    dead_daily = (
        dataframe.dead.iloc[-1] - dataframe.dead.iloc[-2],
        dataframe.dead.iloc[-2] - dataframe.dead.iloc[-3],
    )
    tested_daily = (
        dataframe.tested.iloc[-1] - dataframe.tested.iloc[-2],
        dataframe.tested.iloc[-2] - dataframe.tested.iloc[-3],
    )

    # print(((dataframe_reg.iloc[-1][1:] - dataframe_reg.iloc[-2][1:]) / dataframe_reg.iloc[-1][1:])*100)

    # Establishing a layout for the charts
    def chart_layout(self):
        layout = dict(
            {
                "title": {"text": "", "font": {"size": 20, "color": "#cecece"}},
                "paper_bgcolor": "#312E2E",
                "plot_bgcolor": "#312E2E",
                "xaxis": {"color": "#3EC283"},
                "yaxis": {"color": "white"},
                "hovermode": "x",
                "showlegend": False,
                "xaxis_showgrid": False,
            }
        )
        return layout

    def cured_vs_dead(self):
        """Function visualizing the relation between the number of cured and dead people"""
        data_cured = go.Scatter(
            x=self.dataframe.date[10:],
            y=self.dataframe.cured[10:],
            line=dict(color="#9EFF37", width=3),
            fill="tonexty",
            name="Cured",
        )
        data_dead = go.Scatter(
            x=self.dataframe.date[10:],
            y=self.dataframe.dead[10:],
            line=dict(color="#DD0000", width=3),
            fill="tozeroy",
            name="Dead",
        )
        figure = go.Figure(data=(data_cured, data_dead), layout=self.chart_layout())
        figure.update_layout({"title": {"text": "Recovered vs Dead (overall):"}})
        return figure

    def fatality_rate(self):
        """Function visualizing the fatality rate: dead/(sick + cured)*100"""
        data_fatality = go.Scatter(
            x=self.dataframe.date[10:],
            y=(self.dataframe.dead[10:] / self.dataframe.sick[10:]).round(decimals=4) * 100,
            line=dict(color="#FF8700", width=3),
            fill="tozeroy",
            name="Fatality",
        )
        data_recovery = go.Scatter(
            x=self.dataframe.date[10:],
            y=(self.dataframe.cured[10:] / self.dataframe.sick[10:]).round(decimals=4) * 100,
            line=dict(color="#057BF2", width=3),
            fill="tonexty",
            name="Recovery",
        )
        figure = go.Figure(
            data=(data_recovery, data_fatality), layout=self.chart_layout()
        )
        figure.update_layout({"title": {"text": "Fatality vs Recovery rate (%):"}})
        return figure

    def sick_people(self, axis_x, axis_y, color_scale):
        """Function visualizing the data packed into the dataframe created out of MySQL data"""

        self.dataframe_reg.set_index("date")
        data = go.Bar(
            x=axis_x,
            y=axis_y.tolist(),
            text="Infected",
            marker={"color": axis_y, "colorscale": color_scale},
        )
        figure_sick_reg = go.Figure(data=data, layout=self.chart_layout())
        figure_sick_reg.update_layout(
            {"title": {"text": "Number of Sick people (overall):"}}
        )
        return figure_sick_reg

    def tested_people(self):
        """Function visualizing the data about people tested """

        data_tests = go.Scatter(
            x=self.dataframe.date[10:],
            y=self.dataframe.tested[10:],
            text="Tested",
            fill="tozeroy",
            line=dict(color="#B785FF", width=3),
        )
        figure_tested = go.Figure(data=data_tests, layout=self.chart_layout())
        figure_tested.update_layout({"title": {"text": "People Tested (overall):"}})
        return figure_tested


# Show graph with subplots
viz = Visualization()

tabtitle = "Covid19 in Ukraine: latest numbers"

########### Initiate the app
app = dash.Dash(__name__, server=server)
app.title = tabtitle

########### Set up the layout
app.layout = html.Div(
    children=[
        html.H1(
            f'Covid-19 in Ukraine: latest numbers — {datetime.date.today().strftime("%b %d %Y")}'
        ),
        # html.Div(className='ten columns offset-by-one',  # Define the row element
        #         children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="nine columns div-bar-chart",
                    children=[
                        dcc.Graph(
                            id="covid19_id",
                            figure=viz.sick_people(
                                viz.dataframe.date[10:],
                                viz.dataframe.sick[10:],
                                "Aggrnyl",
                            ),
                        ),
                    ],
                ),
                html.Div(
                    className="three columns div-explainers",
                    children=[
                        html.H2(f"Total: {viz.dataframe.sick.iloc[-1]} cases"),
                        html.H3(f"Today:  +{viz.sick_daily[0]} cases"),
                        html.H3(f"Yesterday:  +{viz.sick_daily[1]} cases"),
                    ],
                ),
            ],
        ),
        html.Br(),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="nine columns div-for-charts",
                    children=[
                        dcc.Graph(
                            id="covid19_lethality",
                            figure=viz.sick_people(
                                viz.dataframe_reg.keys()[1:],
                                viz.dataframe_reg.iloc[-1][1:],
                                "Aggrnyl",
                            ),
                        ),
                    ],
                ),
                html.Div(
                    className="three columns div-explainers",
                    children=[
                        html.H2("Cases by regions"),
                        html.H3("Highest today:"),
                        html.H3("Region +# cases"),
                        html.Br(),
                        html.H3("Lowest today:"),
                        html.H3("Region +# cases"),
                    ],
                ),
            ],
        ),
        html.Br(),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="nine columns div-for-charts",
                    children=[
                        dcc.Graph(
                            id="covid19_cured_vs_dead", figure=viz.cured_vs_dead()
                        ),
                    ],
                ),
                html.Div(
                    className="three columns div-explainers",
                    children=[
                        html.H2(f"Recovery:  {viz.dataframe.cured.iloc[-1]} cases"),
                        html.H3(f"Recovered today: +{viz.cured_daily[0]}"),
                        html.H3(f"Recovered yesterday: +{viz.cured_daily[1]}"),
                        html.Br(),
                        html.H2(f"Deaths:  {viz.dataframe.dead.iloc[-1]} cases"),
                        html.H3(f"Died today: + {viz.dead_daily[0]}"),
                        html.H3(f"Died yesterday: + {viz.dead_daily[1]}"),
                    ],
                ),
            ],
        ),
        html.Br(),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="nine columns div-charts",
                    children=[
                        dcc.Graph(
                            id="covid19_sick_overall", figure=viz.fatality_rate()
                        )  # Define the right element
                    ],
                ),
                html.Div(
                    className="three columns div-explainers",
                    children=[
                        html.H2("Current ratio"),
                        html.H3(
                            f"Recovery: {(viz.dataframe.cured / viz.dataframe.sick * 100).round(decimals=2).iloc[-1]} %"
                        ),
                        html.H3(
                            f"Fatality: {(viz.dataframe.dead / viz.dataframe.sick * 100).round(decimals=2).iloc[-1]} %"
                        ),
                    ],
                ),
            ],
        ),
        html.Br(),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="nine columns div-charts",
                    children=[
                        dcc.Graph(id="covid19_tested", figure=viz.tested_people(),),
                    ],
                ),
                html.Div(
                    className="three columns div-explainers",
                    children=[
                        html.H2(f"Total tested: {viz.dataframe.tested.iloc[-1]}"),
                        html.H3(f"Today:  +{viz.tested_daily[0]}"),
                        html.H3(f"Yesterday:  +{viz.tested_daily[1]}"),
                        html.H3(
                            f"Tested {(viz.dataframe.tested.iloc[-1]/41980000*100).round(decimals=2)} % out of 41,98 M"
                        ),
                    ],
                ),
            ],
        ),
        html.Br(),
        html.H4(
            "Charts are updated on daily basis, data is being collected from the following sources :"
        ),
        html.A(
            "\t\tCOVID-19 platform by the Cabinet of Ministers of Ukraine",
            href="https://covid19.com.ua/",
        ),
        html.Br(),
        html.A(
            "\t\tMinistry of Healthcare - Official website",
            href="https://moz.gov.ua/article/news/operativna-informacija-pro-poshirennja-koronavirusnoi-infekcii-2019-ncov-",
        ),
        html.Br(),
        html.Br(),
    ]
)

if __name__ == "__main__":
    app.run_server()
