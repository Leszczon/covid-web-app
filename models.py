import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.integrate import odeint
from lmfit import minimize, Parameters, Parameter, report_fit
from IPython.display import display

class Models():
	def sir(y, t, N, beta, gamma):
		S, I, R = y
		dSdt = -beta * S * I / N
		dIdt = beta * S * I / N - gamma * I
		dRdt = gamma * I
		return dSdt, dIdt, dRdt

	def sird(y, t, N, beta, gamma, mi):
		S, I, R, D = y
		dSdt = -beta * S * I / N
		dIdt = beta * S * I / N - gamma * I - mi * I
		dRdt = gamma * I
		dDdt = mi * I
		return dSdt, dIdt, dRdt, dDdt

	def seird(y, t, N, beta, gamma, mi, sigma):
		S, E, I, R, D = y
		dSdt = -beta * S * I / N
		dEdt = beta * S * I / N - sigma * E
		dIdt = sigma * E - gamma * I - mi * I
		dRdt = gamma * I
		dDdt = mi * I
		return dSdt, dEdt, dIdt, dRdt, dDdt
	
	def prepare_model_data(model, days, region, dataset):
		t = np.arange(0, days, 1)
		cases = dataset[0].groupby(by=["Country/Region"], dropna=False).sum()
		deaths = dataset[1].groupby(by=["Country/Region"], dropna=False).sum()
		recovered = dataset[2].groupby(by=["Country/Region"], dropna=False).sum()
		cases = cases.reset_index()
		deaths = deaths.reset_index()
		recovered = recovered.reset_index()
		eu_daily = dataset[3]
		
		cols = cases[cases['Country/Region']==region].iloc[:, -days:].columns
		
		d1 = np.array(deaths[deaths['Country/Region']==region].iloc[:, -days:])
		r1 = np.array(recovered[recovered['Country/Region']==region].iloc[:, -days:])
		i1 = np.array(cases[cases['Country/Region']==region].iloc[:, -days:]) - d1 - r1
		
		R0 = np.array(recovered[recovered['Country/Region']==region].iloc[:, -days])[0]
		D0 = np.array(deaths[deaths['Country/Region']==region].iloc[:, -days])[0]
		I0 = np.array(cases[cases['Country/Region']==region].iloc[:, -days])[0] - R0 - D0
		E0 = 10*I0 #only seird, approximating exposed count as 10 times the infected number 
		
		region_pop = region.replace(' ','_')
		if 'US' in region:
			region_pop = 'United_States_of_America'
		
		N = eu_daily[eu_daily['countriesAndTerritories']==region_pop]['popData2019'].mean()
		
		if model == 'sir':
			data = np.array([i1[0], r1[0]])
			S0 = N - I0 - R0 - D0
			y = S0, I0, R0
		elif model == 'sird':
			data = np.array([i1[0], r1[0], d1[0]])
			S0 = N - I0 - R0 - D0
			y = S0, I0, R0, D0
		elif model == 'seird':
			data = np.array([i1[0], r1[0], d1[0]])
			S0 = N - I0 - R0 - D0 - E0
			y = S0, E0, I0, R0, D0
			
		return y, t, N, data
		
	def error(params, model_data, model):
		y, t, N, data = model_data
		
		if model == 'sir':
			beta, gamma = params['beta'].value, params['gamma'].value
			solution = odeint(Models.sir, y, t, args=(N, beta, gamma))
			return (solution[:, 1:3] - data.T[:]).ravel()
		elif model == 'sird':
			beta, gamma, mi = params['beta'].value, params['gamma'].value, params['mi'].value
			solution = odeint(Models.sird, y, t, args=(N, beta, gamma, mi))
			return (solution[:, 1:4] - data.T[:]).ravel()
		elif model == 'seird':
			beta, gamma, mi, sigma = params['beta'].value, params['gamma'].value, params['mi'].value, params['sigma'].value
			solution = odeint(Models.seird, y, t, args=(N, beta, gamma, mi, sigma))
			return (solution[:, 2:5] - data.T[:]).ravel()
			
	def get_values(r_params, model, model_data, zeit):
		if zeit == 'past':
			y, t, N, data = model_data
		elif zeit == 'future':
			y, t, N = model_data
		if model == 'sir':
			beta, gamma = r_params['beta'].value, r_params['gamma'].value
			solution = odeint(Models.sir, y, t, args=(N, beta, gamma))
			S1, I1, R1 = solution.T
			return I1, R1
		elif model == 'sird':
			beta, gamma, mi = r_params['beta'].value, r_params['gamma'].value, r_params['mi'].value
			solution = odeint(Models.sird, y, t, args=(N, beta, gamma, mi))
			S1, I1, R1, D1 = solution.T
			return I1, R1, D1
		elif model == 'seird':
			beta, gamma, mi, sigma = r_params['beta'].value, r_params['gamma'].value, r_params['mi'].value, r_params['sigma'].value
			solution = odeint(Models.seird, y, t, args=(N, beta, gamma, mi, sigma))
			S1, E1, I1, R1, D1 = solution.T
			return I1, R1, D1
					
	def prepare_future_model_data(model, future_days, region, dataset):
		t = np.arange(0, future_days, 1)
		
		cases = dataset[0].groupby(by=["Country/Region"], dropna=False).sum()
		deaths = dataset[1].groupby(by=["Country/Region"], dropna=False).sum()
		recovered = dataset[2].groupby(by=["Country/Region"], dropna=False).sum()
		cases = cases.reset_index()
		deaths = deaths.reset_index()
		recovered = recovered.reset_index()
		eu_daily = dataset[3]
		
		R0 = np.array(recovered[recovered['Country/Region']==region].iloc[:, -1])[0]
		D0 = np.array(deaths[deaths['Country/Region']==region].iloc[:, -1])[0]
		I0 = np.array(cases[cases['Country/Region']==region].iloc[:, -1])[0] - R0 - D0
		E0 = 10*I0 #only seird, approximating exposed count as 10 times the infected number 
		
		region_pop = region.replace(' ','_')
		if 'US' in region:
			region_pop = 'United_States_of_America'
		
		N = eu_daily[eu_daily['countriesAndTerritories']==region_pop]['popData2019'].mean()
		
		if model == 'sir':
			S0 = N - I0 - R0 - D0
			y = S0, I0, R0
		elif model == 'sird':
			S0 = N - I0 - R0 - D0
			y = S0, I0, R0, D0
		elif model == 'seird':
			S0 = N - I0 - R0 - D0 - E0
			y = S0, E0, I0, R0, D0
			
		return y, t, N
		
	def draw_historical_and_prediction(self, region, new_values, model, dataset, ffd):
		cases = dataset[0].groupby(by=["Country/Region"], dropna=False).sum()
		deaths = dataset[1].groupby(by=["Country/Region"], dropna=False).sum()
		recovered = dataset[2].groupby(by=["Country/Region"], dropna=False).sum()
		cases = cases.reset_index()
		deaths = deaths.reset_index()
		recovered = recovered.reset_index()
		region_data = pd.DataFrame()
		region_data = region_data.append(cases[cases['Country/Region'] == region])
		region_data = region_data.append(deaths[deaths['Country/Region'] == region])
		region_data = region_data.append(recovered[recovered['Country/Region'] == region])
		region_data.reset_index(inplace=True)
		region_data.drop('index', axis = 1, inplace=True)
		region_data["Data type"] = ['Cases', 'Deaths', 'Recovered']
		region_data.set_index("Data type", inplace=True)
		
		fig = go.Figure()
		
		tmp = region_data[region_data.index == region_data.index[0]]
		fig.add_trace(go.Scatter(x=tmp.columns[4:], y=tmp[tmp.columns[4:]].loc['Cases'], mode='lines', name='Cases'))
		tmp = region_data[region_data.index == region_data.index[1]]
		fig.add_trace(go.Scatter(x=tmp.columns[4:], y=tmp[tmp.columns[4:]].loc['Deaths'], mode='lines', name='Deaths'))
		tmp = region_data[region_data.index == region_data.index[2]]
		fig.add_trace(go.Scatter(x=tmp.columns[4:], y=tmp[tmp.columns[4:]].loc['Recovered'], mode='lines', name='Recovered'))
		
		x = ffd
		
		if model == 'sir':
			I, R = new_values
			D0 = np.array(deaths[deaths['Country/Region']==region].iloc[:, -1])[0]
			I = I + R + D0
			fig.add_trace(go.Scatter(x=x, y=I, mode='lines', name='Predicted infected'))
			fig.add_trace(go.Scatter(x=x, y=R, mode='lines', name='Predicted recovered'))
		else:
			I, R, D = new_values
			I = I + R + D
			fig.add_trace(go.Scatter(x=x, y=I, mode='lines', name='Predicted infected'))
			fig.add_trace(go.Scatter(x=x, y=D, mode='lines', name='Predicted deaths'))
			fig.add_trace(go.Scatter(x=x, y=R, mode='lines', name='Predicted recovered'))   
		
		fig.update_layout(title='Historical plot and predictions for: '+region,
			xaxis_title='Date',
			yaxis_title='Number',
			template='plotly_dark')
		fig.update_xaxes(
			tickangle = 55)

		return fig
		
	def simulate_model(self, model, days, region, dataset, future_days):
		beta = 0.5
		gamma = 0.5
		mi = 0.5
		sigma = 0.5
		params = Parameters()
		if model == 'sir':
			params.add('beta', value=beta, min=0, max=10)
			params.add('gamma', value=gamma, min=0, max=10)
		elif model == 'sird':
			params.add('beta', value=beta, min=0, max=10)
			params.add('gamma', value=gamma, min=0, max=10)
			params.add('mi', value=mi, min=0, max=10)
		elif model == 'seird':
			params.add('beta', value=beta, min=0, max=10)
			params.add('gamma', value=gamma, min=0, max=10)
			params.add('mi', value=mi, min=0, max=10)
			params.add('sigma', value=sigma, min=0, max=10)
		model_data = Models.prepare_model_data(model, days, region, dataset)
		result = minimize(Models.error, params, args=(model_data, model), method='leastsq', nan_policy='omit')
		r_params = result.params
		new_model_data = Models.prepare_future_model_data(model, future_days, region, dataset)
		new_values = Models.get_values(r_params, model, new_model_data, 'future')
		
		return new_values
