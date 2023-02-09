import plotly.express as px
import plotly.offline
import pandas as pd
import requests
import csv
from datetime import datetime
import time

def update_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    response = requests.get(url)
    data = response.json()

    # extract the earthquake information
    earthquakes = data['features']

    # write the data to a CSV file
    with open('./earthquakes.csv', 'w', newline='') as csvfile:
        fieldnames = ['time', 'latitude', 'longitude', 'depth', 'mag']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for earthquake in earthquakes:
            time = datetime.utcfromtimestamp(earthquake['properties']['time']/1000)
            writer.writerow({
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'latitude': earthquake['geometry']['coordinates'][1],
                'longitude': earthquake['geometry']['coordinates'][0],
                'depth': earthquake['geometry']['coordinates'][2],
                'mag': abs(earthquake['properties']['mag'])
            })

def update_figure():
    df = pd.read_csv("./earthquakes.csv", encoding="utf-8")

    df.dropna(
        axis=0,
        how='any',
        thresh=None,
        subset=None,
        inplace=True
    )

    color_scale = [(0, 'yellow'), (1,'red')]
    df["size"] = df["mag"].apply(lambda x: x if x > 5 else 1)*3
    fig = px.scatter_mapbox(df, 
                            lat="latitude", 
                            lon="longitude", 
                            hover_name="time", 
                            hover_data=["time", "mag"],
                            color="mag",
                            color_continuous_scale=color_scale,
                            size="size",
                            size_max=25,
                            zoom=1, 
                            height=None,
                            width=None)

    fig.update_layout(mapbox_style="open-street-map",mapbox_center=dict(lat=30, lon=0))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(
        annotations=[
            dict(
                x=0.5,
                y=0.05,
                align='center',
                valign='top',
                text="Updated at " + str(datetime.utcnow()),
                showarrow=False
            )
        ]
    )
    fig.show()


update_earthquake_data()
#plotly.offline.init_notebook_mode(connected=False)
update_figure()

while True:
    time.sleep(60) # wait for 5 minutes
    update_earthquake_data()
    update_figure()
