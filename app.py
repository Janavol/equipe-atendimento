import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

# Título principal
st.title("Painel de Desempenho da Equipe de Atendimento")

# Sidebar para seleção de período
with st.sidebar:
    st.header("Selecione o Período")
    ano = st.selectbox("Ano", list(range(2023, datetime.today().year + 1)), index=1)
    mes = st.selectbox("Mês", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], index=int(datetime.today().month) - 1)
    st.markdown("---")
    st.subheader("Preenchimento dos Dados")

# Lista para armazenar os dados
colaboradoras = []

# Função para conversão de HH:MM em minutos decimais
def tempo_para_minutos(tempo):
    try:
        if ":" in tempo:
            partes = tempo.split(":")
            horas = int(partes[0])
            minutos = int(partes[1])
            return horas * 60 + minutos
        else:
            return float(tempo)
    except:
        return 0

# Layout alternado para 25 colaboradoras
for i in range(25):
    cor_fundo = "#4F4F4F" if i % 2 == 0 else "#D3D3D3"
    cor_texto = "white" if i % 2 == 0 else "black"

    with st.container():
        st.markdown(f"""
            <div style='background-color: {cor_fundo}; padding: 15px; border-radius: 10px;'>
                <h4 style='color: {cor_texto};'>Colab. {i+1}</h4>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            nome = st.text_input(f"Nome {i+1}", key=f"nome_{i}")
        with col2:
            atendimentos = st.number_input(f"Nro. de atendimentos {i+1}", min_value=0, key=f"atend_{i}")
        with col3:
            tempo = st.text_input(f"Tempo médio (hh:mm) {i+1}", key=f"tempo_{i}")
        erros = st.number_input(f"Quantidade de erros {i+1}", min_value=0, key=f"erros_{i}")

        tempo_convertido = tempo_para_minutos(tempo)

        if nome:
            produtividade = atendimentos
            eficiencia = (atendimentos / tempo_convertido) * 60 if tempo_convertido > 0 else 0
            qualidade = 100 - ((erros / atendimentos) * 100) if atendimentos > 0 else 100
            performance = (produtividade * 0.4) + (eficiencia * 0.3) + (qualidade * 0.3)

            colaboradoras.append({
                "Nome": nome,
                "Produtividade": round(produtividade, 2),
                "Eficiência": round(eficiencia, 2),
                "Qualidade": round(qualidade, 2),
                "Performance Final": round(performance, 2)
            })

        st.markdown("</div><br>", unsafe_allow_html=True)

# Exibir os gráficos de radar se houver dados
if colaboradoras:
    st.subheader("Desempenho Individual")
    for colaboradora in colaboradoras:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[colaboradora["Produtividade"], colaboradora["Eficiência"], colaboradora["Qualidade"], colaboradora["Performance Final"]],
            theta=["Produtividade", "Eficiência", "Qualidade", "Performance Final"],
            fill='toself',
            name=colaboradora["Nome"]
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, title=colaboradora["Nome"])
        st.plotly_chart(fig, use_container_width=True)

    df = pd.DataFrame(colaboradoras)
    st.subheader("Resumo Geral")
    st.dataframe(df)
