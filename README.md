# Covid19 Dashboard (cases in Ukraine)
What this app does?: 
*scrapes the data from the Ministry of Healthcare and Cabinet of Ministers websites (requests)
*records entries to the Google Cloud MySQL DB (SQL)
*transforms the data from the DB into a Pandas Dataframe
*performs ratio calculations 
*visualizes the data with Dash (Plotly, Flask).

Feel free to try it out at: https://covid19-in-ukraine-test.herokuapp.com/

![Covid 19 visualization](https://i.ibb.co/1ntkNJV/Screenshot-from-2020-06-19-10-33-56.png)

While howering over the image, the exact stats and date for a given day are displayed.

![Visualization upon hovering](https://i.ibb.co/N9NNy2P/Screenshot-from-2020-06-19-10-42-27.png)

![Covid 19 visuzalization fatality ratio](https://i.ibb.co/0B0Sv3P/Screenshot-from-2020-06-19-10-36-21.png)


### Event log
7/05/2020 - UA Gov Adopted a law on mass-testing

### Observations

**"Recovery Plateaus" during weekends**

While the infection and fatality rates are pretty consistent throught the whole period, the "Recovery" rate is regurarely stagnating during weekends (+/- 1 day). 

This could be caused by:
- more people addressing hospitals during weekends (increase in number of confirmed cases?)
- medical workers report less people recovering (decrease in recovery numbers?)
- more people die during weekends (increase in number of deaths?)

