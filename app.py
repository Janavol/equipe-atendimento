import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard de Performance", layout="wide")

st.title("Painel de Performance da Equipe de Atendimento")

# Formulário de entrada de dados
with st.sidebar.form(key='formulario'):
    st.header("📋 Preenchimento de Dados")
    nome = st.selectbox("Colaboradora:", ["Ana", "Beatriz", "Carla", "Daniela", "Eduarda"])
    atendimentos = st.number_input("Número de atendimentos:", min_value=0, step=1)
    tempo_medio = st.number_input("Tempo médio por atendimento (min):", min_value=0.0, step=0.1)
    erros = st.number_input("Número de erros:", min_value=0, step=1)
    submitted = st.form_submit_button("Enviar")

# Inicializa ou carrega o DataFrame
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["Nome", "Atendimentos", "Tempo Médio", "Erros", "Produtividade", "Eficiência", "Qualidade", "Performance Final"])

# Cálculo das métricas
def calcular_metricas(atendimentos, tempo_medio, erros):
    produtividade = min(atendimentos / 100, 1)
    eficiencia = max(1 - (tempo_medio / 30), 0)
    qualidade = max(1 - (erros / 10), 0)
    performance = round(((produtividade + eficiencia + qualidade) / 3) * 100, 2)
    return produtividade, eficiencia, qualidade, performance

# Salva os dados após submissão
if submitted:
    produtividade, eficiencia, qualidade, performance = calcular_metricas(atendimentos, tempo_medio, erros)
    novo_dado = {
        "Nome": nome,
        "Atendimentos": atendimentos,
        "Tempo Médio": tempo_medio,
        "Erros": erros,
        "Produtividade": round(produtividade, 2),
        "Eficiência": round(eficiencia, 2),
        "Qualidade": round(qualidade, 2),
        "Performance Final": performance
    }
    st.session_state.dados = pd.concat([st.session_state.dados, pd.DataFrame([novo_dado])], ignore_index=True)
    st.success("Dados salvos com sucesso!")

# Exibe a tabela atualizada
if not st.session_state.dados.empty:
    st.subheader("📊 Tabela de Dados")
    st.dataframe(st.session_state.dados, use_container_width=True)

    st.subheader("📈 Gráficos de Radar")
    for _, row in st.session_state.dados.iterrows():
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[row["Produtividade"], row["Eficiência"], row["Qualidade"]],
            theta=["Produtividade", "Eficiência", "Qualidade"],
            fill='toself',
            name=row["Nome"]
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1])
            ),
            showlegend=True,
            title=f"Desempenho de {row['Nome']}"
        )
        st.plotly_chart(fig, use_container_width=True)
 