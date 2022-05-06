#importing libraries 
import pandas as pd
import datetime as dt
import geopandas
import matplotlib.pyplot as plt
import numpy as np
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from dash import Dash, dash_table
import plotly.graph_objects as go
from pandas.io.html import read_html


#########################################
#importing files
spotify=pd.read_csv('Spotify-2000.csv')

#selecting songs after 2010. 
spotify_2010=spotify[spotify['Year']>=2010]
number_of_songs=spotify_2010.groupby('Year')['Title'].count().reset_index()


spotify_2010_groupby_median_df = spotify_2010.groupby('Year')[['Beats Per Minute (BPM)','Energy','Danceability','Loudness (dB)','Liveness','Valence','Length (Duration)','Acousticness','Speechiness','Popularity']].median().round(2).reset_index()

#to scrape data from wikipedia. 
#data to scrape: 5 artists who win AMA every year from 2010-2019
url_page = 'https://en.wikipedia.org/wiki/American_Music_Award_for_Artist_of_the_Year'
tables = read_html(url_page, attrs={'class':'wikitable'})
ama_test_df = pd.DataFrame(tables[2]).reset_index()

#cleaning AMA winner tables 
ama_test_df = ama_test_df.set_axis(['index','year', 'ama_artist', 'extra'], axis=1, inplace=False)
ama_test_df = ama_test_df.drop(columns=['index','extra'])
ama_test_df = ama_test_df.drop(range(0,5))
ama_test_df['ama_clean_year'] = ama_test_df['year'].apply(lambda x:x.split('(')[0])
ama_test_df = ama_test_df.loc[ama_test_df['ama_artist'].notnull()]
ama_test_df[ama_test_df.ama_artist.str.contains(r'[[0-9]]')]
ama_test_df = ama_test_df.drop(ama_test_df[ama_test_df.ama_artist.str.contains(r'[[0-9]]')].index)
ama_test_df = ama_test_df.drop(columns='year')
ama_test_df['ama_clean_year'] = ama_test_df['ama_clean_year'].apply(lambda x:int(x))
ama_winners_df = spotify_2010.merge(ama_test_df, left_on=['Year','Artist'], right_on=['ama_clean_year','ama_artist'], how='inner')

#create tables to see most 10 songs and artists ever year. 
most_pop_artist_df = spotify_2010.groupby(['Year','Artist'])['Popularity'].mean().reset_index()
spotify_top_10 = spotify_2010[spotify_2010.groupby('Year')['Popularity'].rank(ascending=False)<=10]
spotify_top_10_artists_raw = spotify_2010.groupby(['Year','Artist'])['Popularity'].mean().reset_index()
spotify_top_10_artists_df = spotify_top_10_artists_raw[spotify_top_10_artists_raw.groupby('Year')['Popularity'].rank(ascending=False)<=10]
df_pop_artists=most_pop_artist_df[most_pop_artist_df['Year']==2017] 
search_df = spotify[['Title','Artist','Top Genre','Popularity']]
artist_list = []
for artist in search_df['Artist']:
    if artist not in(artist_list):
        artist_list.append(artist)
song_list = []        
for song in spotify_2010['Title']:
    if artist not in(song_list):
        song_list.append(song)        
ama_winners_small_df = pd.DataFrame(ama_winners_df[['Year','Artist','Title','Popularity']])
ama_winners_small_df = ama_winners_small_df.append({'Year': 2010, 'Artist': 'No Winner in This Year','Title':'','Popularity':''},ignore_index=True)
ama_winners_small_df = ama_winners_small_df.append({'Year': 2014, 'Artist': 'No Winner in This Year','Title':'','Popularity':''},ignore_index=True)
ama_winners_small_df = ama_winners_small_df.append({'Year': 2015, 'Artist': 'No Winner in This Year','Title':'','Popularity':''},ignore_index=True)
ama_winners_small_df = ama_winners_small_df.append({'Year': 2016, 'Artist': 'No Winner in This Year','Title':'','Popularity':''},ignore_index=True)
ama_winners_small_df = ama_winners_small_df.append({'Year': 2019, 'Artist': 'No Winner in This Year','Title':'','Popularity':''},ignore_index=True)
ama_with_links_df = pd.read_csv('to_match_youtube2.csv',index_col=False)
ama_with_links_df = ama_with_links_df.rename({'Youtube2': 'Link'}, axis=1)

#ama_with_links_df.drop('Unnamed: 0',axis=1,inplace=True)
pie_df = spotify_2010.groupby(['Year','Top Genre'])['Title'].count().reset_index()
song_attribute_list = ['Beats Per Minute (BPM)', 'Energy', 'Danceability',
       'Loudness (dB)', 'Liveness', 'Valence', 'Acousticness', 'Speechiness',
       'Popularity']
spotify_2010_pie_component_df = spotify_2010[['Title','Beats Per Minute (BPM)', 'Energy', 'Danceability', 'Loudness (dB)',
       'Liveness', 'Valence', 'Length (Duration)', 'Acousticness',
       'Speechiness']]

#########################################
#starting the dashboard

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

### pandas dataframe to html table
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


app = dash.Dash(__name__, external_stylesheets=stylesheet)
server = app.server



#top 3 Muisc Trend of the Year
pie_top5_df = pie_df[pie_df.groupby('Year')['Title'].rank(ascending=False)<=3].sort_values(by='Title', ascending=True)
genre_trends_fig = px.bar(pie_top5_df, y='Title', x='Year',color='Top Genre'
       , orientation='v',text = 'Top Genre')
genre_trends_fig.update_layout(height=400,legend={'itemclick':False},
    title=dict(text='<b>Top 3 Music Trends of the Year</b>',
        x=0.5,
        y=0.95,
        font=dict(
            family="Arial",
            size=20,
            color='#000000')))


#########################################
#app layout 

app.layout = html.Div([
    #bentley logo 
    html.Img(src='https://d2f5upgbvkx8pz.cloudfront.net/sites/default/files/inline-files/Bentley_Logo_Shield_Only_Blue.png',className='img', style={'height':'5%', 'width':'5%', 'display': 'inline-block','margin-left': '3vw', 'margin-right': '3vw'})
    ,dcc.Markdown('''
    >  MA 705, Professor Luke Cherveny
    
    >  Individual Project: Phung Luu
    
     __About this dashboard:__
    
    The dashboard combined the available dataset from [Kaggle Spotify - All-Time Top 2000s](https://bit.ly/3vH1plg) with data from [Wikipedia American Music Award for Artist of the Year](https://bit.ly/3MP6CwR) to assist users in searching for the following information:
    * Top 10 most popular songs on Spotify from  2010 to 2019
    * Spotify's artists who won "The American Music Awards" in that year.
    * Top 3 famous genres of the year
    * Other intriguing elements that make up a song

    
    ''', style={'margin-left': '3vw', 'margin-right': '3vw','whiteSpace': 'pre-line',
               "background": "#1f77b4",
    'text-transform': 'uppercase',
    'color': 'white',
    'font-size': '14px',
    'font-weight': 600,
    'align-items': 'center',
    'justify-content': 'center',
    'border-radius': '4px',
    'padding':'7px'}
    )

    ,html.Br()
    ,html.Br()
    
 
#title of the dashboard
    ,html.H1("Spotify's Music Trends Over the Last Decade",style={'textAlign': 'center','color': 'midnightblue',"font-weight": "bold", 'margin-left': '3vw', 'margin-right': '3vw','margin-top': '2vw','whiteSpace': 'pre-line'})
    
#link to go to spotify 
    ,html.A('Click to go to Spotify',
           href='https://www.spotify.com/',
           target='_blank', style={'margin-left': '3vw', 'margin-right': '3vw'} )

#dropdown to select years to see most popular songs
    ,html.Div([html.H4('Select Year',style={'textAlign': 'left','color': 'midnightblue',"font-weight": "bold",'margin-left': '3vw', 'margin-right': '3vw','whiteSpace': 'pre-line' }),
              dcc.Dropdown([2010,2011,2012,2013,2014,2015,2016,2017,2018,2019],2017,
                           id='checklist',style={'margin-left': '1.5vw', 'margin-right': '5vw'})])

#scatterplot for top10 songs    
    ,dcc.Graph(id='fig_top_10_songs_scatter_id', style={'textAlign': 'center','margin-left': '10vw', 'margin-right': '10vw', 'margin-top': '1vw',
                                                                                        'align-items': 'center','justify-content': 'center'})
    ,html.Div(children=[dcc.Graph(id='fig_top_artists_id', style={'float': 'left', 'margin-top': '-2vw','margin-left': '7vw','whiteSpace': 'pre-line','display':'inline-block', 'width': 800})
                    , html.H4("Spotify Artists Won 'The American Music Awards' Of Selected Year",style={'margin-top': '-3vw','margin-right': '4vw'
                                                                                                 ,'whiteSpace': 'pre-line','display':'inline-block'
                                                                                                 ,'font-size':'20px','font':'Arial',"font-weight": "bold"
                                                                                                ,'font-color':'#000000'})
                    , html.Div(dash_table.DataTable(
                        id="table_url",
                        columns=[
                            {"name": "Year", "id": "Year", 'type':'numeric'},
                            {"name": "Artist", "id": "Artist", 'type':'text'},
                            {"name": "Title", "id": "Title", 'type':'text'},
                            {"name": "Link", "id": "Link", 'type':'text', "presentation": "markdown"}],
                        data=ama_with_links_df.to_dict('records'),
                        markdown_options={"html": True},
                        style_data={'whiteSpace': 'normal','height': 'auto'}
                        ,fill_width=False 
                       ),style={'margin-top': '-4vw','margin-right': '3vw','whiteSpace': 'pre-line','display':'inline-block'}
                              )])
    
# Select Arrist Name to See Most Popular Songs
    ,html.Div(children=
              [html.H4('Select Artist Name to See Most Popular Songs',
             style={'textAlign': 'left','color': 'midnightblue',"font-weight": "bold", 'margin-left': '3vw', 'margin-right': '3vw','margin-top': '10vw','width': 600})      
               ,html.Div(
              [dcc.Dropdown(artist_list,'Ed Sheeran',id='checklist_artist',style={'margin-left': '1.5vw', 'margin-right': '5vw','width': 600 }),
               dcc.Graph(id='fig_search_id',style={'textAlign': 'center','margin-left': '3vw', 'margin-top': '1vw',
                                                                                        'align-items': 'center','justify-content': 'center','width': 600 }
            )])
               ,html.Div(
                   [html.H4('Select A Song to See Its Attributes',style={'float': 'right','color': 'midnightblue',"font-weight": "bold",'width': 600,'margin-top': '10vw' })
                    ,html.Div(dcc.Dropdown(song_list,'Dancing On My Own',id = 'song_component_dropdown',style={'margin-left': '1.5vw', 'margin-right': '5vw','width': 600 }) ,style=dict(width='100%'))
                    ,html.Div(dcc.Graph(id='component_pie_id',style={'margin-left': '1.5vw', 'margin-right': '5vw' })),
        ],style={'margin-top': '-4vw','whiteSpace': 'pre-line','display':'inline-block'}
               )])   

    
    

#drop down to select songs and see a pie chart of its attributes     
   
    
#genre trends over the years     
,html.H4('Select Attributes to See How They Changed Over the Years',style={'textAlign': 'left','color': 'midnightblue',"font-weight": "bold", 'margin-left': '3vw', 'margin-right': '3vw'})
    
#drop down and line chart to show how song attributes change over time.     
    ,dcc.Dropdown(['Beats Per Minute (BPM)', 'Energy', 'Danceability',
       'Loudness (dB)', 'Liveness', 'Valence', 'Acousticness', 'Speechiness',
       'Popularity'],
    ['Beats Per Minute (BPM)', 'Energy','Valence'],
    multi=True,id = 'dropdown_line',style={'whiteSpace': 'pre-line','textAlign': 'left','margin-left': '1vw', 'margin-right': '5vw'})
    ,dcc.Graph(id='line_fig_id')

    
    ,dcc.Markdown('''
    
    
    * Beats per Minute(BPM): The tempo of the song
    * Energy: The energy of a song - the higher = more energy
    * Danceability: The higher the value, the easier it is to dance to this song
    * Loudness: The higher the value, the louder the song
    * Valence: The higher the value, the more positive mood for the song
    * Length: The duration of the song
    * Acoustic: The higher the value the more acoustic the song is
    * Speechiness: The higher the value the more spoken words the song contains
    * Popularity: The higher the value the more popular the song is

    
    ''', style={'margin-left': '3vw', 'margin-right': '3vw','whiteSpace': 'pre-line' })

    ,html.Br()
    ,html.Br()
    
    ,dcc.Graph(figure=genre_trends_fig,id='genre_trends_fig_id')
    
    ,html.Br()
    ,html.Br()
    
    ,dcc.Markdown('''
      May 2022, Phung Luu.
    
    ''', style={'margin-left': '3vw', 'margin-right': '3vw','whiteSpace': 'pre-line' })
    ,html.Br()
   
])


#########################################
#input and output for top 10 spotify songs scatterplot 

@app.callback(
    Output('fig_top_10_songs_scatter_id','figure'), 
    Input('checklist', 'value')
)
def update_plot(year):
    df_top_10_songs_scatter = spotify_top_10[spotify_top_10['Year']==year]
    fig_top_10_songs_scatter = px.scatter(df_top_10_songs_scatter.sort_values('Popularity'),y='Popularity',x='Title',text = 'Title'
                                          ,size_max=75
                                          ,hover_name ='Artist',size='Popularity',color="Popularity"
                                          ,color_continuous_scale='Oryel',width=1400, height=500
                                            )
                                        
    fig_top_10_songs_scatter.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_top_10_songs_scatter.update_xaxes(visible=False,showticklabels=False)
    fig_top_10_songs_scatter.update_layout(showlegend=False)
    fig_top_10_songs_scatter.update(layout_coloraxis_showscale=False)
    fig_top_10_songs_scatter.update_layout(height=400,
    title=dict(text='<b>Top 10 Greatest Songs Of Selected Year</b>',
        font=dict(
            family="Arial",
            size=20,
            color='#000000')))
    fig_top_10_songs_scatter.update(layout_coloraxis_showscale=False)
    
    return fig_top_10_songs_scatter



#input and output for AMA winner table/dataframe 

@app.callback(
    Output('table_url','data'), 
    Input('checklist', 'value')
)
    
def update_URL_table(value):
    data_table = ama_with_links_df[ama_with_links_df['Year']==value]
    return data_table.to_dict('records')


#input and output for top 10 spotify artist bar chart 

@app.callback(
    Output('fig_top_artists_id','figure'), 
    Input('checklist', 'value')
)

def update_artists(year):
    df_pop_artists=spotify_top_10_artists_df[spotify_top_10_artists_df['Year']==year] 
    fig_pop_artists = px.bar(df_pop_artists, y='Artist', x='Popularity'
                            ,color="Popularity",color_continuous_scale='RdBu')
    fig_pop_artists.update_layout(yaxis={'categoryorder':'total ascending'})
    
    fig_pop_artists.update_layout(height=400,
    title=dict(text='<b>Popular Artists on Spotify Of Selected Year</b>',
        x=0.5,
        y=0.95,
        font=dict(
            family="Arial",
            size=20,
            color='#000000')))
    fig_pop_artists.update(layout_coloraxis_showscale=False)
    return fig_pop_artists


# search songs by artist 

@app.callback(
    Output('fig_search_id','figure'), 
    Input('checklist_artist', 'value')
)


#input and output for song search 

def update_search(value):
    search_df = spotify[['Title','Artist','Top Genre','Popularity']]
    search_df_find = search_df[search_df['Artist']==value] 
    fig3 = go.Figure(data=[go.Table(
    header=dict(values=list(search_df_find.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[search_df_find.Title, search_df_find.Artist,search_df_find['Top Genre'],search_df_find.Popularity],
               fill_color='lavender',
               align='left'))])
    return fig3


@app.callback(
    Output('line_fig_id','figure'), 
    Input('dropdown_line', 'value')
)

#input and output for line chart to show song attributes over the years 

def update_line(attribute_list):
    line_fig = px.line(spotify_2010_groupby_median_df, x='Year',y=attribute_list)
    line_fig.update_traces(mode="markers+lines")
    return line_fig


#input and output for song components/attribute 

@app.callback(
    Output('component_pie_id','figure'), 
    Input('song_component_dropdown', 'value')
)
    
def pie_song_component_function(song_name):
    values = spotify_2010_pie_component_df[spotify_2010_pie_component_df['Title']==song_name][['Energy','Danceability'
                                                                                    ,'Liveness', 'Valence'
                                                                                    ,'Acousticness','Speechiness']].values.flatten().tolist()
    names = ['Energy','Danceability','Liveness', 'Valence','Acousticness','Speechiness']
    song_component_pie_fig = px.pie(values=values, names=names,width=500, height=500)
    song_component_pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    return song_component_pie_fig

    

if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False)
    
    
