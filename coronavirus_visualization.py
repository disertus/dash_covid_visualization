import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import mysql.connector
import pandas as pd


class Visualization:
    
    # Transfering data from the SQLite database into pandas dataframe
    dataframe_reg = pd.read_csv('casualties.csv')
    dataframe_reg = dataframe_reg.sort_values(by=['date']) 

    # Daily stats for each category
    sick_daily = (dataframe_reg.sick.iloc[-1] - dataframe_reg.sick.iloc[-2], dataframe_reg.sick.iloc[-2] - dataframe_reg.sick.iloc[-3])
    cured_daily = dataframe_reg.cured.iloc[-1] - dataframe_reg.cured.iloc[-2]
    dead_daily = dataframe_reg.dead.iloc[-1] - dataframe_reg.dead.iloc[-2]
    tested_daily = dataframe_reg.tested.iloc[-1] - dataframe_reg.tested.iloc[-2]

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
    dcc.Graph(
        id='covid19_sick_overall',
        figure=viz.sick_people(viz.dataframe_reg.date, viz.dataframe_reg.sick, 'Aggrnyl')
    )
    ]
)

if __name__ == '__main__':
    app.run_server()
