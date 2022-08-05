"""
Created by: Tara McBrode
Data: California Fire Incidents
Date: due 08/04/2022
Description: In this program I will analyze California Fire incidents to generate charts showing these fires by county
over time.
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import pydeck as pdk
import numpy as np


def get_data():
    return pd.read_csv('California_Fire_Incidents.csv')


def filter_data(sel_counties, minAcres, sel_year):
    df = get_data()
    df.loc[df['Counties'].isin(sel_counties)]
    df.loc[df['AcresBurned'] < minAcres]
    df.loc[df['ArchiveYear'].isin(sel_year)]

    return df


def all_counties():
    df = get_data()
    lst = []
    for ind, row in df.iterrows():
        if row['Counties'] not in lst:
            lst.append(row['Counties'])

    return lst


def all_acres():
    df = get_data()
    lst = []
    for ind, row in df.iterrows():
        if row['AcresBurned'] not in lst:
            lst.append(row['AcresBurned'])

    return lst


def count_counties(counties, df):
    return [df.loc[df['Counties'].isin([county])].shape[0] for county in counties]


def count_years(years, df):
    return [df.loc[df['ArchiveYear'].isin([year])].shape[0] for year in years]


def county_acresburned(df):
    acres_burned = [row['AcresBurned'] for ind, row in df.iterrows()]
    counties = [row['Counties'] for ind, row in df.iterrows()]
    dict = {}
    for county in counties:
        dict[county] = []

    for i in range(len(acres_burned)):
        dict[counties[i]].append(acres_burned[i])

    return dict


def county_averages(dict_acresburned):
    dict = {}
    for key in dict_acresburned.keys():
        dict[key] = np.mean(dict_acresburned[key])

    return dict


# pie chart
def generate_pie_chart(counts, sel_counties):
    plt.figure()
    explodes = [0 for i in range(len(counts))]
    maximum = counts.index(np.max(counts))
    explodes[maximum] = .25

    plt.pie(counts, labels=sel_counties, explode=explodes, autopct="%.2f")
    plt.title(f"Fires by County: {', '.join(sel_counties)}")
    plt.show()
    return plt


# bar_chart
def generate_bar_chart(dict_avg):
    plt.figure(figsize=(25, 3))
    x = dict_avg.keys()
    y = dict_avg.values()

    plt.bar(x, y)
    plt.xticks(rotation=90)
    plt.ylabel("Acres Burned")
    plt.xlabel("Counties")
    plt.title(f"Average Acres Burned by County: ")
    plt.show()

    return plt


# map
def generate_map(df):

    map_df = df.filter(['Name', 'Latitude', 'Longitude'])

    view_state = pdk.ViewState(latitude=map_df["Latitude"].mean(),
                               longitude=map_df["Longitude"].mean(),
                               zoom=5,
                               pitch=0)

    layer = pdk.Layer('ScatterplotLayer',
                      data=map_df,
                      get_position='[Longitude, Latitude]',
                      get_radius=1000,
                      get_color=[255, 0, 0],
                      pickable=True)

    tool_tip = {'html': 'Fires:<br/> <b>{Name}</b>',
               'style': {'backgroundColor': 'steelblue',
                         'color': 'white'}
               }

    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v10',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)

    st.pydeck_chart(map)


def main():
    # Streamlit:
    # At least three different UI Controls (sliders, drop downs, multi-selects, text box, etc)
    # Page design features (sidebar, fonts, colors, images, navigation)
    # Well-designed, professional-appearing, interactive website

    st.title("Using Python to Manipulate Data: California Fires")
    st.write("Explore this data of California Fires. Open the sidebar to begin.")
    st.sidebar.write("Choose options to display data")

    counties = st.sidebar.multiselect("Select Counties: ", all_counties())
    max_acres = st.sidebar.slider("Number of Acres: ", 0, 80000)
    years = st.sidebar.multiselect("Year: ", [2013, 2014, 2015, 2016, 2017, 2018, 2019])

    data = filter_data(counties, max_acres, years)
    series = count_counties(counties, data)

    # Pivot Table
    st.header("Pivot Table to show the number of crews involved in putting out fires each year in each county of California.")
    PivotTable = pd.pivot_table(data, values='CrewsInvolved', index=['Counties'], columns=['ArchiveYear'],
                                aggfunc=np.sum, fill_value=0)
    st.write(PivotTable)

    if len(counties) > 0:
        st.header("Fires in California")

        # Map
        st.write("View a map of California Fires")
        generate_map(data)

        # Pie chart
        st.write("View a pie chart  to see the percentage of fires by county based on the counties selected.")
        st.pyplot(generate_pie_chart(series, counties))

        # Bar chart
        st.write("View a bar chart that displays the average number of fires by County from 2013 - 2019")
        st.pyplot(generate_bar_chart(county_averages(county_acresburned(data))))
        st.write("This bar chart tells us that Colusa has had the most fires over the years.")


main()
