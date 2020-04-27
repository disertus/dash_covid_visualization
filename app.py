
# A very simple Flask Hello World app for you to get started with...

from flask import Flask

server = Flask(__name__)

@server.route('/')
def hello_world():
    return 'Hello from Flask!'

### Application

import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
import mysql.connector
import plotly.graph_objs as go
import pandas as pd

class MySQL_database:
    # Establish connection with the database    
    conn = mysql.connector.connect(
        user = 'root',
        password = '3a8n4m9qhhltp1r5',
        host = '35.246.212.65',
        database = 'covid'
    )
    curs = conn.cursor()

class Visualization:

    # 'r before the path is specified in order to avoid the unicode decoding error
    # sql_connect = sqlite3.connect(r'C:\Users\Roman\Google Диск\Python-Learning\coronavirus-research\covid19.db') 
    
    # Referring directly to a connection established inside the 'SQLite_database' class
    sql_connect = MySQL_database.conn
    
    # Transfering data from the SQLite database into pandas dataframe
    dataframe = pd.read_sql_query('SELECT * FROM casualties;', sql_connect)
    dataframe = dataframe.sort_values(by=['date'])
    dataframe_reg = pd.read_sql_query('SELECT * FROM casualties_reg;', sql_connect)
    dataframe_reg = dataframe_reg.sort_values(by=['date'])
    
    # Transfering data from the SQLite database into pandas dataframe
    dataframe = pd.read_csv('casualties.csv')
    dataframe = dataframe.sort_values(by=['date'])
    dataframe_reg = pd.read_csv('casualties_reg.csv')
    dataframe_reg = dataframe_reg.sort_values(by=['date'])

    # Daily stats for each category
    sick_daily = (dataframe.sick.iloc[-1] - dataframe.sick.iloc[-2], dataframe.sick.iloc[-2] - dataframe.sick.iloc[-3])
    cured_daily = (dataframe.cured.iloc[-1] - dataframe.cured.iloc[-2], dataframe.cured.iloc[-2] - dataframe.cured.iloc[-3])
    dead_daily = (dataframe.dead.iloc[-1] - dataframe.dead.iloc[-2], dataframe.dead.iloc[-2] - dataframe.dead.iloc[-3])
    tested_daily = dataframe.tested.iloc[-1] - dataframe.tested.iloc[-2]

    # print(((dataframe_reg.iloc[-1][1:] - dataframe_reg.iloc[-2][1:]) / dataframe_reg.iloc[-1][1:])*100)

    #Establishing a layout for the charts
    def chart_layout(self):
        layout = dict({
            'title' : {'text':'',
                        'font' : 
                            {'size' : 20,
                            'color':'#cecece'}},
            'paper_bgcolor' : '#312E2E',
            'plot_bgcolor' : '#312E2E',
            'xaxis':{'color':'#3EC283'},
            'yaxis':{'color':'white'},
            'hovermode':'x'
        })
        return layout

    def cured_vs_dead(self):
        '''Function visualizing the relation between the number of cured and dead people'''
        data_cured = go.Scatter(
            x = self.dataframe.date[-21:],
            y = self.dataframe.cured[-21:],
            line = dict(
                color = '#9EFF37',
                width = 3),
            fill = 'tonexty',
            name = 'Cured'
        )
        data_dead = go.Scatter(
            x = self.dataframe.date[-21:],
            y = self.dataframe.dead[-21:],
            line = dict(
                color = '#DD0000',
                width = 3),
            fill = 'tozeroy',
            name = 'Dead'
        )
        figure = go.Figure(data = (data_cured, data_dead), layout = self.chart_layout())
        figure.update_layout({"title": {"text": "Recovered vs Dead:"}})
        return figure


    def letality_rate(self):
        '''Function visualizing the letality rate: dead/(sick + cured)*100'''
        data_letality = go.Scatter(
            x = self.dataframe.date,
            y = (self.dataframe.dead/(self.dataframe.sick+self.dataframe.cured))*100,
            line = dict(
                color = '#FF8700',
                width = 3),
            fill = 'tonexty',
            name = 'Cured'
        )
        figure = go.Figure(data = data_letality, layout = self.chart_layout())
        figure.update_layout({"title": {"text": "Fatality vs Recovery rate (%):"}})
        return figure


    def sick_people(self, axis_x, axis_y, color_scale):
        '''Function visualizing the data packed into the dataframe created out of MySQL data'''

        self.dataframe_reg.set_index('date')
        data = go.Bar(
            x= axis_x,
            y= axis_y.tolist(),
            text = 'Infected',
            marker= {'color': axis_y,
                    'colorscale': color_scale}
        )
        figure_sick_reg = go.Figure(data = data, layout = self.chart_layout())
        figure_sick_reg.update_layout({"title": {"text": "Number of Sick people (overall):"}})        
        return figure_sick_reg

# Add new entries to the SQL database
sql_db = MySQL_database()
    
# Show graph with subplots
viz = Visualization()

tabtitle = 'Covid19 in Ukraine: latest numbers'

########### Initiate the app
app = dash.Dash(__name__, server = server, routes_pathname_prefix = '/dash/')
app.title=tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    html.H1('Covid-19 in Ukraine: latest numbers — {}'.format(datetime.date.today().strftime('%b %d %Y'))),
    # html.Div(className='ten columns offset-by-one',  # Define the row element
    #         children=[
                html.Div(className='row',
                        children=[
                    html.Div(className='nine columns div-bar-chart',
                            children =[
                                dcc.Graph(
                                    id='covid19_id',
                                    figure=viz.sick_people(viz.dataframe.date, viz.dataframe.sick, 'Aggrnyl')
                                ),
                            ]),
                    html.Div(className='three columns div-explainers',
                            children=[
                                html.H2('Lorem ipsum dolor sit amet'),
                                html.H3('Lorem ipsum dolor sit amet'),
                                html.H3('Lorem ipsum dolor sit amet')
                            ])
                ]),
                        
                html.Br(),
                html.Div(className='row',
                        children=[
                    html.Div(className='nine columns div-for-charts',
                            children = [
                                dcc.Graph(
                                        id='covid19_lethality',
                                        figure=viz.sick_people(viz.dataframe_reg.keys()[1:], viz.dataframe_reg.iloc[-1][1:], 'Aggrnyl')
                                    ),
                            ]),
                    html.Div(className='three columns div-explainers',
                            children=[
                                html.H2('Lorem ipsum dolor sit amet'),
                                html.H3('Lorem ipsum dolor sit amet'),
                                html.H3('Lorem ipsum dolor sit amet')
                            ])
                    ]),

                html.Br(),
                html.Div(className='row',
                        children=[
                    html.Div(className='nine columns div-for-charts',
                            children = [
                                dcc.Graph(
                                    id='covid19_cured_vs_dead',
                                    figure=viz.cured_vs_dead()
                                ),
                            ]),
                    html.Div(className='three columns div-explainers',
                            children=[
                                html.H2('Lorem ipsum dolor sit amet'),
                                html.H3('Lorem ipsum dolor sit amet'),
                                html.H3('Lorem ipsum dolor sit amet')
                            ])
                    ]),

                html.Br(),
                html.Div(className='row',
                        children=[
                    html.Div(className='nine columns div-charts',
                            children = [
                                dcc.Graph(
                                    id='covid19_sick_overall',
                                    figure=viz.letality_rate()
                                )  # Define the right element
                            ]),
                    html.Div(className='three columns div-explainers',
                            children=[
                                html.H2('Lorem ipsum dolor sit amet'),
                                html.H3('Lorem ipsum dolor sit amet'),
                                html.H3('Lorem ipsum dolor sit amet')
                            ])
                ]),

                # html.Div(className='row',
                #         children=[
                #     html.Div(className='six columns div-for-charts',
                #             children = [
                #             dcc.Graph(
                #                 id='covid19_cured_vs_dead',
                #                 figure=viz.cured_vs_dead()
                #             ),
                #             html.Br(),
                #             dcc.Graph(
                #                 id='covid19_sick_overall',
                #                 figure=viz.letality_rate()
                #             )  # Define the right element
                #             ]
                #     ),
                #     ]),
                # ]),
        html.Br(),
        html.H2('Charts are updated on daily basis, data is being collected from the following sources :'),
        html.A('\t\tCOVID-19 platform by the Cabinet of Ministers of Ukraine', href='https://covid19.com.ua/'),
        html.Br(),
        html.A('\t\tMinistry of Healthcare - Official website', href='https://moz.gov.ua/article/news/operativna-informacija-pro-poshirennja-koronavirusnoi-infekcii-2019-ncov-'),
        html.Br(),
        html.Br()
                ])

if __name__ == '__main__':
    app.run_server()
