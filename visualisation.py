import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Visualisation():
	def draw_historical_plotly(self, region, dataset):
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
		
		fig.update_layout(title='Historical plot for: '+region,
			xaxis_title='Date',
			yaxis_title='Number',
			template='plotly_dark')
		fig.update_xaxes(
			tickangle = 55)

		#fig.show()
		return fig
		
	def draw_historical_world_plotly(self, global_data):
		global_data = global_data
		
		fig = go.Figure()
		
		fig.add_trace(go.Scatter(x=global_data.index, y=global_data['total_cases'], mode='lines', name='Cases'))
		fig.add_trace(go.Scatter(x=global_data.index, y=global_data['total_deaths'], mode='lines', name='Deaths'))
		fig.add_trace(go.Scatter(x=global_data.index, y=global_data['total_recovered'], mode='lines', name='Recovered'))
		
		fig.update_layout(title='Historical world plot',
			xaxis_title='Date',
			yaxis_title='Number',
			template='plotly_dark')
		fig.update_xaxes(
			tickangle = 55)

		return fig
		
	def draw_world_map(self, world_map_data, crd_choice):
		if crd_choice == 'deaths':
			title = 'Global deaths map'
		elif crd_choice == 'recovered':
			title = 'Global recovered map'
		else:
			title = 'Global cases map'
		fig = go.Figure(data=go.Choropleth(
			locations=world_map_data['Country code'],
			z=world_map_data['Number'], 
			#hover_name=world_map_data['Country/Region'],
			#color_continuous_scale=px.colors.sequential.Plasma,
			colorscale='Plasma',
			colorbar=dict(tickfont=dict(color='white')),
			hovertext=world_map_data['Country/Region'],
			#template ='plotly_dark')
			), layout = go.Layout(geo=dict(bgcolor= 'rgba(0,0,0,0)'),
				paper_bgcolor='#111111'))
		fig.update_layout(title=title, width=1200, height=800, font=dict(
        #size=18,
        color="white"
    ))
				
		return fig
		
	def draw_subplots(self, daily_bar_data, daily_table_data, crd_choice):
		x = daily_bar_data
		values = daily_table_data
		fig = make_subplots(column_widths=[0.8, 0.2], rows=1, cols=2, specs=[[{"type": "bar"},{"type":"table"}]])
		if crd_choice == 'deaths':
			y = x.iloc[4]
			title = 'Daily deaths'
		elif crd_choice == 'recovered':
			y = x.iloc[5]
			title = 'Daily recovered'
		else:
			y = x.iloc[3]
			title = 'Daily cases'
		fig.add_trace(go.Bar(x=x.iloc[3].index, y=y, marker_color='#FFFF00', name=''), row=1, col=1)
		fig.add_trace(go.Table(cells=dict(height=60, align=['center'],
				values=[['Yesterday\'s cases', 'Yesterday\'s deaths', 'Yesterday\'s recovered'], values])), row=1, col=2)
		fig.update_layout(title=title,
			xaxis_title='Date',
			yaxis_title='Number',
			template='plotly_dark')
		fig.layout['template']['data']['table'][0]['header']['fill']['color']='rgba(0,0,0,0)'
		fig.update_xaxes(
			tickangle = 55)
		
		return fig
		
	def draw_global_subplots(self, global_data, crd_choice):
		x = global_data
		values = global_data.iloc[:, [1,3,5]]
		fig = make_subplots(column_widths=[0.8, 0.2], rows=1, cols=2, specs=[[{"type": "bar"},{"type":"table"}]])
		if crd_choice == 'deaths':
			y = global_data['new_deaths']
			title = 'Daily global deaths'
		elif crd_choice == 'recovered':
			y = global_data['new_recovered']
			title = 'Daily global recovered'
		else:
			y = global_data['new_cases']
			title = 'Daily global cases'
		fig.add_trace(go.Bar(x=global_data.index, y=y, marker_color='#FFFF00', name=''), row=1, col=1)
		fig.add_trace(go.Table(cells=dict(height=60, align=['center'],
				values=[['Yesterday\'s cases', 'Yesterday\'s deaths', 'Yesterday\'s recovered'],
						[values['new_cases'][-1], values['new_deaths'][-1], values['new_recovered'][-1]]])), row=1, col=2)
		fig.update_layout(title=title,
			xaxis_title='Date',
			yaxis_title='Number',
			template='plotly_dark')
		fig.layout['template']['data']['table'][0]['header']['fill']['color']='rgba(0,0,0,0)'
		fig.update_xaxes(
			tickangle = 55)
		
		return fig
		
	
