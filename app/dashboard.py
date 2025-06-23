import dash
from dash import dcc, html, dash_table, Input, Output
import sqlite3
import pandas as pd
import plotly.express as px
import os

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mlb_stats.db")
DB_PATH = os.path.abspath(DB_PATH)

# Function to load all unique values from both tables (hitting + pitching)
def get_unique_values(column):
    query = f"""
        SELECT DISTINCT {column} FROM hitting_stats
        UNION
        SELECT DISTINCT {column} FROM pitching_stats
        ORDER BY {column}
    """
    with sqlite3.connect(DB_PATH) as conn:
        return [row[0] for row in conn.execute(query).fetchall()]

# Get unique values for filters
players = get_unique_values("Player")
years = get_unique_values("Year")
events = get_unique_values("Event")

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server
app.title = "MLB Stats Dashboard"

app.layout = html.Div([
    html.H1("\u26be MLB Stats Dashboard"),

    html.P(
        "Use the dropdowns below to filter and explore MLB statistics interactively.",
        style={"fontSize": "16px", "marginTop": "10px", "marginBottom": "20px"}
    ),

    html.Div([
        html.Label("Player"),
        dcc.Dropdown(options=[{"label": p, "value": p} for p in players], id="player-filter", placeholder="Select player"),
    ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

    html.Div([
        html.Label("Year"),
        dcc.Dropdown(options=[{"label": y, "value": y} for y in years], id="year-filter", placeholder="Select year"),
    ], style={"width": "20%", "display": "inline-block", "padding": "10px"}),

    html.Div([
        html.Label("Event"),
        dcc.Dropdown(options=[{"label": e, "value": e} for e in events], id="event-filter", placeholder="Select event"),
    ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),


    html.Div([
        html.Label("Stat Type"),
        dcc.Dropdown(
            id="type-filter",
            options=[
                {"label": "All", "value": "all"},
                {"label": "Hitting", "value": "hitting"},
                {"label": "Pitching", "value": "pitching"},
            ],
            value="all",
            placeholder="Select stat type"
        ),
    ], style={"width": "15%", "display": "inline-block", "padding": "10px"}),

    html.Br(),
    html.Div(id="kpi-cards", style={"display": "flex", "justifyContent": "start"}),
    html.Br(),
    
    dash_table.DataTable(id="stats-table", page_size=15, style_table={'overflowX': 'auto'}),

    html.Br(),

    html.Div([
        dcc.Graph(id="bar-chart"),
        html.P("Bar chart shows total values aggregated by event.", 
              style={"textAlign": "center", "fontStyle": "italic", "color": "gray", "marginTop": "5px"})
    ], style={"marginBottom": "30px"}),

    html.Div([
        dcc.Graph(id="line-chart"),
        html.P("Line chart displays total values over years to show trends.", 
              style={"textAlign": "center", "fontStyle": "italic", "color": "gray", "marginTop": "5px"})
    ], style={"marginBottom": "30px"}),

    html.Div([
        dcc.Graph(id="pie-chart"),
        html.P("Pie chart highlights top 10 player contributions plus others combined.", 
              style={"textAlign": "center", "fontStyle": "italic", "color": "gray", "marginTop": "5px"})
    ], style={"marginBottom": "30px"}),

    html.Div([
        dcc.Graph(id="scatter-plot"),
        html.P(
            "Scatter plot shows distribution of 'Value' over the years by event type. "
            "It helps identify peaks and trends.",
            style={"textAlign": "center", "fontStyle": "italic", "color": "gray", "marginTop": "5px"}
        )
    ], style={"marginBottom": "30px"}),

    html.Hr(),

    html.Div([
        html.H3("About This Dashboard"),
        html.P(
            "This dashboard presents historical statistics from Major League Baseball. "
            "Data is collected via automated web scraping using Selenium, processed with pandas, "
            "and stored in a SQLite database. You can explore player performance, event frequency, "
            "and other trends by adjusting the filters above.",
            style={"fontSize": "15px"}
        ),
        html.P(
            "Built with ❤️ using Python, Dash, and Plotly.",
            style={"fontSize": "13px", "fontStyle": "italic", "color": "gray"}
        )
    ], style={"padding": "30px", "backgroundColor": "#f9f9f9", "borderRadius": "8px"})
])

@app.callback(
    Output("kpi-cards", "children"),
    Output("stats-table", "data"),
    Output("stats-table", "columns"),
    Output("bar-chart", "figure"),
    Output("line-chart", "figure"),
    Output("pie-chart", "figure"),
    Output("scatter-plot", "figure"),
    Input("player-filter", "value"),
    Input("year-filter", "value"),
    Input("event-filter", "value"),
    Input("type-filter", "value")
)
def update_dashboard(player, year, event, stat_type):
    filters = []
    params = []

    if player:
        filters.append("Player = ?")
        params.append(player)
    if year:
        filters.append("Year = ?")
        params.append(year)
    if event:
        filters.append("Event = ?")
        params.append(event)

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    hitting_query = """
        SELECT h.Year, h.Event, h.Player, h.Team, h.Value, e.Description
        FROM hitting_stats h
        LEFT JOIN events e ON h.Event = e.Event
    """
    pitching_query = """
        SELECT p.Year, p.Event, p.Player, p.Team, p.Value, e.Description
        FROM pitching_stats p
        LEFT JOIN events e ON p.Event = e.Event
    """

    if stat_type == "hitting":
        base_query = hitting_query
    elif stat_type == "pitching":
        base_query = pitching_query
    else:
        base_query = f"""
            {hitting_query}
            UNION ALL
            {pitching_query}
        """

    query = f"""
        SELECT * FROM ({base_query})
        {where_clause}
        ORDER BY Year, Player
    """

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn, params=params)

    # If there is no data
    if df.empty:
        empty_fig = px.scatter(title="No data to display. Please adjust filters.")
        return [], [], [], empty_fig, empty_fig, empty_fig, empty_fig

    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict("records")

  # KPI Cards
    kpi_cards = html.Div([
        html.Div([
            html.H4("Total Players"),
            html.P(f"{df['Player'].nunique()}")
        ], style={"width": "30%", "padding": "20px", "margin": "10px", "backgroundColor": "#e5ecf6", "borderRadius": "10px"}),

        html.Div([
            html.H4("Total Events"),
            html.P(f"{df['Event'].nunique()}")
        ], style={"width": "30%", "padding": "20px", "margin": "10px", "backgroundColor": "#e5ecf6", "borderRadius": "10px"}),

        html.Div([
            html.H4("Total Value"),
            html.P(f"{df['Value'].sum():,.0f}")
        ], style={"width": "30%", "padding": "20px", "margin": "10px", "backgroundColor": "#e5ecf6", "borderRadius": "10px"})
    ], style={"display": "flex", "justifyContent": "space-around"})  

    # Chart 1: Bar chart by event
    bar_data = df.groupby("Event", as_index=False)["Value"].sum()
    bar_fig = px.bar(bar_data, x="Event", y="Value", title="Total Value by Event")

    # Chart 2: Line chart by year
    line_data = df.groupby("Year", as_index=False)["Value"].sum()
    line_fig = px.line(line_data, x="Year", y="Value", title="Total Value by Year")
    line_fig.update_traces(line=dict(color='#ff6696', width=3), marker=dict(size=8))

    # Chart 3: Pie chart by players (Top 10 + "Other")
    player_data = df.groupby("Player")["Value"].sum().sort_values(ascending=False)
    top_n = 10
    top_players = player_data.head(top_n)
    others = player_data[top_n:].sum()
    if others > 0:
        top_players["Other"] = others
    pie_fig = px.pie(names=top_players.index, values=top_players.values, title="Top 10 Player Contributions")

    # Chart 4: Scatter plot Value vs Year by Event
    scatter_fig = px.scatter(df, x="Year", y="Value", color="Event", title="Event Values Over Time")

    return kpi_cards, data, columns, bar_fig, line_fig, pie_fig, scatter_fig

if __name__ == "__main__":
    app.run(debug=True)




