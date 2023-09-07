import streamlit as st
import streamlit.components.v1 as components
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
import seaborn as sns
import matplotlib as plt
import xml.etree.ElementTree as ET
import requests
import json

# streamlit options
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title='boina dashboard', layout = 'wide', initial_sidebar_state = 'auto')


hide_streamlit_style = """<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(
    """
<style>
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   
   overflow-wrap: break-word;
   white-space: break-spaces;
}
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div p {
   font-size: 200% !important;
}

</style>
""",
    unsafe_allow_html=True,
)
css='''
[data-testid="metric-container"] {
    width: fit-content;
    margin: auto;
    padding: 90px 0px;
    
}

[data-testid="metric-container"] > div {
    width: fit-content;
    margin: auto;
    font-size: 35px;
}

[data-testid="metric-container"] label {
    width: fit-content;
    margin: auto;
    font-size: 20px;
}
'''

p = Path(__file__).with_name('LOGO LMDO petit.jpeg')
filename = p.absolute()
#t1.title(filename)
#/app/boina_dashboard2/LOGO LMDO petit.jpeg
logo = Image.open(filename)
st.image(logo)

domain = "cloud.leviia.com";
auth=('boina-oisif_pro', 'Heokepide01!'); # admin user
url = "http://"+domain+"/remote.php/dav/files/"+auth[0];
headers = {"OCS-APIRequest": "true"}

def ColourWidgetText(wgt_txt, wch_colour = '#000000'):
    htmlstr = """<script>var elements = window.parent.document.querySelectorAll('*'), i;
                    for (i = 0; i < elements.length; ++i) { if (elements[i].innerText == |wgt_txt|) 
                        elements[i].style.color = ' """ + wch_colour + """ '; } </script>  """

    htmlstr = htmlstr.replace('|wgt_txt|', "'" + wgt_txt + "'")
    components.html(f"{htmlstr}", height=0, width=0)

def create_card(st, label, value1, value2):
    if value1 > 0:
        kpi_color = '#65AC4C' # green
        display_value1 = '+ ' + str(value1) + ' RDV'
    else:
        kpi_color = '#FF0000' #red
        display_value1 = str(value1) + ' RDV'
        
    return st.metric(label, display_value1, "{:.1%}".format(value2)) , ColourWidgetText(display_value1, kpi_color)




category_list = ['nom osteo', 'rdv_internet', 'age_bin', 'motif_du_rdv', 'fiche_trouvé', 'duree_du_rdv', 'civilite', 'distance_bin', 'nbs_rdv_bin', 'nouveau_patient', 'comment_avezvous_retrouve_notre_fiche_', ]

pwd1, pwd2= st.columns((1,1))
pwd = pwd1.text_input("Password:", value="")

if pwd!= 'fractaldefou':
    st.title('Entrer votre mot de passe SVP')
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


        st.title("Dashboard: La maison de l'ostéopathie")


        #df = pd.read_excel('dashboard_df.xlsx', engine='openpyxl')
        df = pd.concat(df_list)
        df = df.reset_index()
        df_copy = df.copy()

        df_copy['osteo'] = 'Tous'

        df = pd.concat([df, df_copy])
        df = df.reset_index()
        df['year_month'] = df['year'].astype(str) + '-' + df['month_number'].apply(lambda x: '{:02d}'.format(x))
        df['day_number'] = df['date_de_debut'].dt.day

        max_month_number = int(df['year_month'].max()[-2:])
        max_day_number = df[df['year_month']==df['year_month'].max()]['day_number'].max()
        previous_year = int(df['year_month'].max()[:4]) - 1

        previous_month = df['year_month'].drop_duplicates().sort_values().to_list()[-2]

        previous_year_max_date = str(previous_year) + '-' + str(max_month_number) + '-' + str(max_day_number)

        with st.spinner('Mise à jour des informations, un instant SVP.'):

            #Metrics setting and rendering
            f1, f2= st.columns((1,1))
            DF_filter = f1.selectbox('Choisir ostéo', df['osteo'].value_counts().index.to_list() , help = 'Filtrer les données pour un ou tous les ostéos (pour les 2 tableaux ci-dessous)')         
            df_data = df[(df['osteo']==DF_filter)]
            
            f1, f2= st.columns((1,1))         
            DF_legend = f1.selectbox('Choisir légende du tableau ci-dessous', category_list , help = 'La légende est la couleur de barre du tableau ci-dessous')              

            df_data = df[(df['osteo']==DF_filter)]
            KPI_vs_previous_month = df_data[df_data['year_month']==df_data['year_month'].max()]['rdv_compte'].sum() - df_data[(df_data['year_month']== previous_month) & (df_data['day_number']<=max_day_number)]['rdv_compte'].sum()
            KPI_vs_previous_month_perc = KPI_vs_previous_month / df_data[(df_data['year_month']== previous_month) & (df_data['day_number']<=max_day_number)]['rdv_compte'].sum()

            KPI_vs_previous_year =  df_data[df_data['year']==df_data['year'].max()]['rdv_compte'].sum() - df_data[(df_data['year']==previous_year) & (df['date_de_debut']<= previous_year_max_date)]['rdv_compte'].sum()
            KPI_vs_previous_year_perc = KPI_vs_previous_year / df_data[(df_data['year']==previous_year) & (df['date_de_debut']<= previous_year_max_date)]['rdv_compte'].sum()

            g1, g2, g3 = st.columns((2, 1, 1))
            # bar chart
         
            groupby_df_list = [DF_legend, 'year_month', 'month', 'year', 'month_number']
            data = df_data.groupby(groupby_df_list)['index'].count().reset_index()
            data.sort_values(['year', 'month_number'], ascending = True, inplace=True)
            #data['month'] = data['month'].astype(str).str.replace('-', '_')
            data.rename(columns = {'index':'nbs rdv'}, inplace=True)

            fig = px.bar(data, x="month", y="nbs rdv", color= DF_legend, title="Nombre de rdv par mois", )
            fig.add_hline(y=200,  line_color="red")
            fig.add_hline(y=247,  line_color="blue")
            
            g1.plotly_chart(fig, use_container_width=True)
            create_card(g2, 'VS mois dernier', KPI_vs_previous_month, KPI_vs_previous_month_perc)
            create_card(g3, 'VS Année dernière', KPI_vs_previous_year, KPI_vs_previous_year_perc)
            #Metrics setting and rendering
            
            
            f11, f22, f33 = st.columns((1,1,1))

            DF_filter1 = f11.selectbox('Choisir ostéo', df['osteo'].value_counts().index.to_list() , key = 2, help = 'Filtrer les données pour un ou tous les ostéos (pour les 2 tableaux ci-dessous)')

            quarter = f22.multiselect("Choisir les trimestres", df[(df['osteo']==DF_filter1)]['trimestre'].sort_values().drop_duplicates().to_list(), df['trimestre'].sort_values().drop_duplicates().to_list(),)

            feature = f33.selectbox("Choisir caractéristique à analyser", category_list , help = "Choisir l'axe des X du tableau de gauche")


            df_data = df[(df['osteo']==DF_filter1) & (df['trimestre'].isin(quarter))]

            g22, g_empty, g33 = st.columns((1, 0.2, 1))


            # Here we use a column with categorical data
            fig = px.histogram(df_data.sort_values(feature), x=feature, color = 'osteo', title=feature)    
            g22.plotly_chart(fig, use_container_width=True)

            fig = px.pie(df_data.sort_values(feature), values='rdv_compte', names= feature, title = feature)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            g33.plotly_chart(fig,)

            ###
    #        "Pie chart by custom feature"
    #        s1, s2, s3, s4 = st.columns((1,1,1,1))
    #        feature = s1.selectbox('Choisir caractéristique', ['rdv_internet', 'age_bin', 'motif_du_rdv', 'fiche_trouvé', 'duree_du_rdv', 'civilite', 'distance_bin',   #'nbs_rdv_bin', 'nouveau_patient',] , help = 'Choisie la caractéristique à Analyser')
    #        DF_filter = s2.selectbox('Choisir ostéo ', df['osteo'].drop_duplicates().to_list() , help = 'Filtrer les données pour un ou tous les ostéos')
    #        df_data = df[df['osteo']==DF_filter].dropna(subset = [feature])

    #        fig = px.pie(df_data.sort_values(feature), values='rdv_compte', names= feature, title = feature)
    #        fig.update_traces(textposition='inside', textinfo='percent+label')
    #        g3.plotly_chart(fig,)
            ###      
        
            f1111, f2222, f3333empty = st.columns((1,1,1))
            feature1111 = f1111.selectbox("Choisir les colonnes du rangées ci-dessous", category_list )
            category_list_for_table = sorted(set(category_list) - set([feature1111]))
            feature2222 = f2222.selectbox("Choisir les colonnes", category_list_for_table,  ) 
            if feature1111 == feature2222:
                st.caption("Si vous voyez une erreur, c'est parce que la caractéristique sélectionné pour les colonnes et rangées sont la même", )

            px_table = df_data.groupby([feature1111,feature2222 ])['rdv_compte'].sum().reset_index().sort_values('rdv_compte',ascending=False)
            px_table = px_table.pivot(index = feature1111, columns = feature2222, values = 'rdv_compte')
            px_table1 = px_table.copy()
            px_table.loc["Total"] = px_table.sum()

            px_table1 = (px_table1.div(px_table1.sum(), axis=1).round(2)*100).fillna(0).astype(int).astype(str) + '%'        
            # sort columns
            px_table = px_table[px_table.sum().sort_values(ascending=False).index.to_list()].fillna(' ')
            px_table1 = px_table1[px_table1.sum().sort_values(ascending=False).index.to_list()].fillna(' ')
            #st.dataframe(px_table)
            px_table.reset_index(inplace= True)
            fig = go.Figure(
                data = [go.Table (
                    header = dict(
                    values = px_table.columns,
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
            "Nombre de consultation par " + feature1111 + ' et ' + feature2222
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

            st.caption('Les valeurs du tableau ci-haut, mais en % du total (par colonne)')
            px_table1.reset_index(inplace= True)
            fig = go.Figure(
                data = [go.Table (
                    header = dict(
                    values = px_table1.columns,
                    font=dict(size=12, color = 'white'),
                    fill_color = '#264653',
                    line_color = 'rgba(255,255,255,0.2)',
                    align = ['left','center'],
                    #text wrapping
                    height=20
                    )
                , cells = dict(
                    values = [px_table1[K].tolist() for K in px_table1.columns], 
                    font=dict(size=12),
                    align = ['left','center'],
                    #fill_color = colourcode,
                    line_color = 'rgba(255,255,255,0.2)',
                    height=20))],)
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
st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
