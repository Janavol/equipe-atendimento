import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .gray-dark {
            background-color: #2e2e2e;
            color: white;
            padding: 10px;
            border-radius: 10px;
        }
        .gray-light {
            background-color: #d3d3d3;
            color: black;
            padding: 10px;
            border-radius: 10px;
        }
        input {
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Armazena dados na sessão por mês e ano
if "dados_colaboradoras" not in st.session_state:
    st.session_state.dados_colaboradoras = {}

# Seleção de ano e mês
col1, col2 = st.columns(2)
with col1:
    ano = st.selectbox("Selecione o ano:", [2025, 2026], key="ano")
with col2:
    mes = st.selectbox("Selecione o mês:", list(range(1, 13)), format_func=lambda m: datetime(2025, m, 1).strftime("%B"), key="mes")

chave = f"{ano}-{mes}"

# Inicializar dados do mês se não existir
if chave not in st.session_state.dados_colaboradoras:
    st.session_state.dados_colaboradoras[chave] = []

st.title("Painel de Desempenho da Equipe")

col_esquerda, col_direita = st.columns([2, 3])

with col_esquerda:
    st.header("Cadastro de Dados")
    for i in range(1, 26):
        estilo = "gray-dark" if i % 2 != 0 else "gray-light"
        with st.container():
            st.markdown(f'<div class="{estilo}">', unsafe_allow_html=True)
            nome = st.text_input(f"Colaborador {i} - Nome", key=f"nome_{i}")
            atendimentos = st.number_input("Nº de atendimentos", min_value=0, key=f"atend_{i}")
            tempo = st.text_input("Tempo médio de atendimento (mm:ss)", value="00:00", key=f"tempo_{i}")
            erros = st.number_input("Quantidade de erros", min_value=0, key=f"erros_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Salvar dados do período"):
        registros = []
        for i in range(1, 26):
            nome = st.session_state.get(f"nome_{i}", "")
            if nome.strip() == "":
                continue
            atendimentos = st.session_state.get(f"atend_{i}", 0)
            tempo_txt = st.session_state.get(f"tempo_{i}", "00:00")
            try:
                minutos, segundos = map(int, tempo_txt.strip().split(":"))
                tempo_total = minutos + segundos / 60
            except:
                tempo_total = 0
            erros = st.session_state.get(f"erros_{i}", 0)
            registros.append({
                "Nome": nome,
                "Atendimentos": atendimentos,
                "Tempo Médio (min)": tempo_total,
                "Erros": erros
            })
        st.session_state.dados_colaboradoras[chave] = registros
        st.success("Dados salvos com sucesso!")

with col_direita:
    st.header("Radar de Performance")
    dados = st.session_state.dados_colaboradoras.get(chave, [])
    for registro in dados:
        nome = registro["Nome"]
        atendimentos = registro["Atendimentos"]
        tempo = registro["Tempo Médio (min)"]
        erros = registro["Erros"]

        if atendimentos == 0:
            produtividade = 0
        else:
            produtividade = min(atendimentos / 100, 1) * 100

        eficiencia = max(0, 100 - tempo * 10)
        qualidade = max(0, 100 - erros * 20)

        performance = (produtividade + eficiencia + qualidade) / 3

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[produtividade, eficiencia, qualidade, produtividade],
            theta=["Produtividade", "Eficiência", "Qualidade", "Produtividade"],
            fill='toself',
            name=nome
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            title=f"Desempenho de {nome}"
        )
        st.plotly_chart(fig, use_container_width=True)
