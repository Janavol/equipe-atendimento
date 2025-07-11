import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import base64
import io

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

def mes_extenso(mes):
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
             'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    return meses[mes - 1]

# Armazena dados na sessão por mês e ano
if "dados_colaboradoras" not in st.session_state:
    st.session_state.dados_colaboradoras = {}

# Seleção de ano e mês
col1, col2 = st.columns(2)
with col1:
    ano = st.selectbox("Selecione o ano:", [2025, 2026], key="ano")
with col2:
    mes = st.selectbox("Selecione o mês:", list(range(1, 13)), format_func=lambda m: mes_extenso(m).capitalize(), key="mes")

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
            nome = st.session_state.get(f"nome_{i}", "").strip()
            if nome == "":
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

    if dados:
        # Cálculo das médias (somente dados válidos)
        df = pd.DataFrame(dados)
        df = df[df['Nome'].str.strip() != ""]
        media_atend = df['Atendimentos'].mean()
        media_tempo = df['Tempo Médio (min)'].mean()
        media_erros = df['Erros'].mean()

        relatorio_final = []
        for registro in dados:
            nome = registro["Nome"]
            atendimentos = registro["Atendimentos"]
            tempo = registro["Tempo Médio (min)"]
            erros = registro["Erros"]

            produtividade = (atendimentos / media_atend * 100) if media_atend > 0 else 0
            eficiencia = (media_tempo / tempo * 100) if tempo > 0 else 0
            qualidade = (media_erros / erros * 100) if erros > 0 else 100 if media_erros == 0 else 0
            performance = (produtividade * 0.4) + (eficiencia * 0.3) + (qualidade * 0.3)

            # Título do gráfico
            st.subheader(f"{mes_extenso(mes).capitalize()} {ano} - {nome}")

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[produtividade, eficiencia, qualidade, performance, produtividade],
                theta=["Produtividade", "Eficiência", "Qualidade", "Performance", "Produtividade"],
                fill='toself',
                name=nome
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 150])
                ),
                showlegend=True,
                title=f"Desempenho de {nome}"
            )
            st.plotly_chart(fig, use_container_width=True)

            necessidades = []
            if produtividade < 100:
                necessidades.append("📚 produtividade")
            if eficiencia < 100:
                necessidades.append("📚 eficiência")
            if qualidade < 100:
                necessidades.append("📚 qualidade")

            if necessidades:
                st.markdown(f"<b>{nome}:</b> necessita de capacitação em {', '.join(necessidades)}.", unsafe_allow_html=True)
                relatorio_final.append(f"{nome}, capacitação em {', '.join(necessidades)}")

        if relatorio_final:
            st.subheader("Relatório Geral de Capacitação")
            st.markdown(f"Com base nos dados analisados durante o mês de <b>{mes_extenso(mes).capitalize()} de {ano}</b>, necessitam de aperfeiçoamento os seguintes colaboradores:", unsafe_allow_html=True)
            for linha in relatorio_final:
                st.markdown(f"- {linha}")

        if st.button("Exportar dados para PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Relatório de Desempenho - {mes_extenso(mes).capitalize()}/{ano}", ln=True, align='C')
            pdf.ln(10)

            for reg in dados:
                pdf.cell(200, 10, txt=f"{reg['Nome']}: Atendimentos={reg['Atendimentos']}, Tempo Médio={reg['Tempo Médio (min)']:.2f} min, Erros={reg['Erros']}", ln=True)

            if relatorio_final:
                pdf.ln(10)
                pdf.cell(200, 10, txt="Colaboradores que necessitam capacitação:", ln=True)
                for linha in relatorio_final:
                    pdf.cell(200, 10, txt=f"- {linha}", ln=True)

            buffer = io.BytesIO()
            pdf.output(buffer)
            b64 = base64.b64encode(buffer.getvalue()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="relatorio_{chave}.pdf">Clique aqui para baixar o PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
