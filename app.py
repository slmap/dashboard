
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, dash_table, Input, Output
import wbdata
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- List of post-Soviet countries ---
post_soviet = [
    'Russia', 'Ukraine', 'Georgia', 'Kazakhstan', 'Belarus', 'Armenia', 'Azerbaijan',
    'Moldova', 'Uzbekistan', 'Turkmenistan', 'Kyrgyzstan', 'Tajikistan', 'Estonia', 'Latvia', 'Lithuania'
]

# --- GDP PPP from World Bank ---
def get_gdp_ppp():
    country_map = {
        "RU": "Russia", "UA": "Ukraine", "GE": "Georgia", "KZ": "Kazakhstan", "BY": "Belarus",
        "AM": "Armenia", "AZ": "Azerbaijan", "MD": "Moldova", "UZ": "Uzbekistan",
        "TM": "Turkmenistan", "KG": "Kyrgyzstan", "TJ": "Tajikistan", "EE": "Estonia",
        "LV": "Latvia", "LT": "Lithuania"
    }
    indicators = {"NY.GDP.PCAP.PP.CD": "GDP PPP"}
    data = wbdata.get_dataframe(indicators, country=list(country_map.keys()), data_date=datetime(2023, 1, 1))
    data.reset_index(inplace=True)
    data['Country'] = data['country'].map(country_map)
    return data[['Country', 'GDP PPP']]

# --- Economic Freedom from Heritage ---
def get_economic_freedom():
    url = 'https://www.heritage.org/index/ranking'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table')
    df = pd.read_html(str(table))[0]
    df = df[df['Country Name'].isin(post_soviet)]
    df = df[['Country Name', 'Overall Score']]
    df.columns = ['Country', 'Economic Freedom']
    return df

# --- Freedom Index Placeholder (manual or pre-saved) ---
def get_freedom_index():
    # Simulated placeholder data
    freedom_data = {
        'Country': post_soviet,
        'Freedom Index': [20, 39, 61, 23, 19, 55, 28, 58, 11, 3, 27, 10, 94, 89, 91]
    }
    return pd.DataFrame(freedom_data)

# --- Merge Data ---
gdp_df = get_gdp_ppp()
eco_df = get_economic_freedom()
freedom_df = get_freedom_index()

combined = pd.merge(freedom_df, eco_df, on='Country')
combined = pd.merge(combined, gdp_df, on='Country')

# --- Initialize Dash App ---
app = dash.Dash(__name__)
server = app.server  # for deployment

# --- Layout ---
app.layout = html.Div([
    html.H1("Post-Soviet Space Index Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Index to View:"),
        dcc.Dropdown(
            id='index-selector',
            options=[
                {'label': 'Freedom Index', 'value': 'Freedom Index'},
                {'label': 'Economic Freedom', 'value': 'Economic Freedom'},
                {'label': 'GDP PPP', 'value': 'GDP PPP'}
            ],
            value='Freedom Index'
        )
    ], style={'width': '40%', 'margin': 'auto'}),

    dcc.Graph(id='dynamic-map'),

    html.Div([
        html.H2("Raw Data Table", style={'marginTop': '30px'}),
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in combined.columns],
            data=combined.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
            style_cell={"textAlign": "left", "padding": "5px"},
        )
    ])
])

# --- Callbacks ---
@app.callback(
    Output('dynamic-map', 'figure'),
    Input('index-selector', 'value')
)
def update_map(index):
    return px.choropleth(
        data_frame=combined,
        locations='Country',
        locationmode='country names',
        color=index,
        hover_name='Country',
        color_continuous_scale='Viridis',
        title=f'{index} Across Post-Soviet Countries'
    )

if __name__ == '__main__':
    app.run_server(debug=True)
