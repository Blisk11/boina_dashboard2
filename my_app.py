import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import numpy as np
from datetime import datetime, date
from math import floor
import seaborn as sns
import matplotlib as plt
import plotly.express as px
from PIL import Image
from pathlib import Path
import openpyxl


# streamlit options
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title='boina dashboard', layout = 'wide', initial_sidebar_state = 'auto')


hide_streamlit_style = """<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
p = Path(__file__).with_name('LOGO LMDO petit.jpeg')
filename = p.absolute()
#t1.title(filename)
#/app/boina_dashboard2/LOGO LMDO petit.jpeg
logo = Image.open(filename)
st.image(logo)

pwd1, pwd2= st.columns((1,1))
pwd1 = st.text_input("Password:", value="")

if pwd1!= 'fractaldefou':
    st.title('Please enter correct password')
else:
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    with st.spinner('Mise à jour des informations, un instant SVP.'):
#t1, t2 = st.columns((0.25,1)) 
        path = "/Oisif-Pro/operation/DATA/dashboard_data";
        df_list = []
        r = requests.request('PROPFIND', url+path, data=None, auth=auth);
        data = ET.fromstring(r.text);
        list = [el[0].text for el in data];
        for i in list:
            if 'Maison_OSTEOPATHIE_Osteo' in i:
                path = i
                print(i)
                r = requests.request('GET', "http://"+domain+path, auth=auth)
                temp_df = pd.read_excel(r.content, )
                df_list.append(temp_df)


        st.title("Dashboard demo: La maison de l'ostéopathie")


        #df = pd.read_excel('dashboard_df.xlsx', engine='openpyxl')
        df = pd.concat(df_list)
        df = df.reset_index()
        df_copy = df.copy()

        df_copy['agenda'] = 'Tous'

        df = pd.concat([df, df_copy])
        df = df.reset_index()
        with st.spinner('Mise à jour des informations, un instant SVP.'):

            #Metrics setting and rendering
            f1, f2= st.columns((1,1))

            DF_filter = f1.selectbox('Choisir ostéo', df['agenda'].value_counts().index.to_list() , help = 'Filtrer les données pour un ou tous les ostéos (pour les 2 tableaux ci-dessous)')              

            df_data = df[(df['agenda']==DF_filter)]

            f1, f2= st.columns((1,1))        
            DF_legend = f1.selectbox('Choisir légende du tableau ci-dessous', ['nom osteo', 'rdv_internet', 'age_bin', 'motif_du_rdv', 'fiche_trouvé', 'duree_du_rdv', 'civilite', 'distance_bin', 'nbs_rdv_bin', 'nouveau_patient',] , help = 'La légende est la couleur de barre du tableau ci-dessous')              

            df_data = df[(df['agenda']==DF_filter)]        
            g1, g2 = st.columns((1,1))
            # bar chart

            groupby_df_list = list(set([DF_legend, 'year', 'month_number', 'month']))
            data = df_data.groupby(groupby_df_list)['index'].count().reset_index()
            data.sort_values(['year', 'month_number'], ascending = [True, True], inplace=True)
            #data['month'] = data['month'].astype(str).str.replace('-', '_')
            data.rename(columns = {'index':'nbs rdv'}, inplace=True)

            fig = px.bar(data, x="month", y="nbs rdv", color= DF_legend, title="Nombre de rdv par mois")   
            g1.plotly_chart(fig, use_container_width=True)

            #Metrics setting and rendering
            f11, f22, f33 = st.columns((1,1,1))

            DF_filter1 = f11.selectbox('Choisir ostéo', df['agenda'].value_counts().index.to_list() , key = 2, help = 'Filtrer les données pour un ou tous les ostéos (pour les 2 tableaux ci-dessous)')

            quarter = f22.multiselect("Choisir les trimestres", df[(df['agenda']==DF_filter1)]['trimestre'].sort_values().drop_duplicates().to_list(), df['trimestre'].sort_values().drop_duplicates().to_list(),)

            feature = f33.selectbox("Choisir caractéristique à analyser", ['rdv_internet', 'age_bin', 'motif_du_rdv', 'fiche_trouvé', 'duree_du_rdv', 'civilite', 'distance_bin', 'nbs_rdv_bin', 'nouveau_patient',] , help = "Choisir l'axe des X du tableau de gauche")


            df_data = df[(df['agenda']==DF_filter1) & (df['trimestre'].isin(quarter))]

            g22, g_empty, g33 = st.columns((1, 0.2, 1))


            # Here we use a column with categorical data
            fig = px.histogram(df_data.sort_values(feature), x=feature, color = 'nom osteo', title=feature)    
            g22.plotly_chart(fig, use_container_width=True)

            fig = px.pie(df_data.sort_values(feature), values='rdv_compte', names= feature, title = feature)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            g33.plotly_chart(fig,)

            ###
    #        "Pie chart by custom feature"
    #        s1, s2, s3, s4 = st.columns((1,1,1,1))
    #        feature = s1.selectbox('Choisir caractéristique', ['rdv_internet', 'age_bin', 'motif_du_rdv', 'fiche_trouvé', 'duree_du_rdv', 'civilite', 'distance_bin',   #'nbs_rdv_bin', 'nouveau_patient',] , help = 'Choisie la caractéristique à Analyser')
    #        DF_filter = s2.selectbox('Choisir ostéo ', df['agenda'].drop_duplicates().to_list() , help = 'Filtrer les données pour un ou tous les ostéos')
    #        df_data = df[df['agenda']==DF_filter].dropna(subset = [feature])

    #        fig = px.pie(df_data.sort_values(feature), values='rdv_compte', names= feature, title = feature)
    #        fig.update_traces(textposition='inside', textinfo='percent+label')
    #        g3.plotly_chart(fig,)
            ###

            px_table = df_data.groupby(['nom osteo', 'departement'])['rdv_compte'].sum().reset_index().sort_values('rdv_compte',ascending=False)
            px_table = px_table.pivot(index = 'departement', columns = 'nom osteo', values = 'rdv_compte')
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
