import pandas as pd
import folium
import geopandas
import requests
import streamlit as st
from streamlit_folium import st_folium
import plotly.express as px
import time
from streamlit_option_menu import option_menu
import brazilcep
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import mysql.connector
from sqlalchemy import create_engine , text
from streamlit_js_eval import streamlit_js_eval
import googlemaps

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


def get_markers_data():
    # Criação de GeoDataFrames
    geo_df = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))
    geo_df_2 = geopandas.GeoDataFrame(df_2, geometry=geopandas.points_from_xy(df_2.Longitude, df_2.Latitude))
    geo_df_UHE = geopandas.GeoDataFrame(df_UHE, geometry=geopandas.points_from_xy(df_UHE.Longitude, df_UHE.Latitude))
    geo_df_projects = geopandas.GeoDataFrame(df_projects, geometry=geopandas.points_from_xy(df_projects.Longitude, df_projects.Latitude))
    return geo_df, geo_df_2, geo_df_UHE, geo_df_projects

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
        # type_color = {"P": "black", "E": "red"}.get(df['(E)xistente/(P)otencial'][i], "purple")

        icon_html = f"""
        <div style="font-size: 18px; color: black;">
            <i class="fa-solid fa-magnifying-glass-location"></i>
        </div>
        """
        custom_icon = folium.DivIcon(html=icon_html)

        folium.Marker(
            location=coordinates,
            icon=custom_icon,
            tooltip=df['Instituicao'][i],
            popup=folium.Popup(("Instituição: "
                                + str(df['Instituicao'][i])
                                + "<br>"
                                + "Área de Pesquisa: "
                                + str(df['Area de pesquisa'][i])
                                + "<br>"
                                + "Projetos:"
                                + str(df['Projetos'][i])
                                + "<br>"
                                + "Site: <a href='" + str(df['Site'][i]) + "' target='_blank'>" + str(df['Site'][i]) + "</a>"),
                               max_width=400)
        ).add_to(fg)

        i += 1

    i = 0
    for coordinates in geo_df_list_2:
        # type_color = {"P": "black", "E": "red"}.get(df_2['(E)xistente/(P)otencial'][i], "purple")

        icon_html = f"""
        <div style="font-size: 18px; color: black;">
            <i class="fa-solid fa-industry"></i>
        </div>
        """
        custom_icon = folium.DivIcon(html=icon_html)

        folium.Marker(
            location=coordinates,
            icon=custom_icon,
            tooltip=df_2['Instituicao'][i],
            popup=folium.Popup(("Empresa: "
                                + str(df_2['Instituicao'][i])
                                + "<br>"
                                + "Setor: "
                                + str(df_2['Setor'][i])
                                + "<br>"
                                + "Consumo: "
                                + str(df_2['Consumo H2'][i])
                                + "<br>"
                                + "Site: "
                                + "Site: <a href='" + str(df_2['Site'][i]) + "' target='_blank'>" + str(df_2['Site'][i]) + "</a>"),
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
            tooltip=df_projects['Instituicao'][i],
            popup=folium.Popup(("Nome: "
                                + str(df_projects['Instituicao'][i])
                                + "<br>"
                                + "Estágio: "
                                + str(df_projects['Estágio'][i])
                                + "<br>"
                                + "Capacidade (T/ano): "
                                + str(f'{df_projects['Capacidade'][i]} T/ano')
                                + "<br>"
                                + "Finalidade:"
                                + str(df_projects['Finalidade'][i])
                                + "<br>"
                                + "Cidade:"
                                + str(df_projects['Cidade'][i])
                                + "<br>"
                                + "Site: <a href='" + str((df_projects['Site'][i]) + "' target='_blank'>" + str(df_projects['Site'][i]) + "</a>")),
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

def get_capacidade():
    df_projects['Capacidade'] = df_projects['Capacidade'].astype(int) 
    capacidade_total_operando_h2v = round((df_projects[df_projects['Finalidade'] == 'H2V']['Capacidade'].sum())/1000 , 0)
    capacidade_total_operando_nh3v = round((df_projects[df_projects['Finalidade'] == 'NH3V']['Capacidade'].sum())/1000 , 0)
    capacidade_total_estados = df_projects.groupby(['Estado','Estágio'])['Capacidade'].sum().reset_index().sort_values(by = 'Capacidade')
    capacidade_total_estados['Capacidade'] = capacidade_total_estados['Capacidade'] / 1000
    porcentagem_capacidade_projeto_h2v = df_projects[(df_projects['Capacidade'] != 0) & (df_projects['Finalidade'] == 'H2V')]
    porcentagem_capacidade_projeto_nh3v = df_projects[(df_projects['Capacidade'] != 0) & (df_projects['Finalidade'] == 'NH3V')]


    return capacidade_total_operando_h2v,capacidade_total_operando_nh3v,capacidade_total_estados,porcentagem_capacidade_projeto_h2v,porcentagem_capacidade_projeto_nh3v

@st.cache_resource
def get_db_connection():
    username = 'Matheus'
    password = 'mineiro01'
    host = 'database-1.c9i6ismmcgj9.sa-east-1.rds.amazonaws.com'
    port = '3306'
    database = 'database_1'
    
    connection_string = f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}'
    engine = create_engine(connection_string)
    
    return engine

def fetch_data(_engine):
    query_df = "SELECT * FROM DADOS_UNIVERSIDADES_E_CENTROS_PED"
    query_df_2 = "SELECT * FROM DADOS_CONSUMIDORES"
    query_df_projects = "SELECT * FROM DADOS_PROJETOS"

    df = pd.read_sql(query_df, engine)
    df_2 = pd.read_sql(query_df_2, engine)
    df_projects = pd.read_sql(query_df_projects, engine)

    return df,df_2,df_projects

def insert_data_to_db_projects(rua,cidade,estado,num,bairro,finalidade,estagio,capacidade,latitude,longitude,engine):
    with engine.connect() as conn:  # Usar 'with' para garantir que a conexão será fechada automaticamente
        sql = """
        INSERT INTO DADOS_PROJETOS
        (`Instituicao`, `CEP`, `Numero`, `Estado`, `Rua`, `Bairro`, `Cidade`, `Finalidade`, `Estágio`, `Tecnologia`, `Capacidade`,`Quantidade_plantas`,`Demais_areas`,`Expectativa_crescimento`,`Setor`,`Site`, `Latitude`, `Longitude`)
        VALUES 
        (:Instituição, :CEP, :Numero, :Estado, :Rua, :Bairro, :Cidade, :Finalidade, :Estágio, :Tecnologia, :Capacidade,:Quantidade_plantas,:Demais_areas,:Expectativa_crescimento,:Setor,:Site ,:Latitude, :Longitude)
        """
        
        # Usando dicionário para passar parâmetros nomeados para a query
        params = {
            'Instituição': nome_instituicao,
            'CEP': cep,
            'Numero': num,
            'Estado': estado,
            'Rua': rua,
            'Bairro': bairro,
            'Cidade': cidade,
            'Finalidade': finalidade,
            'Estágio': estagio,
            'Tecnologia': tecnologia,
            'Capacidade': capacidade,
            'Quantidade_plantas': qntd_plantas,
            'Demais_areas': demais_areas,
            'Expectativa_crescimento': expectativa_crescimento,
            'Setor': setor,
            'Site': site,
            'Latitude': latitude,
            'Longitude': longitude
        }
        
        conn.execute(text(sql), params)  # Passando os parâmetros como dicionário
        conn.connection.commit()

def insert_data_to_db_consumidor(rua,cidade,estado,num,bairro,setor,site_empresa,consumo,latitude,longitude,engine):
    with engine.connect() as conn:  # Usar 'with' para garantir que a conexão será fechada automaticamente
        sql = """
        INSERT INTO DADOS_CONSUMIDORES
        (`Instituicao`, `CEP`, `Numero`, `Estado`, `Rua`, `Bairro`, `Cidade`, `Setor`, `Consumo H2`, `Site`,`Numero_plantas`,`Custo_anual`,`Considera_produzir`, `Latitude`, `Longitude`)
        VALUES 
        (:Instituição, :CEP, :Numero, :Estado, :Rua, :Bairro, :Cidade, :Setor, :Consumo_H2, :Site,:Numero_plantas,:Custo_anual,:Considera_produzir, :Latitude, :Longitude)
        """
        
        # Usando dicionário para passar parâmetros nomeados para a query
        params = {
            'Instituição': nome_instituicao,
            'CEP': cep,
            'Numero': num,
            'Estado': estado,
            'Rua': rua,
            'Bairro': bairro,
            'Cidade': cidade,
            'Setor': setor,
            'Consumo_H2': consumo,
            'Site': site_empresa,
            'Numero_plantas': numero_plantas,
            'Custo_anual': custo_anual,
            'Considera_produzir': considera_produzir,
            'Latitude': latitude,
            'Longitude': longitude
        }

        conn.execute(text(sql), params)  # Passando os parâmetros como dicionário
        conn.connection.commit()

def insert_data_to_db_pesquisa(rua,cidade,estado,num,bairro,area_pesquisa,site,projetos,latitude,longitude,engine):
    with engine.connect() as conn:  # Usar 'with' para garantir que a conexão será fechada automaticamente
        sql = """
        INSERT INTO DADOS_UNIVERSIDADES_E_CENTROS_PED
        (`Instituicao`, `CEP`, `Numero`, `Estado`, `Rua`, `Bairro`, `Cidade`, `Area de pesquisa`, `Projetos`, `Site`,`Quantidade_grupos`,`Quantidade_realizados`, `Latitude`, `Longitude`)
        VALUES 
        (:Instituição, :CEP, :Numero, :Estado, :Rua, :Bairro, :Cidade, :Area, :Projetos, :Site, :Quantidade_grupos, :Quantidade_realizados, :Latitude, :Longitude)
        """
        
        # Usando dicionário para passar parâmetros nomeados para a query
        params = {
            'Instituição': nome_instituicao,
            'CEP': cep,
            'Numero': num,
            'Estado': estado,
            'Rua': rua,
            'Bairro': bairro,
            'Cidade': cidade,
            'Area': area_pesquisa,
            'Projetos': projetos,
            'Site': site,
            'Quantidade_grupos': qntd_grupos,
            'Quantidade_realizados': qntd_realizados,
            'Latitude': latitude,
            'Longitude': longitude
        }
        
        conn.execute(text(sql), params)  # Passando os parâmetros como dicionário
        conn.connection.commit()

engine = get_db_connection()

df,df_2,df_projects = fetch_data(engine)

# df = load_data_from_excel("DADOS_UNIVERSIDADES_E_CENTROS_PED.xlsx")

# df_2 = load_data_from_excel("DADOS_CONSUMIDORES.xlsx")

df_3 = load_data_from_csv('siga.csv')

gmaps = googlemaps.Client(key='AIzaSyCGStXTdz-TMMAJS17Zu25LF7LYDoZcFeo')

# df_projects = load_data_from_excel('DADOS_PROJETOS_V2.xlsx')

df_UHE = df_3.rename(columns={'NumCoordNEmpreendimento':'Latitude', 'NumCoordEEmpreendimento':'Longitude'})
df_UHE = df_UHE[(df_UHE['SigTipoGeracao'] == 'UHE') & (df_3['DscFaseUsina'] == 'Operação')]
df_UHE.reset_index(drop=True,inplace=True)
df_UHE['Latitude'] = df_UHE['Latitude'].astype(str).str.replace(',', '.').astype(float)
df_UHE['Longitude'] = df_UHE['Longitude'].astype(str).str.replace(',', '.').astype(float)
df_UHE.info()

geo_df, geo_df_2, geo_df_UHE, geo_df_projects = get_markers_data()

geo_df_list, geo_df_list_2, geo_df_list_UHE,geo_df_list_projects, geo_json_data  = get_map_data()

map = create_map(geo_df_list, geo_df_list_2, geo_df_list_UHE,geo_df_list_projects,geo_json_data)
capacidade_total_operando_h2v,capacidade_total_operando_nh3v,capacidade_total_estados,porcentagem_capacidade_projeto_h2v,porcentagem_capacidade_projeto_nh3v = get_capacidade()

with st.sidebar:
    selected = option_menu(
            "Menu",
            [
                "DASHBOARD H2V BRASIL",
                "FORMULÁRIO CAPTAÇÃO DE DADOS"
            ],
            icons=[ "list-task","list-task"],
            menu_icon="list",
            default_index=0,
            orientation="vertical"
        )
    
if selected == "DASHBOARD H2V BRASIL":
    st.markdown('<h1 style="font-size:40px;">Análise do Potencial de Produção do H2V no Brasil</h1>', unsafe_allow_html=True)

    col1,col2,col5 = st.columns([0.33,0.33,0.33],gap='small')
    with col1:
        st.metric('Potencial Total de produção de H2V', f'{capacidade_total_operando_h2v} KT/ano'.replace(',', 'X').replace('.', ',').replace('X', '.'))

        with st.container(height= 350):
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
            st.metric('Potencial Total de produção de NH3V', f'{capacidade_total_operando_nh3v} KT/ano'.replace(',', 'X').replace('.', ',').replace('X', '.'))

            fig = px.bar(capacidade_total_estados, x = 'Estado',y = 'Capacidade',text_auto='.2s',color = 'Estágio',color_discrete_sequence=['#1e4a20','#42f54b'], title='Capacidade de Produção Por Estado (KT/ano)',height=400)
            fig.update_layout(xaxis_title ='',title_yref='container',title_xanchor='center',title_x=0.5,title_y=0.95,legend=dict(orientation='h',yanchor='top',y=-0.1,xanchor='center',x=0.3,font=dict(size=14)),font=dict(size=18),title_font=dict(size=20))    
            st.plotly_chart(fig,use_container_width=True)
    with col5:
            target_state = st.selectbox('Estado', df_2['Estado'].sort_values().unique(),index=0,placeholder=('Escolha uma opção'))
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
        fig3 = px.pie(porcentagem_capacidade_projeto_h2v, names = 'Instituicao', values='Capacidade', title='Projetos de H2V',color_discrete_sequence=px.colors.sequential.Greens,hole=.3,height= 500)
        fig3.update_layout(title_yref='container',title_xanchor='center',title_x=0.5,title_y=0.95,legend=dict(orientation='h',yanchor='top',y=-0.1,xanchor='center',x=0.3,font=dict(size=14)),font=dict(size=16),title_font=dict(size=20))    
        fig3.update_traces(showlegend=False,textinfo='label+percent',marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig3,use_container_width=True)
    with col4:
        fig4 = px.pie(porcentagem_capacidade_projeto_nh3v, names = 'Instituicao', values='Capacidade', title='Projetos de NH3V',color_discrete_sequence=px.colors.sequential.YlOrBr,hole=.3,height= 500)
        fig4.update_layout(title_yref='container',title_xanchor='center',title_x=0.5,title_y=0.95,legend=dict(orientation='h',yanchor='top',y=-0.1,xanchor='center',x=0.3,font=dict(size=14)),font=dict(size=16),title_font=dict(size=20))    
        fig4.update_traces(showlegend=False,textinfo='label+percent',marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig4,use_container_width=True)

if selected =="FORMULÁRIO CAPTAÇÃO DE DADOS":
    st.markdown('<h1 style="font-size:40px;">Formulario Geral</h>', unsafe_allow_html=True)
    with st.form('my_form_1'):
        col1, col2 = st.columns([0.5,0.5])
        with col1:
            nome_instituicao = st.text_input('Nome da Instituição ou Empresa') 
        with col2:
            area = st.selectbox('Selecione a área de atuação', ['Consumo', 'Produção', 'Pesquisa'], index=None)  
        col3, col4,col18 = st.columns(3)
        with col3:
            cep = st.text_input('CEP (XXXXX-XXX)')
            cep_sem_hifen = cep.replace("-","")
        with col4:
            num = st.text_input('Número do Local')

        col15,col16,col17 = st.columns(3)
    
        with col15:
            rua = st.text_input('Rua')
        with col16:
            bairro = st.text_input('Bairro')
        with col17:
            cidade = st.text_input('Cidade')
        with col18:
            estado = st.text_input('Estado (Ex: MG, SP, DF e etc)')
        endereco = rua + ',' + num + ',' + bairro + ',' + cidade + ',' + estado

        if 'latitude' not in st.session_state:
            st.session_state['latitude'] = None
        if 'longitude' not in st.session_state:
            st.session_state['longitude'] = None

        submitted_1 = st.form_submit_button("Carregue o Formulário Específico")
        if submitted_1:
            # Validate if all required fields are filled
            if rua and num and bairro and cidade and estado:
                try:
                    # Make the API call
                    location = gmaps.geocode(endereco)

                    # Check if the API returned any results
                    if location:
                        first_result = location[0]
                        geometry = first_result.get('geometry', {})
                        location_coords = geometry.get('location', {})
                        latitude = location_coords.get('lat')
                        longitude = location_coords.get('lng')
                        latitude = str(latitude) if latitude is not None else None
                        longitude = str(longitude) if longitude is not None else None

                        st.session_state['latitude'] = latitude
                        st.session_state['longitude'] = longitude

                        # Display the results
                        st.success("Endereço encontrado!")
                        st.write(f"Latitude: {latitude}")
                        st.write(f"Longitude: {longitude}")
                    else:
                        st.error("Nenhum resultado encontrado para o endereço fornecido.")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao buscar o endereço: {e}")
            else:
                st.warning("Por favor, preencha todos os campos do endereço.")

    
    st.markdown('<h1 style="font-size:40px;">Formulario Específico</h1>',unsafe_allow_html=True)
    if area == 'Consumo':
        with st.form('my_form_2'):
            col11,col12 = st.columns(2)
            with col11:
                setor = st.selectbox('Qual o setor em que sua empresa atua?', ['Óleo e Gás','Geração de Energia', 'Alimentos e Bebidas', 'Fertilizantes', 'Siderúrgico', 'Químico/Petroquímico', 'Outro'],index=None)

            with col12:
                site_empresa = st.text_input('Site da Empresa')
            col13,col14 = st.columns(2)
            with col13:
               consumo = st.number_input('Consumo médio de H2 por ano (T/ano)', step=100)
            with col14:
                numero_plantas = st.number_input('Sua empresa está operando em quantas plantas com consumo de H2?', step=1)
            colc1,colc2 = st.columns(2)
            with colc1:
                custo_anual = st.number_input('Qual o custo anual da sua empresa com hidrogênio?', step=1000)
            with colc2:
                considera_produzir = st.selectbox('Sua empresa considera a produção própria de hidrogênio baseado em fontes renováveis?', ['Não há planos de uma produção própria de hidrogênio', 'Sim, memso que o custo para redução da carga de CO2 seja mais elevado','Sim, com incentivos do governo', 'Sim, caso seja economicamente viável'], index=None)

            submitted_2 = st.form_submit_button("Envia Formulário Completo")
            if submitted_2:
                latitude = st.session_state.get('latitude')
                longitude = st.session_state.get('longitude')

                print(f"Latitude final: {latitude} (Tipo: {type(latitude)})")
                print(f"Longitude final: {longitude} (Tipo: {type(longitude)})")
                insert_data_to_db_consumidor(rua,cidade,estado,num,bairro,setor,site_empresa,consumo,latitude,longitude,engine)
                st.success("Formulário Registrado")
                st.write(f"Latitude antes do insert: {latitude}, Longitude antes do insert: {longitude}")
                streamlit_js_eval(js_expressions="parent.window.location.reload()")

    if area == 'Produção':
        with st.form('my_form_3', enter_to_submit=False):
            col5,col6 = st.columns(2)
            with col5:
                finalidade = st.selectbox('Selecione a finalidade', ['H2V', 'NH3V'])
            with col6:
                estagio = st.text_input('Estágio da operação (Por exemplo P&D, MoU ou Operando)')
            col7,col8 = st.columns(2)
            with col7:
                tecnologia = st.selectbox('Tecnologia utilizada', ['PEM', 'Eletrólise Alcalina'], index=None)
            with col8:
                capacidade = st.number_input('Capacidade de Produção esperada ou em operação (T/ano)', step=100)
            colp1,colp2 = st.columns(2)
            with colp1:
                qntd_plantas = st.number_input('Quantas plantas de produção sua empresa está operando?', step=1)
            with colp2:
                demais_areas = st.selectbox('Além da produção de hidrogênio, em quais outras áreas sua empresa atua?', ['Prestação de Serviços','Fornecimento de Tecnologia para H2','Consumo de H2','Armazenamento e Distribuição de H2'],index=None)
            colp3,colp4 = st.columns(2)
            with colp3:
                expectativa_crescimento = st.selectbox('Qual a expectativa de crescimento do faturamento com a venda de hidrogênio verde até 2030?', ['Não está em nossos planos', '>50%', '25%-50%', "10%-25%", '10%-25%', '0-10%'],index=None)
            with colp4:
                setor = st.selectbox('Qual o setor em que sua empresa atua?', ['Óleo e Gás','Geração de Energia', 'Alimentos e Bebidas', 'Fertilizantes', 'Siderúrgico', 'Químico/Petroquímico', 'Outro'],index=None)
            
            site = st.text_input('Site')
            
            submitted_3 = st.form_submit_button("Envia Formulário Completo")
            if submitted_3:
                latitude = st.session_state.get('latitude')
                longitude = st.session_state.get('longitude')

                insert_data_to_db_projects(rua,cidade,estado,num,bairro,finalidade,estagio,capacidade,latitude,longitude,engine)
                st.success("Formulário Registrado")
                streamlit_js_eval(js_expressions="parent.window.location.reload()")

    if area == 'Pesquisa':
        with st.form('my_form_4', enter_to_submit=False):
            col9,col10 = st.columns(2)
            with col9:
                area_pesquisa = st.multiselect('Área de Pesquisa (Selecione todas as que se aplicam)',['Equipamentos Industriais', 'Fertilizantes','Cimento','Alimentos e Bebidas','Siderúrgico','Usina de álcool e açucar', 'Química', 'Geração de Eletricidade', 'Construtoras', 'Mineradoras', 'Gás e Petróleo', 'Transporte e Mobilidade', 'Outros'])
                area_pesquisa = ", ".join(area_pesquisa)

            with col10:
                site = st.text_input('Site da Instituição')

            cold11,cold12 = st.columns(2)
            with cold11:
                qntd_grupos = st.number_input('Atualmente, quantos grupos de pesquisa na área de hidrogênio a isntituição possui?', step=1)
            with cold12:
                qntd_realizados = st.number_input('Quantos projetos na área de hidrogênio já foram realziados pela instituição?', step=1)

            projetos = st.text_area('Quais foram esses projetos realziados pela instituição?') 

            submitted_4 = st.form_submit_button("Envia Formulário Completo")
            if submitted_4:
                latitude = st.session_state.get('latitude')
                longitude = st.session_state.get('longitude')

                insert_data_to_db_pesquisa(rua,cidade,estado,num,bairro,area_pesquisa,site,projetos,latitude,longitude,engine)
                st.success("Formulário Registrado")
                streamlit_js_eval(js_expressions="parent.window.location.reload()")


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