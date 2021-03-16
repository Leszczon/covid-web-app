import requests
import pandas as pd
import datetime
from datetime import date, timedelta

class Data():
	def download_data(self):
		url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
		r = requests.get(url, allow_redirects=True)
		open('data/time_series.csv', 'wb').write(r.content)

		url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
		r = requests.get(url, allow_redirects=True)
		open('data/deaths.csv', 'wb').write(r.content)

		url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
		r = requests.get(url, allow_redirects=True)
		open('data/recovered.csv', 'wb').write(r.content)

		url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
		r = requests.get(url, allow_redirects=True)
		open('data/eu_daily_report.csv', 'wb').write(r.content)
		
	def prepare_global_data(self, dataset):
		tmp = dataset[0].copy()
		tmp.drop(['Province/State', 'Lat', 'Long', 'Country/Region'], axis=1, inplace=True)
		global_cases = tmp.sum()

		tmp = dataset[1].copy()
		tmp.drop(['Province/State', 'Lat', 'Long', 'Country/Region'], axis=1, inplace=True)
		global_deaths = tmp.sum()

		tmp = dataset[2].copy()
		tmp.drop(['Province/State', 'Lat', 'Long', 'Country/Region'], axis=1, inplace=True)
		global_recovered = tmp.sum()
		
		global_data = pd.DataFrame (global_cases, columns = ['total_cases'])
		global_data.index.names = ['date']
		global_data['new_cases'] = 0
		global_data['total_deaths'] = global_deaths
		global_data['new_deaths'] = 0
		global_data['total_recovered'] = global_recovered
		global_data['new_recovered'] = 0
		
		for i in range(len(global_data['total_cases'])):
			if i == 0:
				global_data['new_cases'][i] = global_data['total_cases'][i]
				global_data['new_deaths'][i] = global_data['total_deaths'][i]
				global_data['new_recovered'][i] = global_data['total_recovered'][i]
			else:
				global_data['new_cases'][i] = global_data['total_cases'][i]-global_data['total_cases'][i-1]
				global_data['new_deaths'][i] = global_data['total_deaths'][i]-global_data['total_deaths'][i-1]
				global_data['new_recovered'][i] = global_data['total_recovered'][i]-global_data['total_recovered'][i-1]
		global_data[global_data < 0] = 0
				
		return global_data
		
	def prepare_daily_bar_data(self, region, dataset):
		region_data = pd.DataFrame()
		cases = dataset[0].groupby(by=["Country/Region"], dropna=False).sum()
		deaths = dataset[1].groupby(by=["Country/Region"], dropna=False).sum()
		recovered = dataset[2].groupby(by=["Country/Region"], dropna=False).sum()
		cases = cases.reset_index()
		deaths = deaths.reset_index()
		recovered = recovered.reset_index()
		region_data = region_data.append(cases[cases['Country/Region'] == region])
		region_data = region_data.append(deaths[deaths['Country/Region'] == region])
		region_data = region_data.append(recovered[recovered['Country/Region'] == region])
		region_data.reset_index(inplace=True)
		region_data.drop('index', axis = 1, inplace=True)
		region_data["Data type"] = ['Cases', 'Deaths', 'Recovered']
		region_data.set_index("Data type", inplace=True)

		x = region_data.iloc[:, 4:]
		for j in range(0, 3): 
			testo = []
			for i in range(0, len(x.iloc[j, :])):
				if i == 0:
					testo.append(x.iloc[j, i])
				else:
					testo.append(x.iloc[j, i] - x.iloc[j, i-1])
			if j==0:
				x.loc['New_cases'] = testo
			if j==1:
				x.loc['New_deaths'] = testo
			if j==2:
				x.loc['New_recovered'] = testo
				
		x[x < 0] = 0
		
		return x
    
	def prepare_daily_table_data(self, region, dataset):
		values = []
		cases = dataset[0].groupby(by=["Country/Region"], dropna=False).sum()
		deaths = dataset[1].groupby(by=["Country/Region"], dropna=False).sum()
		recovered = dataset[2].groupby(by=["Country/Region"], dropna=False).sum()
		cases = cases.reset_index()
		deaths = deaths.reset_index()
		recovered = recovered.reset_index()
		values.append(cases[cases['Country/Region']==region].iloc[:, -1] - cases[cases['Country/Region']==region].iloc[:, -2])
		values.append(deaths[deaths['Country/Region']==region].iloc[:, -1] - deaths[deaths['Country/Region']==region].iloc[:, -2])
		values.append(recovered[recovered['Country/Region']==region].iloc[:, -1] - recovered[recovered['Country/Region']==region].iloc[:, -2])
		
		return values
		
	def get_options(self, countries):
		dict_list = []
		for i in countries:
			dict_list.append({'label': i, 'value': i})
			
		return dict_list
		
	def generate_dates_dict(self, cases):
		dict_list = []
		for i in range(1, len(cases.iloc[:, 4:].columns)):
			dict_list.append({'label': i, 'value': i})
			
		return dict_list
		
	def generate_ffd(self, future_days, start_date):
		future_forecast_dates = []
		for i in range(future_days):
			temp_date = (start_date - timedelta(1) + datetime.timedelta(days=i)).strftime('%#m/%#d/%y')
			future_forecast_dates.append(temp_date)
			
		return future_forecast_dates
		
	def prepare_world_map_data(self, dataset, crd_choice):
		#między 0 a 2 days 2
		yesterday = date.today() - timedelta(days=1)
		s = yesterday.strftime('%#m/%#d/%y')
		
		cases = dataset[0]
		cases_cpy = cases.copy()
		cases_cpy.loc[cases_cpy.loc[cases_cpy['Country/Region'] == 'US'].index[0], 'Country/Region'] = 'United_States_of_America'
		cases_cpy['Country/Region'] = cases_cpy['Country/Region'].str.replace(' ','_')
		
		deaths = dataset[1]
		deaths_cpy = deaths.copy()
		deaths_cpy.loc[deaths_cpy.loc[deaths_cpy['Country/Region'] == 'US'].index[0], 'Country/Region'] = 'United_States_of_America'
		deaths_cpy['Country/Region'] = deaths_cpy['Country/Region'].str.replace(' ','_')
		
		recovered = dataset[2]
		recovered_cpy = recovered.copy()
		recovered_cpy.loc[recovered_cpy.loc[recovered_cpy['Country/Region'] == 'US'].index[0], 'Country/Region'] = 'United_States_of_America'
		recovered_cpy['Country/Region'] = recovered_cpy['Country/Region'].str.replace(' ','_')

		eu_daily = dataset[3]
		temp = eu_daily.copy()
		#temp.drop(['dateRep', 'day', 'month', 'year', 'deaths', 'geoId', 'popData2019', 'continentExp', 'Cumulative_number_for_14_days_of_COVID-19_cases_per_100000'], axis=1, inplace=True)
		temp = temp[['cases', 'countriesAndTerritories', 'countryterritoryCode']]
		temp.columns = ['value', 'Country/Region', 'countryterritoryCode']
		new = temp.groupby('Country/Region')
		temp.head()
		temp1 = new.first()['countryterritoryCode']
		test = pd.DataFrame()
		test['country_name'] = temp1

		if crd_choice == 'deaths':
			result = pd.merge(deaths_cpy, test, on='Country/Region')
			result = result.rename(columns={s: 'Number', 'country_name': 'Country code'})
			aggregation_functions = {'Number': 'sum'}
			deaths_0 = result.groupby(['Country code', 'Country/Region']).aggregate(aggregation_functions)
			deaths_0.reset_index(drop=False, inplace=True)
			deaths_0['Country/Region'] = deaths_0['Country/Region'].str.replace('_',' ')
			return deaths_0
		elif crd_choice == 'recovered':
			result = pd.merge(recovered_cpy, test, on='Country/Region')
			result = result.rename(columns={s: 'Number', 'country_name': 'Country code'})
			aggregation_functions = {'Number': 'sum'}
			recovered_0 = result.groupby(['Country code', 'Country/Region']).aggregate(aggregation_functions)
			recovered_0.reset_index(drop=False, inplace=True)
			recovered_0['Country/Region'] = recovered_0['Country/Region'].str.replace('_',' ')
			return recovered_0
		else:
			print(cases_cpy)
			print(test)
			result = pd.merge(cases_cpy, test, on='Country/Region')
			result = result.rename(columns={s: 'Number', 'country_name': 'Country code'})
			aggregation_functions = {'Number': 'sum'}
			cases_0 = result.groupby(['Country code', 'Country/Region']).aggregate(aggregation_functions)
			cases_0.reset_index(drop=False, inplace=True)
			cases_0['Country/Region'] = cases_0['Country/Region'].str.replace('_',' ')
			return cases_0
