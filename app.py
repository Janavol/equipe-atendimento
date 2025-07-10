import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ----- CONFIGURAÇÕES INICIAIS -----
st.set_page_config(page_title="Painel de Performance", layout="wide")
st.sidebar.title("Preenchimento de Dados")

# ----- LISTAS E VARIÁVEIS -----
colaboradoras = [f"Colab_{i}" for i in range(1, 21)]  # Até 20 colaboradoras
anos_disponiveis = list(range(2024, datetime.now().year + 1))
meses_disponiveis = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
    "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

# ----- ENTRADAS -----
colab_nome = st.sidebar.selectbox("Selecione a colaboradora", colaboradoras)
ano_selecionado = st.sidebar.selectbox("Ano", anos_disponiveis, index=len(anos_disponiveis)-1)
mes_selecionado = st.sidebar.selectbox("Mês", list(meses_disponiveis.keys()), index=datetime.now().month-1)

# Entrada de dados
atendimentos = st.sidebar.number_input("Nº de Atendimentos", min_value=0, step=1)
tempo_medio = st.sidebar.number_input("Tempo Médio por Atendimento (min)", min_value=0.0, step=0.1)
erros = st.sidebar.number_input("Nº de Erros", min_value=0, step=1)

# Botão para enviar
if st.sidebar.button("Salvar Dados"):
    dados = {
        "Ano": ano_selecionado,
        "Mês": mes_selecionado,
        "Colaboradora": colab_nome,
        "Atendimentos": atendimentos,
        "Tempo Médio": tempo_medio,
        "Erros": erros
    }
    st.session_state.setdefault("dados", []).append(dados)
    st.sidebar.success("Dados salvos!")

# ----- ANÁLISE -----
st.title("Painel de Performance da Equipe de Atendimento")

if "dados" not in st.session_state or not st.session_state["dados"]:
    st.info("Nenhum dado registrado ainda.")
else:
    df = pd.DataFrame(st.session_state["dados"])

    # Filtro por mês e ano
    df_filtrado = df[(df["Ano"] == ano_selecionado) & (df["Mês"] == mes_selecionado)]

    if df_filtrado.empty:
        st.warning("Nenhum dado para este período.")
    else:
        for nome in df_filtrado["Colaboradora"].unique():
            colab_df = df_filtrado[df_filtrado["Colaboradora"] == nome]

            # Métricas
            produtividade = colab_df["Atendimentos"].mean()
            eficiencia = 100 - colab_df["Tempo Médio"].mean()
            qualidade = max(0, 100 - (colab_df["Erros"].mean() * 10))
            performance_final = (produtividade + eficiencia + qualidade) / 3

            # Radar chart
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[produtividade, eficiencia, qualidade, performance_final],
                theta=["Produtividade", "Eficiência", "Qualidade", "Performance Final"],
                fill='toself',
                name=nome
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title=f"Performance - {nome} ({mes_selecionado}/{ano_selecionado})"
            )
            st.plotly_chart(fig, use_container_width=True)
