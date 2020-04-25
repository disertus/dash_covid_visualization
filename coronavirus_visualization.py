import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import mysql.connector
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

    # Daily stats for each category
    sick_daily = (dataframe.sick.iloc[-1] - dataframe.sick.iloc[-2], dataframe.sick.iloc[-2] - dataframe.sick.iloc[-3])
    cured_daily = dataframe.cured.iloc[-1] - dataframe.cured.iloc[-2]
    dead_daily = dataframe.dead.iloc[-1] - dataframe.dead.iloc[-2]
    tested_daily = dataframe.tested.iloc[-1] - dataframe.tested.iloc[-2]

    # print(((dataframe_reg.iloc[-1][1:] - dataframe_reg.iloc[-2][1:]) / dataframe_reg.iloc[-1][1:])*100)

    #Establishing a layout for the charts
    layout = dict({
    'title' : {'text' : 'Number of people infected: +%s today, +%s yesterday' % (sick_daily[0], sick_daily[1]),
                'font' : {'size' : 20, 
                'color':'#3EC283'}},
    'paper_bgcolor' : '#292727',
    'plot_bgcolor' : '#2A2727',
    'xaxis':{'color':'#3EC283'},
    'yaxis':{'color':'white'}
    })

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
        figure = go.Figure(data = (data_cured, data_dead), layout = self.layout)
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
        figure = go.Figure(data = data_letality, layout = self.layout)
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
        figure_sick_reg = go.Figure(data = data, layout = self.layout)
        return figure_sick_reg


# Add new entries to the SQL database
sql_db = MySQL_database()

# Show graph with subplots
viz = Visualization()

tabtitle = 'Covid19 in Ukraine'
myheading = 'Covid 19 in Ukraine - stats'

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    html.H1(myheading),
    html.Div(className='row',  # Define the row element
            children=[
                html.Div(className='six columns div-user-controls', 
                        children =[
                            dcc.Graph(
                                id='covid19_id',
                                figure=viz.sick_people(viz.dataframe_reg.keys()[1:], viz.dataframe_reg.iloc[-1][1:], 'Aggrnyl')
                            ),
                            html.Br(),
                            dcc.Graph(
                                id='covid19_lethality',
                                figure=viz.letality_rate()
                            ), 
                        ]
                ), # Define the left element

                html.Div(className='six columns div-for-charts',
                        children = [
                        dcc.Graph(
                            id='covid19_cured_vs_dead',
                            figure=viz.cured_vs_dead()
                        ),
                        html.Br(),
                        dcc.Graph(
                            id='covid19_sick_overall',
                            figure=viz.sick_people(viz.dataframe.date, viz.dataframe.sick, 'Aggrnyl')
                        )  # Define the right element
                        ]
                )
    ]
)])

if __name__ == '__main__':
    app.run_server(debug=True)
