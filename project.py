import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
from array import *
from numpy import NAN
from streamlit_vega_lite import vega_lite_component, altair_component

## task 3 ##
@st.cache
def map_state():
	ansi = pd.read_csv('https://www2.census.gov/geo/docs/reference/state.txt', sep='|')
	ansi.columns = ['id', 'abbr', 'State', 'statens']
	ansi = ansi[['id', 'State']]
	mapping = dict(ansi[['State', 'id']].values)
	return mapping


@st.cache
def load_state6878():
	dat_state = pd.read_csv('mortality/state_level/Mort6878.tsv', sep='\t', low_memory = False)
	dat_state['state_id'] = dat_state.State.map(map_state())
	return dat_state
@st.cache
def load_state7998():
	dat_state = pd.read_csv('mortality/state_level/Mort7998.tsv', sep='\t', low_memory = False)
	dat_state['state_id'] = dat_state.State.map(map_state())
	return dat_state

@st.cache
def load_state9916():
	dat_state = pd.read_csv('mortality/state_level/Mort9916.tsv', sep='\t', low_memory = False)
	dat_state['state_id'] = dat_state.State.map(map_state())
	return dat_state

@st.cache
def load_county6878():
	dat_county = pd.read_csv('mortality/county_level/Mort6878_county.tsv', sep='\t', low_memory = False)
	dat_county["County"] = dat_county.County.str.replace(' County', '')
	return dat_county

@st.cache
def load_county7988():
	dat_county = pd.read_csv('mortality/county_level/Mort7988_county.tsv', sep='\t', low_memory = False)
	dat_county["County"] = dat_county.County.str.replace(' County', '')
	return dat_county	


#select year
year_min = 1968
year_max = 2016
year = st.slider('Year', min_value = year_min, max_value = year_max, step = 1)


if year <= 1978:
  dat_state = load_state6878()
  dat_county = load_county6878()
elif year > 1978 and year <= 1988:
  dat_state = load_state7998()
  dat_county = load_county7988()
elif year > 1988 and year <= 1998:
  dat_state = load_state7998()
  dat_county = NAN  
else:
  dat_state = load_state9916()
  dat_county = NAN  

# select sex
gender = st.radio("Sex", tuple(dat_state["Gender"].unique()))

# select race
race = st.radio("Race", tuple(dat_state["Race"].unique()))

# select ICD group according to state level data
ICD = st.selectbox('ICD Group', dat_state["ICD Group"].unique())

age = st.selectbox('Age Group', dat_state["Age Group"].unique())


def prep_data(dat, year, race, gender, age, ICD):
  dat = dat[dat['Year'] == year]
  dat = dat[dat['Race'] == (race)]
  dat = dat[dat['Gender'] == (gender)]
  dat = dat[dat['Age Group'] == (age)]
  dat = dat[dat['ICD Group'] == (ICD)]
  return dat

state_subset = prep_data(dat_state, year, race, gender, age, ICD)
if len(state_subset) == 0:
	st.write("No data avaiable for given subset.")
else:
	if st.checkbox("Show Raw Data"):
		st.write(state_subset)
	from vega_datasets import data
	source = alt.topo_feature(data.us_10m.url, 'states')
	def make_state_rate():
		width = 800
		height  = 480
		project = 'albersUsa'
		rate_scale = alt.Scale(domain=[state_subset['Mortality Rate'].min(), state_subset['Mortality Rate'].max()])
		rate_color = alt.Color(field="Mortality Rate", type="quantitative", scale=rate_scale)
		selector = alt.selection_single()
		background_us = alt.Chart(source
		).mark_geoshape(
    		fill='lightgray',
    		stroke='white'
		).properties(
    		width=width,
    		height=height
		).project(project)


		state_rate = alt.Chart(source).mark_geoshape().encode(
    		color=rate_color,
    		tooltip=["Mortality Rate:Q", "State:N"]
    	).transform_filter(
    		selector
		).properties(
    		title=f'Mortality Rate U.S. {year}',
    		width = width,
    		height = height
		).transform_lookup(
      		lookup="id",
      		from_=alt.LookupData(state_subset, "state_id", ["Mortality Rate", 'State']),
    	).project(project).add_selection(selector)
		return (background_us+state_rate)

	state_chart = make_state_rate()
	event_dict = altair_component(state_chart)
	st.write(event_dict)
	st.altair_chart(state_chart, use_container_width=True)
	if "_vgsid_" in event_dict:
		sl = event_dict["_vgsid_"][0]
		st.write(state_subset.iloc[[sl]])


