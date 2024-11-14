import pandas as pd
import folium
import geopandas
import requests
import streamlit as st
from streamlit_folium import st_folium
import plotly.express as px
import time

CENTER_START = [-15.7942, -47.8822]
ZOOM_START = 4  

if "center" not in st.session_state:
    st.session_state["center"] = [-15.7942, -47.8822]
if "zoom" not in st.session_state:
    st.session_state["zoom"] = 5
if "markers" not in st.session_state:
    st.session_state["markers"] = []

st.set_page_config(layout="wide")

# st.image('logo-unifei-grande.png', width=100)


@st.cache_data
def get_markers_data():
    # Criação de GeoDataFrames
    geo_df = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))
    geo_df_2 = geopandas.GeoDataFrame(df_2, geometry=geopandas.points_from_xy(df_2.Longitude, df_2.Latitude))
    geo_df_UHE = geopandas.GeoDataFrame(df_UHE, geometry=geopandas.points_from_xy(df_UHE.Longitude, df_UHE.Latitude))
    geo_df_projects = geopandas.GeoDataFrame(df_projects, geometry=geopandas.points_from_xy(df_projects.Longitude, df_projects.Latitude))
    return geo_df, geo_df_2, geo_df_UHE, geo_df_projects

@st.cache_data
def get_map_data():
    geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in geo_df.geometry]
    geo_df_list_2 = [[point.xy[1][0], point.xy[0][0]] for point in geo_df_2.geometry]
    geo_df_list_UHE = [[point.xy[1][0], point.xy[0][0]] for point in geo_df_UHE.geometry]
    geo_df_list_projects = [[point.xy[1][0], point.xy[0][0]] for point in geo_df_projects.geometry]

    url = "https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states.json"
    geo_json_data = requests.get(url).json()

    return geo_df_list, geo_df_list_2, geo_df_list_UHE,geo_df_list_projects,geo_json_data

def create_map(geo_df_list, geo_df_list_2, geo_df_list_UHE, geo_df_list_projects,geo_json_data):
    map = folium.Map(location=CENTER_START, tiles=None, zoom_start=ZOOM_START)
    folium.TileLayer(tiles='OpenStreetMap', name='Mapa',
                     attr='&copy; <a href="http://www.maptilesapi.com/">MapTiles API</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(map)

    fg = folium.FeatureGroup(name="Universidades/Centros de Pesquisa", show=False).add_to(map)
    fg3 = folium.FeatureGroup(name="Consumidores de Hidrogênio", show=False).add_to(map)
    fg_UHE = folium.FeatureGroup(name="UHEs", show=False).add_to(map)
    fg_projects = folium.FeatureGroup(name="Projetos de H2V", show=False).add_to(map)

    i = 0
    for coordinates in geo_df_list:
        type_color = {"P": "black", "E": "red"}.get(df['(E)xistente/(P)otencial'][i], "purple")

        icon_html = f"""
        <div style="font-size: 18px; color: {type_color};">
            <i class="fa-solid fa-magnifying-glass-location"></i>
        </div>
        """
        custom_icon = folium.DivIcon(html=icon_html)

        folium.Marker(
            location=coordinates,
            icon=custom_icon,
            tooltip=df['Instituição'][i],
            popup=folium.Popup(("Instituição: "
                                + str(df['Instituição'][i])
                                + "<br>"
                                + "Área de Pesquisa: "
                                + str(df['Área de Pesquisa'][i])
                                + "<br>"
                                + "Status:"
                                + str(df['(E)xistente/(P)otencial'][i])
                                + "<br>"
                                + "Site: <a href='" + str(df['Sites'][i]) + "' target='_blank'>" + str(df['Sites'][i]) + "</a>"),
                               max_width=400)
        ).add_to(fg)

        i += 1

    i = 0
    for coordinates in geo_df_list_2:
        type_color = {"P": "black", "E": "red"}.get(df_2['(E)xistente/(P)otencial'][i], "purple")

        icon_html = f"""
        <div style="font-size: 18px; color: {type_color};">
            <i class="fa-solid fa-industry"></i>
        </div>
        """
        custom_icon = folium.DivIcon(html=icon_html)

        folium.Marker(
            location=coordinates,
            icon=custom_icon,
            tooltip=df_2['Empresa'][i],
            popup=folium.Popup(("Empresa: "
                                + str(df_2['Empresa'][i])
                                + "<br>"
                                + "Setor: "
                                + str(df_2['Setor'][i])
                                + "<br>"
                                + "Site: "
                                + str(df_2['Site'][i])),
                               max_width=400)
        ).add_to(fg3)

        i += 1

    i = 0
    for coordinates in geo_df_list_projects:
        icon_html = f"""
        <div style="font-size: 22px; color: green;">
            <i class="fa-solid fa-location-dot"></i>
        </div>
        """
        custom_icon = folium.DivIcon(html=icon_html)
        folium.Marker(
            location=coordinates,
            icon=custom_icon,
            tooltip=df_projects['Nome'][i],
            popup=folium.Popup(("Nome: "
                                + str(df_projects['Nome'][i])
                                + "<br>"
                                + "Estágio: "
                                + str(df_projects['Estagio'][i])
                                + "<br>"
                                + "Capacidade (T/ano): "
                                + str(f'{df_projects['Capacidade'][i]} T/ano')
                                +"<br>"
                                +"Local:"
                                + str(df_projects['Local'][i])),
                            max_width=400)
        ).add_to(fg_projects)
        i += 1

    i = 0
    for coordinates in geo_df_list_UHE:
        icon_html = f"""
        <div style="font-size: 18px; color: blue;">
            <i class="fa-solid fa-droplet"></i>
        </div>
        """
        custom_icon = folium.DivIcon(html=icon_html)

        folium.Marker(
            location=coordinates,
            icon=custom_icon,
            tooltip=df_UHE['NomEmpreendimento'][i],
            popup=folium.Popup(("Nome Empreendimento: "
                                + str(df_UHE['NomEmpreendimento'][i])
                                + "<br>"
                                + "Tipo de Geração: "
                                + str(df_UHE['SigTipoGeracao'][i])
                                + "<br>"
                                + "Potência do Empreendimento: "
                                + str(df_UHE['MdaPotenciaFiscalizadaKw'][i])),
                               max_width=400)
        ).add_to(fg_UHE)

        i += 1

    folium.LayerControl().add_to(map)
    return map

@st.cache_data
def load_data_from_excel(file_path):
    return pd.read_excel(file_path)

@st.cache_data
def load_data_from_csv(file_path, sep=';', encoding='Windows-1252'):
    return pd.read_csv(file_path, sep=sep, encoding=encoding)

@st.cache_data
def get_capacidade():
    capacidade_total_operando = df_projects['Capacidade'].sum()
    capacidade_total_estados = df_projects.groupby(['Estado','Estagio'])['Capacidade'].sum().reset_index().sort_values(by = 'Capacidade')
    porcentagem_capacidade_projeto_h2v = df_projects[(df_projects['Capacidade'] != 0) & (df_projects['Finalidade'] == 'H2V')]
    porcentagem_capacidade_projeto_nh3v = df_projects[(df_projects['Capacidade'] != 0) & (df_projects['Finalidade'] == 'NH3V')]


    return capacidade_total_operando,capacidade_total_estados,porcentagem_capacidade_projeto_h2v,porcentagem_capacidade_projeto_nh3v

df = load_data_from_excel("DADOS_UNIVERSIDADES_E_CENTROS_PED.xlsx")

df_2 = load_data_from_excel("DADOS_CONSUMIDORES.xlsx")

df_3 = load_data_from_csv('siga.csv')

df_projects = load_data_from_excel('DADOS_PROJETOS_V2.xlsx')

df_UHE = df_3.rename(columns={'NumCoordNEmpreendimento':'Latitude', 'NumCoordEEmpreendimento':'Longitude'})
df_UHE = df_UHE[(df_UHE['SigTipoGeracao'] == 'UHE') & (df_3['DscFaseUsina'] == 'Operação')]
df_UHE.reset_index(drop=True,inplace=True)
df_UHE['Latitude'] = df_UHE['Latitude'].astype(str).str.replace(',', '.').astype(float)
df_UHE['Longitude'] = df_UHE['Longitude'].astype(str).str.replace(',', '.').astype(float)


geo_df, geo_df_2, geo_df_UHE, geo_df_projects = get_markers_data()

geo_df_list, geo_df_list_2, geo_df_list_UHE,geo_df_list_projects, geo_json_data  = get_map_data()

map = create_map(geo_df_list, geo_df_list_2, geo_df_list_UHE,geo_df_list_projects,geo_json_data)
capacidade_total_operando,capacidade_total_estados,porcentagem_capacidade_projeto_h2v,porcentagem_capacidade_projeto_nh3v = get_capacidade()

col1,col2,col5 = st.columns([0.33,0.33,0.33],gap='small')
with col1:
        
    st.markdown('<h1 style="font-size:40px;">Análise do Potencial de Produção do H2V no Brasil</h1>', unsafe_allow_html=True)
    with st.container():
         st_folium(
            map,
            center=st.session_state["center"],
            zoom=st.session_state["zoom"],
            key="new",
            height=300,
            use_container_width=True,
            returned_objects=["last_object_clicked"]
        )
with col2:

        st.metric('Potencial Total de produção de H2V', f'{capacidade_total_operando:,.0f} T/ano'.replace(',', 'X').replace('.', ',').replace('X', '.'))

        fig = px.bar(capacidade_total_estados, x = 'Estado',y = 'Capacidade',text_auto='.2s',color = 'Estagio',color_discrete_sequence=['#1e4a20','#42f54b'], title='Capacidade de Produção Por Estado',height=400)
        fig.update_layout(xaxis_title ='',title_yref='container',title_xanchor='center',title_x=0.5,title_y=0.95,legend=dict(orientation='h',yanchor='top',y=-0.1,xanchor='center',x=0.3,font=dict(size=14)),font=dict(size=18),title_font=dict(size=20))    
        st.plotly_chart(fig,use_container_width=True)
with col5:
        target_state = st.selectbox('Estado', df_2['Estado'].sort_values().unique(),index=6,placeholder=('Escolha uma opção'))
        @st.cache_data
        def get_df_2_setor():
            df_2_setor = df_2.groupby(['Setor','Estado']).size().reset_index(name='Contagem').sort_values(by='Contagem')
            return df_2_setor
        
        df_2_setor = get_df_2_setor()
        df_2_setor = df_2_setor[df_2_setor['Estado'] == target_state]

        fig2 = px.bar(df_2_setor, x = 'Setor',y = 'Contagem', text_auto='.2s',title='Principais Consumidores de Hidrogênio por Estado',color_discrete_sequence=['#42f54b'],height=400)
        fig2.update_layout(title_yref='container',title_xanchor='center',title_x=0.5,title_y=0.95,title_font=dict(size=20),font=dict(size=18))    
        st.plotly_chart(fig2,use_container_width=True)


col3,col4 = st.columns(2, gap='small')
with col3:
    fig3 = px.pie(porcentagem_capacidade_projeto_h2v, names = 'Nome', values='Capacidade', title='Projetos de H2V',color_discrete_sequence=px.colors.sequential.Greens,hole=.3,height= 500)
    fig3.update_layout(title_yref='container',title_xanchor='center',title_x=0.5,title_y=0.95,legend=dict(orientation='h',yanchor='top',y=-0.1,xanchor='center',x=0.3,font=dict(size=14)),font=dict(size=16),title_font=dict(size=20))    
    fig3.update_traces(showlegend=False,textinfo='label+percent',marker=dict(line=dict(color='#000000', width=1)))
    st.plotly_chart(fig3,use_container_width=True)
with col4:
    fig4 = px.pie(porcentagem_capacidade_projeto_nh3v, names = 'Nome', values='Capacidade', title='Projetos de NH3V',color_discrete_sequence=px.colors.sequential.YlOrBr,hole=.3,height= 500)
    fig4.update_layout(title_yref='container',title_xanchor='center',title_x=0.5,title_y=0.95,legend=dict(orientation='h',yanchor='top',y=-0.1,xanchor='center',x=0.3,font=dict(size=14)),font=dict(size=16),title_font=dict(size=20))    
    fig4.update_traces(showlegend=False,textinfo='label+percent',marker=dict(line=dict(color='#000000', width=1)))
    st.plotly_chart(fig4,use_container_width=True)

st.markdown("""
    <style>
    /* Centralizar o conteúdo dentro do label do st.metric */
    [data-testid="stMetricLabel"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Centralizar o conteúdo interno do label */
    [data-testid="stMetricLabel"] div {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }

    /* Centralizar o valor do st.metric */
    [data-testid="stMetricValue"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Centralizar o conteúdo interno do valor */
    [data-testid="stMetricValue"] div {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    /* Centralizar o valor do st.metric */
    [data-testid="stMetricDelta"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Centralizar o conteúdo interno do valor */
    [data-testid="stMetricDelta"] div {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)