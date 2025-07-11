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

# Função para traduzir o mês
meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
def mes_extenso(mes):
    return meses_pt[mes - 1]

# Armazena dados na sessão por mês e ano
if "dados_colaboradoras" not in st.session_state:
    st.session_state.dados_colaboradoras = {}

# Seleção de ano e mês
col1, col2 = st.columns(2)
with col1:
    ano = st.selectbox("Selecione o ano:", [2025, 2026], key="ano")
with col2:
    mes = st.selectbox("Selecione o mês:", list(range(1, 13)), format_func=mes_extenso, key="mes")

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
            tempo = st.text_input("Tempo médio de atendimento", value="00:00", key=f"tempo_{i}")
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
        df = pd.DataFrame(dados)
        media_atend = df["Atendimentos"].mean()
        media_tempo = df["Tempo Médio (min)"].mean()
        media_erros = df["Erros"].mean()

        relatorio_final = []
        tabela_resultados = []

        for registro in dados:
            nome = registro["Nome"]
            atendimentos = registro["Atendimentos"]
            tempo = registro["Tempo Médio (min)"]
            erros = registro["Erros"]

            produtividade = (atendimentos / media_atend) * 100 if media_atend > 0 else 0
            eficiencia = (media_tempo / tempo) * 100 if tempo > 0 else 0
            qualidade = (media_erros / erros) * 100 if erros > 0 else 100

            performance = (produtividade * 0.4) + (eficiencia * 0.3) + (qualidade * 0.3)

            mes_ano_texto = f"{mes_extenso(mes).capitalize()} {ano}"
            st.subheader(f"{mes_ano_texto} - {nome}")

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

            atencao = []
            capacitacao = []

            for valor, area in zip([produtividade, eficiencia, qualidade], ["produtividade", "eficiência", "qualidade"]):
                if valor < 90:
                    capacitacao.append(area)
                elif valor < 100:
                    atencao.append(area)

            emoji = "📚"
            if capacitacao or atencao:
                mensagem = f"<b>{nome}</b>: "
                if capacitacao:
                    mensagem += f"requer capacitação em {', '.join(capacitacao)}"
                if capacitacao and atencao:
                    mensagem += " e "
                if atencao:
                    mensagem += f"atenção em {', '.join(atencao)}"
                st.markdown(f"{mensagem} {emoji}", unsafe_allow_html=True)
                relatorio_final.append(mensagem.strip("<b>").strip("</b>").replace("<b>", "").replace("</b>", ""))

            tabela_resultados.append([nome, produtividade, eficiencia, qualidade, performance])

        # Tabela final de resultados
        st.subheader("Tabela de Resultados")
        df_result = pd.DataFrame(tabela_resultados, columns=["Colaborador", "Produtividade", "Eficiência", "Qualidade", "Performance"])
        format_dict = {col: "{:.2f}" for col in df_result.select_dtypes(include='number').columns}
        st.dataframe(df_result.style.format(format_dict))

        # Relatório geral
        if relatorio_final:
            st.subheader("Relatório Geral de Capacitação e Atenção")
            st.markdown(f"Com base nos dados analisados durante o mês de <b>{mes_extenso(mes)} de {ano}</b>, necessitam de aperfeiçoamento os seguintes colaboradores:", unsafe_allow_html=True)
            for linha in relatorio_final:
                st.markdown(f"- {linha}")

        # PDF ainda será corrigido (próxima etapa)
        if st.button("Exportar dados para PDF"):
            st.warning("Função de exportar PDF será implementada em breve.")
