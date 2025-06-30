import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import wbdata
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# List of post-Soviet countries
post_soviet = [
    'Armenia', 'Azerbaijan', 'Belarus', 'Estonia', 'Georgia',
    'Kazakhstan', 'Kyrgyz Republic', 'Latvia', 'Lithuania',
    'Moldova', 'Russian Federation', 'Tajikistan', 'Turkmenistan',
    'Ukraine', 'Uzbekistan'
]

country_map = {
    'ARM': 'Armenia', 'AZE': 'Azerbaijan', 'BLR': 'Belarus', 'EST': 'Estonia',
    'GEO': 'Georgia', 'KAZ': 'Kazakhstan', 'KGZ': 'Kyrgyz Republic',
    'LVA': 'Latvia', 'LTU': 'Lithuania', 'MDA': 'Moldova',
    'RUS': 'Russian Federation', 'TJK': 'Tajikistan', 'TKM': 'Turkmenistan',
    'UKR': 'Ukraine', 'UZB': 'Uzbekistan'
}

def get_gdp_ppp():
    indicators = {'NY.GDP.PCAP.PP.CD': 'GDP per capita PPP'}
data = wbdata.get_dataframe(indicators, country=list(country_map.keys()))
    data.reset_index(inplace=True)
    df_latest = data.sort_values("date").drop_duplicates("country", keep="last")
    df_latest['Country'] = df_latest['country'].map(country_map)
    return df_latest

def get_freedom_index():
    url = 'https://freedomhouse.org/countries/freedom-world/scores'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('table')
    df = pd.read_html(str(table))[0]
    df = df[df['Country/Territory'].isin(post_soviet)]
    return df

# Load data
gdp_df = get_gdp_ppp()
freedom_df = get_freedom_index()

# Initialize Dash
app = dash.Dash(__name__)
server = app.server

# App layout
app.layout = html.Div([
    html.H1("Post-Soviet Region Dashboard", style={'textAlign': 'center'}),

    dcc.Tabs([
        dcc.Tab(label='GDP per Capita PPP', children=[
            dcc.Graph(
                figure=px.bar(gdp_df, x='Country', y='GDP per capita PPP', title="GDP per capita PPP (USD)")
            )
        ]),
        dcc.Tab(label='Freedom Index', children=[
            dcc.Graph(
                figure=px.choropleth(
                    freedom_df,
                    locations="Country/Territory",
                    locationmode="country names",
                    color="Aggregate Score",
                    hover_name="Country/Territory",
                    color_continuous_scale=px.colors.sequential.Reds,
                    title="Freedom Index Map"
                )
            ),
            html.Div([
                html.H4("Freedom Index Table"),
                dcc.Graph(
                    figure=px.scatter(
                        freedom_df,
                        x="Country/Territory",
                        y="Aggregate Score",
                        title="Freedom Score by Country"
                    )
                )
            ])
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
