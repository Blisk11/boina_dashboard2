import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import pandas as pd
import numpy as np
from datetime import datetime, date
import streamlit as st
from math import floor
import seaborn as sns
import matplotlib as plt
from geopy.geocoders import Nominatim
import plotly.express as px
from PIL import Image


# streamlit options
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title='boina dashboard', layout = 'wide', initial_sidebar_state = 'auto')


hide_streamlit_style = """<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

pwd = st.text_input("Password:", value="")

if pwd!= 'fractaldefou':
    st.title('Please enter correct password')
else:
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    t1, t2 = st.columns((0.07,1)) 

    logo = Image.open('LOGO LMDO petit.jpg')

    t1.image(logo)
    t2.title("Dashboard demo: La maison de l'ostéopathie")

    df = pd.read_json('cleanded_df.json.gz', orient = 'index')

    # prep df
    df['month'] = ( pd.to_datetime(df['date_de_derniere_mise_a_jour'].str[:10])).dt.to_period('M')

    age_bins = []
    for i in range (0,100,10):
        age_bins.append(i)

    df['age_bin'] = pd.cut(df.age,
            bins=age_bins,
            labels=['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '70-80', '90-100', '100+'])


    df['departement'] = np.where(df['unnamed_30'].astype(str).str.len() ==6, '0'+ df['unnamed_30'].astype(str).str[0], df['unnamed_30'].astype(str).str[:2])
    df['departement'] = df['departement'].str.replace('na', 'non renseigné')


    df = df[df['statut'].isin(['À venir', 'Absent non excusé'])]

    df['nom osteo'] = df['agenda']

    df['rdv_compte'] =1

    df_copy = df.copy()

    df_copy['agenda'] = 'Tous'

    df = pd.concat([df, df_copy])

    with st.spinner('Updating Report...'):

        #Metrics setting and rendering

        DF_filter = st.selectbox('Choisir ostéo', df['agenda'].drop_duplicates().to_list() , help = 'Filtrer les données pour un ou tous les ostéos')
        df_data = df[df['agenda']==DF_filter]

        g1, g2 = st.columns((1,1))
        # bar chart

        data = df_data.groupby(['nom osteo', 'month'])['index'].count().reset_index()
        data.sort_values(['month', 'index'], ascending = [True, False], inplace=True)
        data['month'] = data['month'].astype(str).str.replace('-', '_')
        data.rename(columns = {'index':'nbs rdv'}, inplace=True)

        fig = px.bar(data, x="month", y="nbs rdv", color="nom osteo", title="Nb de rdv par mois")   
        g1.plotly_chart(fig, use_container_width=True)

        # Here we use a column with categorical data

        fig = px.histogram(df_data.sort_values('age_bin'), x="age_bin", color = 'nom osteo', title="Nb de rdv par groupe d'âge")    
        g2.plotly_chart(fig, use_container_width=True)


        px_table = df_data.groupby(['nom osteo', 'departement'])['rdv_compte'].sum().reset_index().sort_values('rdv_compte',ascending=False)
        px_table = px_table.pivot('departement', 'nom osteo', 'rdv_compte')
        # sort columns by osteo
        px_table = px_table[px_table.sum().sort_values(ascending=False).index.to_list()].fillna(' ')

        #st.dataframe(px_table)
        px_table.reset_index(inplace= True)
        fig = go.Figure(
            data = [go.Table (
                header = dict(
                values = list(px_table.columns),
                font=dict(size=12, color = 'white'),
                fill_color = '#264653',
                line_color = 'rgba(255,255,255,0.2)',
                align = ['left','center'],
                #text wrapping
                height=20
                )
            , cells = dict(
                values = [px_table[K].tolist() for K in px_table.columns], 
                font=dict(size=12),
                align = ['left','center'],
                #fill_color = colourcode,
                line_color = 'rgba(255,255,255,0.2)',
                height=20))],)
        "Nombre de consultation par département"
        fig.update_layout(
        width=1400,
        height=450,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
            )
        )
        st.plotly_chart(fig,)



        "Pie chart by custom feature"
        s1, s2, s3, s4 = st.columns((1,1,1,1))
        feature = s1.selectbox('Choisir caractéristique', ['rdv_internet', 'age_bin', 'motif_du_rdv', 'duree_du_rdv', 'civilite', 'nouveau_patient',] , help = 'Choisie la caractéristique à Analyser')
        DF_filter2 = s2.selectbox('Choisir ostéo ', df['agenda'].drop_duplicates().to_list() , help = 'Filtrer les données pour un ou tous les ostéos')
        df_data = df[df['agenda']==DF_filter]
        
        fig = px.pie(df_data.sort_values(feature), values='rdv_compte', names= feature, title = feature)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig,)