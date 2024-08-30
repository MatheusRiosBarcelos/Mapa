import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import xml.etree.ElementTree as ET
from io import StringIO
from datetime import datetime
import plotly.graph_objects as go
import base64

def update_svg(svg_path, data):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Namespace encontrado no SVG
    namespace = {'ns0': 'http://www.w3.org/2000/svg'}
    
    # Mapeamento de cores para os status
    color_map = {'running': '#3ACC55', 'stopped': '#FC1010'}
    
    for machine in data.itertuples():
        try:
            # Verifica o status e o ID
            status = machine.status
            if status not in color_map:
                st.write(f"Status '{status}' não encontrado no color_map")
                continue
            
            # Ajuste para considerar o namespace `ns0`
            element = root.find(f".//*[@id='{machine.estacao}']", namespace)
            
            if element is not None:
                # Alterar a cor da máquina de acordo com o status
                element.set('{http://www.w3.org/2000/svg}fill', color_map[status])
            else:
                st.write(f"Elemento com ID '{machine.estacao}' não encontrado no SVG")
        
        except Exception as e:
            st.write(f"Erro ao processar máquina {machine.estacao}: {e}")
    
    svg_data = StringIO()
    tree.write(svg_data, encoding='unicode')
    
    return svg_data.getvalue()

def format_timedelta(td):
    if pd.isna(td):
        return pd.NA

    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'

def render_svg(svg_file):

    with open(svg_file, "r") as f:
        lines = f.readlines()
        svg = "".join(lines)

        """Renders the given svg string."""
        b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
        return html

username = 'usinag87_matheus'
password = '%40Elohim32'
host = 'usinagemelohim.com.br'
port = '3306'
database = 'usinag87_controleprod'

connection_string = f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}'

engine = create_engine(connection_string)

query_ordens = "SELECT * FROM ordens"
query_pedidos = "SELECT * FROM pedidos"
ordens = pd.read_sql(query_ordens, engine)
pedidos = pd.read_sql(query_pedidos,engine)

st.set_page_config(layout="wide") 
colA, colB = st.columns([0.8,0.2])
with colA:
    st.image('logo.png', width= 150)

ordens = ordens[ordens['estacao'] != 'Selecione...']
ordens.dropna(subset=['ordem', 'data_ini', 'hora_ini'], inplace=True)
ordens = ordens[ordens['estacao'] == 'SRC 001']
ordens = ordens[ordens['status'] == 1]

ordens['hora_ini'] = ordens['hora_ini'].apply(format_timedelta)
ordens['hora_fim'] = ordens['hora_fim'].apply(format_timedelta)

ordens['Datetime_ini'] = pd.to_datetime(ordens['data_ini'].astype(str) + ' ' + ordens['hora_ini'], errors='coerce')
ordens['Datetime_fim'] = pd.to_datetime(ordens['data_fim'].astype(str) + ' ' + ordens['hora_fim'], errors='coerce')

ordens["data_ini"] = pd.to_datetime(ordens["data_ini"], errors='coerce')
ordens["data_fim"] = pd.to_datetime(ordens["data_fim"], errors='coerce')
now = datetime.now()
ordens = ordens[(ordens['Datetime_ini'].dt.day == now.day) & (ordens['Datetime_ini'].dt.month == now.month)]
ordens = ordens.drop_duplicates(subset='estacao',keep='last')
ordens['status'] = ordens.apply(lambda row: 'running' if row['status'] == 1 else 'stopped', axis=1)
print(ordens)
svg_content = update_svg('Group 1.svg', ordens)

svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
data_url = f'data:image/svg+xml;base64,{svg_base64}'

st.markdown(f'<img src="{data_url}" width="100%" />', unsafe_allow_html=True)
st.markdown(svg_content, unsafe_allow_html=True)

