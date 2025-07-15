import streamlit as st
from opcua import Client
import pandas as pd
import time

# Configuração da página com loyout wide para melhor visualização
st.set_page_config(
    page_title="Dashboard OPC UA",
    layout="wide"
)
st.title("Dashboard OPC UA")

# Estado da sessão
if 'client' not in st.session_state:
    st.session_state.client = None
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'nodes' not in st.session_state:
    st.session_state.nodes = []
if 'charts' not in st.session_state:
    st.session_state.charts = {}

# Sidebar: conexão
st.sidebar.header("Conexão OPC UA")
url = st.sidebar.text_input("URL do Servidor OPC UA", value="opc.tcp://192.168.1.5:5352") #valor definido como exemplo
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Conectar"):
        try:
            client = Client(url)
            client.connect()
            st.session_state.client = client
            st.session_state.connected = True
            # Descobrir variáveis em 'simulation', onde estão os dados para esse exemplo
            root = client.get_objects_node()
            for child in root.get_children():
                if child.get_browse_name().Name.lower() == "simulation":
                    st.session_state.nodes = [n for n in child.get_children() if n.get_node_class().name == "Variable"]
                    break
            st.sidebar.success("Conectado com sucesso!")
        except Exception as e:
            st.sidebar.error(f"Erro ao conectar: {e}")
with col2:
    #Caso o usuário queira desconectar
    if st.button("Desconectar"):
        if st.session_state.client:
            st.session_state.client.disconnect()
        st.session_state.client = None
        st.session_state.connected = False
        st.session_state.nodes = []
        st.session_state.charts = {}
        st.sidebar.info("Desconectado.")

# Se conectado e ainda não inicializou charts, cria layout
if st.session_state.connected and st.session_state.nodes and not st.session_state.charts:
    st.markdown("---")
    st.header("📊 Variáveis em Tempo Real")
    names = [n.get_display_name().Text for n in st.session_state.nodes]
    # Cria placeholders em grid 2 col com iteração sobre as variaveis
    for i, name in enumerate(names):
        #caso seja par o gráfico será colocado na primeira coluna, caso seja ímpar na segunda
        if i % 2 == 0:
            cols = st.columns(2)
        placeholder = cols[i % 2].empty()
        # Inicializa chart com dados vazios
        st.session_state.charts[name] = placeholder.line_chart(pd.DataFrame({name: []}))

# Loop de atualização dos charts
if st.session_state.connected and st.session_state.nodes:
    try:
        while st.session_state.connected:
            # Coleta valor atual de cada variável
            update = {}
            for node in st.session_state.nodes:
                name = node.get_display_name().Text
                try:
                    value = node.get_value()
                except:
                    value = None
                update[name] = value
            # Atualiza cada gráfico em-place com novo ponto
            for name, chart in st.session_state.charts.items():
                # chart.add_rows requer uma lista ou DataFrame
                chart.add_rows(pd.DataFrame({name: [update[name]]}))
            time.sleep(1)
    except Exception as e:
        st.error(f"Erro durante atualização: {e}")
else:
    if not st.session_state.connected:
        st.info("Clique em 'Conectar' para iniciar a leitura das variáveis.")
