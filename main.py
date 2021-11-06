import dash
import pandas as pd

from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output

df = pd.read_csv('games.csv')
df = df[(~df.isna()).all(axis='columns') & (df['Year_of_Release'] >= 2000)]
df['Year_of_Release'] = pd.to_numeric(df['Year_of_Release'], downcast='integer')
df['User_Score'] = pd.to_numeric(df['User_Score'], errors='coerce')

user_critic_scores = px.scatter(
    df,
    x='User_Score',
    y='Critic_Score',
    color='Genre',
    labels=dict(
        User_Score='User Score',
        Critic_Score='Critic Score',
    ))

grouped_df = df.groupby(['Year_of_Release', 'Platform']).size().reset_index(name='Count')

stacked_games_year_platform = px.area(
    grouped_df,
    x='Year_of_Release',
    y='Count',
    color='Platform',
    labels=dict(
        Year_of_Release='Year'
    ))

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.Div(children=[
        html.H1(children='Game Analytics'),
        html.P(children='Information about games by genre, rating and year')
    ]),
    html.Div(children=[
        html.Div(children=[dcc.Dropdown(
            id='filter-genre-dropdown',
            options=[{'label': genre, 'value': genre} for genre in set(df['Genre'])],
            value=[],
            multi=True
        )], style={'flex': 1}),
        html.Div(children=[dcc.Dropdown(
            id='filter-rate-dropdown',
            options=[{'label': rate, 'value': rate} for rate in set(df['Rating'])],
            value=[],
            multi=True
        )], style={'flex': 1})
    ], style={
        'display': 'flex',
        'flex-direction': 'row'
    }),
    html.Br(),
    html.Div(id='label-game-number'),
    html.Div(children=[
        html.Div(children=[dcc.Graph(
            id='plot-stacked_games_year_platform',
            figure=stacked_games_year_platform
        )], style={
            'flex': 1
        }),
        html.Div(children=[dcc.Graph(
            id='plot-user-critic-scores',
            figure=user_critic_scores
        )], style={
            'flex': 1
        })
    ], style={
        'display': 'flex',
        'flex-direction': 'row'
    }),
    html.Div(children=[
        html.Div(children=[
            dcc.RangeSlider(
                id='filter-year-range',
                marks={year: str(year) for year in set(df['Year_of_Release'])},
                min=min(df['Year_of_Release']),
                max=max(df['Year_of_Release']),
                value=[min(df['Year_of_Release']), max(df['Year_of_Release'])]
            )
        ], style={
            'flex': 1
        }),
        html.Div(style={
            'flex': 1
        })
    ], style={
        'display': 'flex',
        'flex-direction': 'row'
    })
])


@app.callback(
    Output(component_id='label-game-number', component_property='children'),
    Input(component_id='filter-genre-dropdown', component_property='value'),
    Input(component_id='filter-rate-dropdown', component_property='value'),
    Input(component_id='filter-year-range', component_property='value')
)
def update_game_number(genre, rating, years):
    return 'Selected {} games'.format(len(df[get_mask_by_filters(genre, rating, years)]))


@app.callback(
    Output(component_id='plot-user-critic-scores', component_property='figure'),
    Input(component_id='filter-genre-dropdown', component_property='value'),
    Input(component_id='filter-rate-dropdown', component_property='value'),
    Input(component_id='filter-year-range', component_property='value')
)
def update_user_critic_scores_plot(genre, rating, years):
    return px.scatter(
        df[get_mask_by_filters(genre, rating, years)],
        x='User_Score',
        y='Critic_Score',
        color='Genre',
        labels=dict(
            User_Score='User Score',
            Critic_Score='Critic Score'
        ))


@app.callback(
    Output(component_id='plot-stacked_games_year_platform', component_property='figure'),
    Input(component_id='filter-genre-dropdown', component_property='value'),
    Input(component_id='filter-rate-dropdown', component_property='value'),
    Input(component_id='filter-year-range', component_property='value')
)
def update_stacked_games_year_platform(genre, rating, years):
    result_df = df[get_mask_by_filters(genre, rating, years)] \
        .groupby(['Year_of_Release', 'Platform']) \
        .size() \
        .reset_index(name='Count')
    return px.area(
        result_df,
        x='Year_of_Release',
        y='Count',
        color='Platform',
        labels=dict(
            Year_of_Release='Year'
        )
    )


def get_mask_by_filters(genre, rating, years):
    genre_mask = df['Genre'].isin(genre) if len(genre) > 0 else ~df['Genre'].isin([])
    rating_mask = df['Rating'].isin(rating) if len(rating) > 0 else ~df['Rating'].isin([])
    year_mask = df['Year_of_Release'].between(*years)
    return genre_mask & rating_mask & year_mask;


if __name__ == '__main__':
    app.run_server(debug=True)
