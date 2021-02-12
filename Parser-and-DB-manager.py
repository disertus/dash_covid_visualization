import datetime
import re
import time

import mysql.connector
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup, SoupStrainer

start = time.time()
# https://www.worldometers.info/coronavirus/ - table with cases worldwide
# https://coronavirus.jhu.edu/map.html - visualization by John Hopkins

# https://covid19.com.ua/ - daily updated data by the Ministry of Healthcare of Ukraine
# https://moz.gov.ua/article/news/operativna-informacija-pro-poshirennja-koronavirusnoi-infekcii-2019-ncov-
# https://moz.gov.ua/article/news/operativna-informacija-pro-poshirennja-koronavirusnoi-infekcii-2019-ncov-1

# Opens a URL of the webpage, which is going to be parsed
openurl = requests.get("https://covid19.com.ua/").text
soup = BeautifulSoup(openurl, "lxml")

# Opens a URL of the regional statistics webpage
openurl_reg = requests.get(
    "https://moz.gov.ua/article/news/operativna-informacija-pro-poshirennja-koronavirusnoi-infekcii-2019-ncov-1"
).text
soup_reg = BeautifulSoup(openurl_reg, "lxml")


class People:

    # Parse the Ministry of Healthcare website for stats regarding COVID-19
    def parsing():
        # Extracts the numeric values for cases in the form of strings inside a list
        parsed_tags = soup.find_all("div", {"class": "field-value"})
        cases_list = []
        for i in parsed_tags:
            value = i.string
            if value == None:
                continue
            value = re.findall(
                r"\d+", value
            )  # Filters out all non-digit characters in the 'value' string
            value = ["".join(value)]  # Joins multiple values inside the list object, in
            # case '2000' is written as '2' '000'
            cases_list.append(str(value[0]))
        return cases_list

    def parsing_reg(self):
        cases_dict = {}
        parsed_tags_reg_ul = soup_reg.find_all("ul")[2].text
        parsed_tags_reg_p = soup_reg.find_all("div", {"class": "editor"})[0]
        parsed_tags_reg_p = re.sub(
            r"<br/>", "", parsed_tags_reg_p.find_all("p")[2].text
        )

        def parsing(parsed_tags_reg):
            values = re.split(r";", parsed_tags_reg)
            for i in values:
                reg_clean = re.split("—", (re.sub(r"\n", "", i)))
                reg_name = re.sub(r"обл.", "", reg_clean[0]).strip()
                reg_stats = re.findall(r"\d+", i)[0]
                cases_dict.update({reg_name: int(reg_stats)})
            cases_dict["Івано_Франківська"] = cases_dict.pop("Івано-Франківська")
            cases_dict["Київ"] = cases_dict.pop("м. Київ")

        try:
            parsing(parsed_tags_reg_p)
        except:
            parsing(parsed_tags_reg_ul)

        return cases_dict

    # Values representing the stats for each category - tested, sick, cured and dead
    tested = parsing()[0]
    sick = parsing()[1]
    cured = parsing()[2]
    dead = parsing()[3]

    # Print out the result of the parsing - to check if values correspond to those on the website
    def print_out_results(self):
        day = datetime.date.today()
        print(f"\nСтатистика захворюваності станом на {day}:")
        print(
            f"""
            Протестовано: {self.tested}

            Хворих:    \t{self.sick}
            
            Одужало:   \t{self.cured}
            
            Померло:   \t{self.dead} 
        """
        )

        for k, v in self.parsing_reg().items():
            print(f"{k}:   {v}")


# Add the collected values to the SQLite database for storage and collection of stats
class MysqlDatabase:
    # Establish connection with the database
    conn = mysql.connector.connect(
        user="root", password="some password", host="some IP address", database="covid"
    )
    curs = conn.cursor()

    # Create the database and a table inside it
    def db_create(self):
        """Function creating the MySQL database and corresponding tables"""
        try:
            self.curs.execute("CREATE DATABASE covid")
        except:
            print("The database with the specified name already exists")

        try:
            self.curs.execute(
                """CREATE TABLE casualties
                            (tested int not null, sick int not null, 
                            cured int not null, dead int not null, 
                            date unique not null);"""
            )
            print("The specified DB and a table have been created")
        except:
            print("Table with overall statistics ---- ALREADY CREATED")

        try:
            self.curs.execute(
                """CREATE TABLE casualties_reg 
                (`date` date primary key not null, Вінницька int not null, Волинська int not null, 
                Дніпропетровська int not null, Донецька int not null, Житомирська int not null, 
                Закарпатська int not null, Запорізька int not null, Івано_Франківська int not null, 
                Кіровоградська int not null, Київ int not null, Київська int not null, 
                Львівська int not null, Луганська int not null, Миколаївська int not null, 
                Одеська int not null, Полтавська int not null, Рівненська int not null, 
                Сумська int not null, Тернопільська int not null, Харківська int not null, 
                Херсонська int not null, Хмельницька int not null, Чернівецька int not null, 
                Черкаська int not null, Чернігівська int not null);"""
            )
        except:
            print("Table with regional statistics ---- ALREADY CREATED")

    # Insert the latest data entry into the database
    def db_update(self):
        """Function adding new entries to the MySQL database tables 'casualties' and 'casualties_reg'"""
        day = datetime.date.today()
        try:
            self.curs.execute(
                """INSERT INTO casualties VALUES
                (%s, %s, %s, %s, %s);""",
                (
                    casualties.tested,
                    casualties.sick,
                    casualties.cured,
                    casualties.dead,
                    day,
                ),
            )
        except:
            print("Overall statistics -------------- ALREADY UPDATED")

        dic = casualties.parsing_reg()
        try:
            self.curs.execute(
                """INSERT INTO casualties_reg (date, Вінницька, Волинська, Дніпропетровська, 
            Донецька, Житомирська, Закарпатська, Запорізька, Івано_Франківська, Кіровоградська, Київ, Київська, 
            Львівська, Луганська, Миколаївська, Одеська, Полтавська, Рівненська, 
            Сумська, Тернопільська, Харківська, Херсонська, Хмельницька, Чернівецька, 
            Черкаська, Чернігівська) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s);""",
                (
                    day,
                    dic["Вінницька"],
                    dic["Волинська"],
                    dic["Дніпропетровська"],
                    dic["Донецька"],
                    dic["Житомирська"],
                    dic["Закарпатська"],
                    dic["Запорізька"],
                    dic["Івано_Франківська"],
                    dic["Кіровоградська"],
                    dic["Київ"],
                    dic["Київська"],
                    dic["Львівська"],
                    dic["Луганська"],
                    dic["Миколаївська"],
                    dic["Одеська"],
                    dic["Полтавська"],
                    dic["Рівненська"],
                    dic["Сумська"],
                    dic["Тернопільська"],
                    dic["Харківська"],
                    dic["Херсонська"],
                    dic["Хмельницька"],
                    dic["Чернівецька"],
                    dic["Черкаська"],
                    dic["Чернігівська"],
                ),
            )
        except:
            print("Regional statistics ------------- ALREADY UPDATED")


class Visualization:

    # 'r before the path is specified in order to avoid the unicode decoding error
    # sql_connect = sqlite3.connect(r'C:\Users\Roman\Google Диск\Python-Learning\coronavirus-research\covid19.db')

    # Referring directly to a connection established inside the 'SQLite_database' class
    sql_connect = MysqlDatabase.conn

    # Transferring data from the SQLite database into pandas dataframe
    dataframe = pd.read_sql_query("SELECT * FROM casualties;", sql_connect)
    dataframe = dataframe.sort_values(by=["date"])
    dataframe_reg = pd.read_sql_query("SELECT * FROM casualties_reg;", sql_connect)
    dataframe_reg = dataframe_reg.sort_values(by=["date"])

    # Daily stats for each category
    sick_daily = (
        dataframe.sick.iloc[-1] - dataframe.sick.iloc[-2],
        dataframe.sick.iloc[-2] - dataframe.sick.iloc[-3],
    )
    cured_daily = dataframe.cured.iloc[-1] - dataframe.cured.iloc[-2]
    dead_daily = dataframe.dead.iloc[-1] - dataframe.dead.iloc[-2]
    tested_daily = dataframe.tested.iloc[-1] - dataframe.tested.iloc[-2]

    print(
        (
            (dataframe_reg.iloc[-1][1:] - dataframe_reg.iloc[-2][1:])
            / dataframe_reg.iloc[-1][1:]
        )
        * 100
    )

    # Establishing a layout for the charts
    layout = dict(
        title={
            "text": "Number of people infected: +%s today, +%s yesterday"
                    % (sick_daily[0], sick_daily[1]),
            "font": {"size": 20, "color": "#3EC283"},
        },
        paper_bgcolor="#292727",
        plot_bgcolor="#2A2727",
        xaxis={"color": "#3EC283"},
        yaxis={"color": "white"},
        hovermode="x"
    )

    def cured_vs_dead(self):
        """Function visualizing the relation between the number of cured and dead people"""
        data_cured = go.Scatter(
            x=self.dataframe.date[-21:],
            y=self.dataframe.cured[-21:],
            line=dict(color="#9EFF37", width=3),
            fill="tonexty",
            name="Cured",
        )
        data_dead = go.Scatter(
            x=self.dataframe.date[-21:],
            y=self.dataframe.dead[-21:],
            line=dict(color="#DD0000", width=3),
            fill="tozeroy",
            name="Dead",
        )
        figure = go.Figure(data=(data_cured, data_dead), layout=self.layout)
        figure.show()

    def fatality_rate(self):
        """Function visualizing the fatality rate: dead/(sick + cured)*100"""
        data_fatality = go.Scatter(
            x=self.dataframe.date,
            y=(self.dataframe.dead / (self.dataframe.sick + self.dataframe.cured))
            * 100,
            line=dict(color="#FF8700", width=3),
            fill="tonexty",
            name="Cured",
        )
        figure = go.Figure(data=data_fatality, layout=self.layout)
        figure.show()

    def sick_people(self, axis_x, axis_y, color_scale):
        """Function visualizing the data packed into the dataframe created out of MySQL data"""

        self.dataframe_reg.set_index("date")
        data = go.Bar(
            x=axis_x,
            y=axis_y.tolist(),
            text="Infected",
            marker={"color": axis_y, "colorscale": color_scale},
        )
        figure_sick_reg = go.Figure(data=data, layout=self.layout)
        figure_sick_reg.show()


# Print out the results to check them in terminal
casualties = People()
casualties.parsing_reg()
casualties.print_out_results()


# Add new entries to the SQL database
sql_db = MysqlDatabase()
sql_db.db_create()
sql_db.db_update()
sql_db.conn.commit()
sql_db.conn.close()

# # Show graph with subplots
# viz = Visualization()
# viz.sick_people(viz.dataframe.date, viz.dataframe.sick, 'Aggrnyl')
# viz.sick_people(viz.dataframe_reg.keys()[1:], viz.dataframe_reg.iloc[-1][1:], 'Aggrnyl')
# viz.cured_vs_dead()
# viz.letality_rate()

finish = time.time()

print("Execution time: ", finish - start)
