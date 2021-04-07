import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from bokeh.plotting import figure
from bokeh.io import output_notebook, show
import datetime as dt
from bokeh import events
from bokeh.models import CustomJS, Div, Button
from bokeh.layouts import column, row
from plotly.colors import n_colors
import streamlit as st
def clean(l):
    for i in range(len(l)):
        l[i] = l[i].strip()
        l[i] = l[i].replace("'", '')
        l[i] = l[i].replace("'", '')
    return l
def get_singer(l, singers):
    for i in range(len(l)):
        singers.append(l[i])
    return singers
singers = []
data = pd.read_csv('data.csv')
data.sort_values(['year'], inplace = True)

dat = data.copy()
dat['artists'] = dat['artists'].str[2:-2]
soloists = dat[dat['artists'].str.split(',').apply(len)==1]
#dat['artists'] = dat['artists'].str.split(',')
#dat['artists'] = dat['artists'].apply(clean)

dist_per_year = []
for year in data['year'].unique():
    dist_per_year.append(list(data['tempo'][data['year'] == year]))
singers = []
for i in dat['artists'].values:
    get_singer(i, singers)

subdat = dat.groupby('year').mean()

st.set_page_config(page_title="Spotify insights",
                  # page_icon='/Users/anastasia/Desktop/archive/spotlog.png',
                   layout='wide')
st.title("Insights of Spotify music library")
st.markdown(
"""
This app serves to visualize dataset of Spotify music from 1920 till 2014. Here you can get information on song-, artist-, and general levels. """
)
st.sidebar.markdown("Select the level of data")
select_event = st.sidebar.selectbox('How do you want to explore data?',
                                    ['The whole dataset', 'The artist'])
if select_event == 'The whole dataset':
    st.markdown("You can hide perticular variables by click on them")
    fig = go.Figure()
    fig.add_trace(
    go.Scatter(x=list(subdat.index), y=list(subdat['acousticness']), line=dict(color="#26a122"), name = 'Acousticness') )
    fig.add_trace(
    go.Scatter(x=list(subdat.index), y=list(subdat['danceability']), line=dict(color="#1edee3"), name = 'Danceability'))
    fig.add_trace(
    go.Scatter(x=list(subdat.index), y=list(subdat['energy']), line=dict(color="#6e0af0"), name = 'Energy'))
    fig.update_layout(
    title_text="Means of music characteristics through years"
    )

# Add range slider
    fig.update_layout(
        xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
      )
     )

    st.write(fig)
    fig = go.Figure()

    fig.add_trace(
    go.Scatter(x=list(np.sort(data['year'].unique()).astype(str)), y=list(data.groupby('year').count()['artists']), line=dict(color="#26a122")))


    fig.update_layout(
    title_text="Number of songs per year"
    )


    fig.update_layout(
       xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
       )
     )
    st.write(fig)
    st.markdown('This Violin chart helps to investigate how the mean music tempo has been changing')
    value = st.slider("Year range", 1920, 2014, (1920, 2014), 1)
    colors = n_colors('rgb(135, 251, 44)', 'rgb(75, 144, 22)', value[1]-value[0], colortype='rgb')
    fig = go.Figure()
    for data_line, color, year in zip(dist_per_year[(value[0]-1920):(value[1]-1920)], colors, data['year'].unique()[(value[0]-1920):(value[1]-1920)]):
        fig.add_trace(go.Violin(x=data_line, line_color=color, name=str(year)))
    fig.update_traces(orientation='h', side='positive', width=3, points=False)
    fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False)
    st.write(fig)
if select_event == 'The artist':
    st.markdown("### **Select Artist:**")
    select_artist = []
    select_artist.append(st.selectbox('', sorted(soloists['artists'].unique())))
    artist = soloists[soloists['artists'].str.contains(select_artist[0])]
    st.markdown("### **Summary statistics:**")
    st.markdown("Here there is aggregated values of artist's songs characteristics")
    fig = go.Figure(go.Bar(
        x=artist[['danceability', 'energy', 'instrumentalness', 'speechiness', "liveness"]].mean(),
        y=['Danceability', 'Energy', 'Instrumentalness', 'Speechiness', "Liveness"],
        marker=dict(color="#26a122"),
        orientation='h'))
    st.write(fig)
    st.markdown("This graph provides information of singer's works per year and their raitings in the USA")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=artist['year'],
        y=artist['popularity'],
        mode='markers',
        # marker_color = artist_df['clusters'].map(color_dict),
        customdata=artist[['year', 'name', 'popularity']],
        hovertemplate='<b>Year: %{customdata[0]}</b><br>Rank: %{customdata[2]} <br>Title: %{customdata[1]}',
        legendgroup='grp1',
        showlegend=False, line=dict(color="#26a122")
    ))
    fig.update_traces(marker=dict(symbol='circle', size=12
                                  # ,line = dict(color = 'grey', width = 0.5)
                                  ),
                      name="")
    fig.update_yaxes(autorange='reversed', title='Rank', showgrid=True,
                     mirror=True, zeroline=False, linecolor='black',
                     title_standoff=0, gridcolor='white', gridwidth=0.1)
    fig.update_xaxes(title="", showgrid=True, mirror=True,
                     linecolor='black', range=[(min(artist['year'])-1), (max(artist['year'])+1)],
                     gridcolor='white', gridwidth=0.1)
    st.write(fig)
    st.markdown("### **Select Songs for comparison:**")
    songs = st.multiselect( 'What are your favorite colors', artist['name'].values)
    st.write(type(songs), len(songs))
#data description
with st.beta_expander("Data description"):
    st.markdown("I have taken the dataset Spotify Dataset 1921-2020, 160k+ Tracks from kaggle.com." +
                "Since it was quite massive and contains plenty of lesser-known artist, I have reduced the number of observations with careful cleaning."+
                "It helps make the app work faster.")
    col1, col2, col3 = st.beta_columns(3)

    with col1:
        st.subheader("Acousticness")
        st.markdown("A confidence measure from 0.0 to 1.0 of whether the " +
                    "track is acoustic. 1.0 represents high confidence the track is acoustic.")

        st.subheader("Liveness")
        st.markdown("Detects the presence of an audience in the recording. Higher liveness values " +
                    "represent an increased probability that the track was performed live. A value above 0.8 " +
                    "provides strong likelihood that the track is live.")

        st.subheader("Speechiness ")
        st.markdown("Detects the presence of spoken words in a track. The more exclusively speech-like the " +
                    "recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values " +
                    "above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and" +
                    "0.66 describe tracks that may contain both music and speech, either in sections or layered, including such" +
                    "cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks")

    with col2:
        st.subheader("Danceability")
        st.markdown("Describes how suitable a track is for dancing based on a " +
                    "combination of musical elements including tempo, rhythm stability, beat strength, " +
                    "and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.")

        st.subheader("Instrumentalness")
        st.markdown("Predicts whether a track contains no vocals. " +
                    "“Ooh” and “aah” sounds are treated as instrumental in this context. " +
                    "Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness " +
                    "value is to 1.0, the greater likelihood the track contains no vocal content. Values " +
                    "above 0.5 are intended to represent instrumental tracks, but confidence is higher as the " +
                    "value approaches 1.0")

        st.subheader("Tempo")
        st.markdown(
            "The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is" +
            "the speed or pace of a given piece and derives directly from the average beat duration.")

    with col3:
        st.subheader("Energy")
        st.markdown("Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity " +
                    "and activity. Typically, energetic tracks feel fast, loud, and noisy." +
                    "For example, death metal has high energy, while a Bach prelude scores low on the scale. " +
                    "Perceptual features contributing to this attribute include dynamic range, perceived loudness, " +
                    "timbre, onset rate, and general entropy.")

        st.subheader("Loudness")
        st.markdown("The overall loudness of a track in decibels (dB). Loudness values are " +
                    "averaged across the entire track and are useful for comparing relative loudness " +
                    "of tracks. Loudness is the quality of a sound that is the primary psychological " +
                    "correlate of physical strength (amplitude). Values typical range between -60 and 0 db")

        st.subheader("Valence")
        st.markdown("A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. " +
                    "Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low" +
                    "valence sound more negative (e.g. sad, depressed, angry).")
