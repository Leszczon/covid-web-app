#import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
#from datetime import date, timedelta
from IPython.display import display

import plotly.express as px
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from data import Data
from visualisation import Visualisation
from models import Models



data = Data()
vis = Visualisation()
models = Models()

data.download_data()

cases = pd.read_csv("data/time_series.csv")
deaths = pd.read_csv("data/deaths.csv")
recovered = pd.read_csv("data/recovered.csv")
eu_daily = pd.read_csv("data/eu_daily_report.csv")
dataset = [cases, deaths, recovered, eu_daily]

countries = cases['Country/Region'].unique()
countries_pred = []
for country in countries:
	country = country.replace(' ','_')
	if 'US' in country:
		country = 'United_States_of_America'
	if country in eu_daily['countriesAndTerritories'].unique():
		country = country.replace('_', ' ')
		if 'United States of America' in country:
			country = 'US'
		countries_pred.append(country)

days = 14
future_days = 14
start = str(datetime.datetime.today().strftime ('%m/%d/%y'))
start_date = datetime.datetime.strptime(start, '%m/%d/%y')
future_forecast_dates = data.generate_ffd(future_days, start_date)
model = 'sir'
region = countries[0]
start_values = models.simulate_model(model, days, region, dataset, future_days)

#layout
app = dash.Dash(__name__)
app.layout = html.Div(children=[
	html.Div(className='row',  
		children=[
			html.Div(className='four columns div-user-controls', children=[
				html.H2('Dash - COVID-19 Data Visualisation'),
				html.P('''Analysing COVID-19 data with Plotly - Dash'''),
				html.P('''Choose any of the buttons below'''),
				html.Button('Local data', id='local_button', n_clicks=0),
				html.Button('Global data', id='global_button', n_clicks=0),
				html.Button('World map', id='global_map_button', n_clicks=0),
				html.Button('Predictions', id='predictions_button', n_clicks=0),
				html.Button('About', id='about_button', n_clicks=0)
				]),
			html.Div(id='right_side', className='eight columns div-for-charts bg-grey', children=[
				dcc.Dropdown(id='country_choice',
                           options=data.get_options(countries),
                           value=countries[0],
                           style={'backgroundColor': '#1E1E1E'},
                           className='countrySelector'),
				dcc.Graph(id='country_graph', figure=vis.draw_historical_plotly(countries[0], dataset)),
				dcc.Graph(id='daily_local_bar', figure=vis.draw_subplots(data.prepare_daily_bar_data(countries[0], dataset), data.prepare_daily_table_data(countries[0], dataset), 'cases')),
				dcc.Dropdown(id='country_choice_pred',
					options=data.get_options(countries),
					value=countries[0],
					style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Dropdown(id='model_choice',
					options=[{'label':'SIR','value':'sir'}, {'label':'SIRD','value':'sird'}, {'label':'SEIRD','value':'seird'}],
					value='sir',
					style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Dropdown(id='past_days_choice',
					options=data.generate_dates_dict(cases),
					value=days,
					style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Dropdown(id='future_days_choice',
					options=data.generate_dates_dict(cases),
					value=14,
					style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Dropdown(id='type_choice', style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Dropdown(id='type_choice_global', style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Dropdown(id='type_choice_map', style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Graph(id='world_map', style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Graph(id='daily_global_bar', style={'backgroundColor': '#1E1E1E', 'display': 'none'}),
				dcc.Graph(id='predictions_graph', figure=models.draw_historical_and_prediction(region, start_values, model, dataset, future_forecast_dates))])
		])
	])	

#callbacks	
@app.callback(Output('right_side', 'children'),
              [Input('global_map_button', 'n_clicks'),
              Input('local_button', 'n_clicks'),
              Input('global_button', 'n_clicks'),
              Input('predictions_button', 'n_clicks'),
              Input('about_button', 'n_clicks')])
def change_right_side(btn1, btn2, btn3, btn4, btn5):
	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
	if 'global_map_button' in changed_id:
		return [dcc.Dropdown(id='type_choice_map', options=[{'label':'Cases','value':'cases'}, {'label':'Deaths','value':'deaths'}, {'label':'Recovered','value':'recovered'}],
				value='cases', style={'backgroundColor': '#1E1E1E'}),
				dcc.Graph(id='world_map', figure=vis.draw_world_map(data.prepare_world_map_data(dataset, 'cases'), 'cases'))]
	elif 'global_button' in changed_id:
		return [dcc.Graph(id='global_graph', figure=vis.draw_historical_world_plotly(data.prepare_global_data(dataset))),
				dcc.Dropdown(id='type_choice_global', options=[{'label':'Cases','value':'cases'}, {'label':'Deaths','value':'deaths'}, {'label':'Recovered','value':'recovered'}],
				value='cases', style={'backgroundColor': '#1E1E1E'}),
				dcc.Graph(id='daily_global_bar',  figure=vis.draw_global_subplots(data.prepare_global_data(dataset), 'cases'))]
	elif 'predictions_button' in changed_id:
		return [html.Br(),
				html.P('Country:'),
				dcc.Dropdown(id='country_choice_pred',
					options=data.get_options(countries_pred),
					value=countries_pred[0],
					style={'backgroundColor': '#1E1E1E'}),
				html.Br(),
				html.P('Model:'),
				dcc.Dropdown(id='model_choice',
					options=[{'label':'SIR','value':'sir'}, {'label':'SIRD','value':'sird'}, {'label':'SEIRD','value':'seird'}],
					value='sir',
					style={'backgroundColor': '#1E1E1E'}),
				html.Br(),
				html.P('Past days:'),
				dcc.Dropdown(id='past_days_choice',
					options=data.generate_dates_dict(cases),
					value=days,
					style={'backgroundColor': '#1E1E1E'}),
				html.Br(),
				html.P('Future days:'),
				dcc.Dropdown(id='future_days_choice',
					options=data.generate_dates_dict(cases),
					value=14,
					style={'backgroundColor': '#1E1E1E'}),
		dcc.Graph(id='predictions_graph', figure=models.draw_historical_and_prediction(region, start_values, model, dataset, future_forecast_dates))]
	elif 'about_button' in changed_id:
		return html.H2('About info coming soon')
	#elif 'local_button' in changed_id:
	else:
		return [dcc.Dropdown(id='country_choice',
				options=data.get_options(countries),
				value=countries[0],
				style={'backgroundColor': '#1E1E1E'}),
		dcc.Graph(id='country_graph', figure=vis.draw_historical_plotly(countries[0], dataset)),
		dcc.Dropdown(id='type_choice', options=[{'label':'Cases','value':'cases'}, {'label':'Deaths','value':'deaths'}, {'label':'Recovered','value':'recovered'}],
			value='cases', style={'backgroundColor': '#1E1E1E'}),
		dcc.Graph(id='daily_local_bar', figure=vis.draw_subplots(data.prepare_daily_bar_data(countries[0], dataset), data.prepare_daily_table_data(countries[0], dataset), 'cases'))
		]
		
@app.callback(Output('world_map', 'figure'),
              [Input('type_choice_map', 'value')])
def update_timeseries(selected_dropdown_value):
	if isinstance(selected_dropdown_value, list):
		return vis.draw_world_map(data.prepare_world_map_data(dataset, 'cases'), 'cases')
	else:
		return vis.draw_world_map(data.prepare_world_map_data(dataset, selected_dropdown_value), selected_dropdown_value)
		
@app.callback(Output('daily_global_bar', 'figure'),
              [Input('type_choice_global', 'value')])
def update_timeseries(selected_dropdown_value):
	if isinstance(selected_dropdown_value, list):
		return vis.draw_global_subplots(data.prepare_global_data(dataset), 'cases')
	else:
		return vis.draw_global_subplots(data.prepare_global_data(dataset), selected_dropdown_value)
		
@app.callback(Output('country_graph', 'figure'),
              [Input('country_choice', 'value')])
def update_timeseries(selected_dropdown_value):
	if isinstance(selected_dropdown_value, list):
		return vis.draw_historical_plotly(selected_dropdown_value[0], dataset)
	else:
		return vis.draw_historical_plotly(selected_dropdown_value, dataset)
		
@app.callback(Output('predictions_graph', 'figure'),
              [Input('country_choice_pred', 'value'),
              Input('model_choice', 'value'),
              Input('past_days_choice', 'value'),
              Input('future_days_choice', 'value')])
def update_timeseries(dv1, dv2, dv3, dv4):
	if isinstance(dv1, list):
		return models.draw_historical_and_prediction(countries[0], start_values, model, dataset, future_forecast_dates)
	else:
		return models.draw_historical_and_prediction(dv1, models.simulate_model(dv2, dv3, dv1, dataset, dv4), dv2, dataset, data.generate_ffd(dv4, start_date))
		
@app.callback(Output('daily_local_bar', 'figure'),
              [Input('country_choice', 'value'),
              Input('type_choice', 'value')])
def update_timeseries(selected_dropdown_value, dropdown_type):
	if isinstance(selected_dropdown_value, list):
		return vis.draw_subplots(data.prepare_daily_bar_data(countries[0], dataset), data.prepare_daily_table_data(countries[0], dataset), 'cases')
	else:
		return vis.draw_subplots(data.prepare_daily_bar_data(selected_dropdown_value, dataset), data.prepare_daily_table_data(selected_dropdown_value, dataset), dropdown_type)

#def update_crd(btn1, btn2, btn3):
#	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#	if 'c_button' in changed_id:
#		return vis.draw_subplots(data.prepare_daily_bar_data(selected_dropdown_value, dataset), data.prepare_daily_table_data(selected_dropdown_value, dataset), 'cases')
#	elif 'd_button' in changed_id:
#		return vis.draw_subplots(data.prepare_daily_bar_data(selected_dropdown_value, dataset), data.prepare_daily_table_data(selected_dropdown_value, dataset), 'deaths')
#	elif 'r_button' in changed_id:
#		return vis.draw_subplots(data.prepare_daily_bar_data(selected_dropdown_value, dataset), data.prepare_daily_table_data(selected_dropdown_value, dataset), 'recovered')
	
if __name__ == '__main__':
	app.run_server(debug=True)
