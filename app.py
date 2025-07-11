import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import base64
import io

st.set_page_config(layout="wide")

# Função para retornar o nome do mês em português
def mes_extenso(mes):
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    return meses.get(mes, "mês inválido").capitalize()

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

if "dados_colaboradoras" not in st.session_state:
    st.session_state.dados_colaboradoras = {}

col1, col2 = st.columns(2)
with col1:
    ano = st.selectbox("Selecione o ano:", [2025, 2026], key="ano")
with col2:
    mes = st.selectbox("Selecione o mês:", list(range(1, 13)), format_func=lambda m: mes_extenso(m), key="mes")

chave = f"{ano}-{mes}"

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
            tempo = st.text_input("Tempo médio de atendimento", value="00:00", key=f"tempo_{i}")
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
    dados_validos = [r for r in dados if r["Nome"] and r["Atendimentos"] > 0 and r["Tempo Médio (min)"] > 0]

    if dados_validos:
        relatorio_final = []

        media_atend = sum([r["Atendimentos"] for r in dados_validos]) / len(dados_validos)
        media_tempo = sum([r["Tempo Médio (min)"] for r in dados_validos]) / len(dados_validos)
        media_erros = sum([r["Erros"] for r in dados_validos]) / len(dados_validos)

        tabela_resultados = []

        for registro in dados_validos:
            nome = registro["Nome"]
            atendimentos = registro["Atendimentos"]
            tempo = registro["Tempo Médio (min)"]
            erros = registro["Erros"]

            produtividade = (atendimentos / media_atend) * 100 if media_atend else 0
            eficiencia = (media_tempo / tempo) * 100 if tempo else 0
            qualidade = (media_erros / erros) * 100 if erros else 0

            performance = (produtividade * 0.4) + (eficiencia * 0.3) + (qualidade * 0.3)
            tabela_resultados.append([nome, produtividade, eficiencia, qualidade, performance])

            st.subheader(f"{mes_extenso(mes)} {ano} - {nome}")
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[produtividade, eficiencia, qualidade, performance, produtividade],
                theta=["Produtividade", "Eficiência", "Qualidade", "Performance", "Produtividade"],
                fill='toself',
                name=nome
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 150])),
                showlegend=True,
                title=f"Desempenho de {nome}"
            )
            st.plotly_chart(fig, use_container_width=True)

            necessidades = []
            atencao = []
            if produtividade < 90:
                necessidades.append("produtividade")
            elif produtividade < 100:
                atencao.append("produtividade")
            if eficiencia < 90:
                necessidades.append("eficiência")
            elif eficiencia < 100:
                atencao.append("eficiência")
            if qualidade < 90:
                necessidades.append("qualidade")
            elif qualidade < 100:
                atencao.append("qualidade")

            if necessidades or atencao:
                comentario = f"<b>{nome}</b>: "
                if necessidades:
                    comentario += f"📚 requer capacitação em {', '.join(necessidades)}"
                if atencao:
                    if necessidades:
                        comentario += " e "
                    comentario += f"🔍 atenção em {', '.join(atencao)}"
                st.markdown(comentario, unsafe_allow_html=True)
                relatorio_final.append(comentario)

        st.subheader("Tabela de Resultados")
        df_result = pd.DataFrame(tabela_resultados, columns=["Colaborador", "Produtividade", "Eficiência", "Qualidade", "Performance"])
        st.dataframe(df_result.style.format("{:.2f}"))

        if relatorio_final:
            st.subheader("Relatório Geral de Capacitação e Atenção")
            st.markdown(f"Com base nos dados analisados durante o mês de <b>{mes_extenso(mes)} de {ano}</b>, seguem os apontamentos:", unsafe_allow_html=True)
            for linha in relatorio_final:
                st.markdown(f"- {linha}", unsafe_allow_html=True)

        if st.button("Exportar dados para PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Relatório de Desempenho - {mes_extenso(mes)} {ano}", ln=True, align='C')
            pdf.ln(10)
            for linha in relatorio_final:
                pdf.multi_cell(0, 10, txt=linha.replace('<b>', '').replace('</b>', '').replace('<br>', '').replace('🔍', '').replace('📚', ''))
            pdf.ln(10)
            for index, row in df_result.iterrows():
                pdf.cell(0, 10, txt=f"{row['Colaborador']} - P:{row['Produtividade']:.2f}, E:{row['Eficiência']:.2f}, Q:{row['Qualidade']:.2f}, PF:{row['Performance']:.2f}", ln=True)

            buffer = io.BytesIO()
            pdf.output(buffer)
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="relatorio_{chave}.pdf">Clique aqui para baixar o PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
