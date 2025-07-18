import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações iniciais do app
st.set_page_config(page_title="Análise de Falhas - UFV", layout="centered")

# CSS para fundo preto e cores no texto
st.markdown("""
    <style>
        body {
            background-color: #0e0e0e;
            color: #f0f0f0;
        }
        .stApp {
            background-color: #0e0e0e;
            color: #f0f0f0;
        }
        .block-container {
            padding-top: 2rem;
        }
        h1, h2, h3, h4 {
            color: #f9f871;
        }
        .stDataFrame {
            background-color: #1e1e1e;
        }
    </style>
""", unsafe_allow_html=True)

# Dados das falhas
falhas = {
    "Soltec": {
        "NCU perdeu comunicação": 1,
        "Tracker parado por falha Motor_baterias_comlost": 30,
        "Inject TCU modo fact": 4,
        "TCU em curto + inject": 1,
        "Eixo Cardan": 1,
        "Falha de Motor TCU": 1
    },
    "Sungrow": {
        "Falha de Ventilação no inversor": 1,
        "Falha de Impedância (ISOLAÇÃO)": 1,
        "Falha de Proteção PDP (mau contato nas conexões)": 1
    },
    "PV": {
        "Fusível rompido na string": 1,
        "Cabo solar danificado": 3,
        "Fusível 400A DC atuado": 1,
        "Conector MC4 danificado": 1
    },
    "Módulos": {
        "Junction box danificada": 150
    }
}

acoes = [
    "Plano de Manutenção PCS-SKID – quinzenal/mensal – Concluído 08/07",
    "Plano de Manutenção Trafo – Semestral – Concluído 07/07",
    "Inspeção Combiner BOX (performance) – Concluído 11/07",
    "Plano de estação meteorológica – mensal – Concluído 11/07",
    "Plano Inversor Central - mv Station - Check-list Semestral/Trimestral - Em Andamento"
]

observacoes = [
    "01/07 a 02/07: Tracker parado por MODO FACT até as 16h",
    "03/07: Motor de TCU com falha – 3 horas inoperante",
    "08/07: Falha ventilador inversor 2.1-2 – troca levou 24 horas",
    "10/07: Falha de Proteção PDP (mau contato em conexões de fases – 1 hora parada)",
    "Limpeza de 2 strings Combiner 17 → aumento de corrente de 5,8A para 7,8A (~34,48%)"
]

# Processamento dos dados
df_falhas = []
for categoria, eventos in falhas.items():
    for falha, qtd in eventos.items():
        df_falhas.append({"Categoria": categoria, "Falha": falha, "Ocorrências": qtd})
df = pd.DataFrame(df_falhas)
df_total = df.groupby("Categoria")["Ocorrências"].sum().reset_index()

# Mapeamento de cores vibrantes para cada categoria
colors = {
    "Soltec": "#00f7ff",      # ciano neon
    "Sungrow": "#f72585",     # rosa neon
    "PV": "#ffd60a",          # amarelo vibrante
    "Módulos": "#80ffdb"      # verde água
}
df_total["Cor"] = df_total["Categoria"].map(colors)

# Layout do app
st.title("📊 Análise de Falhas - Julho 2025")
st.markdown("<h4 style='color:#00f7ff'>Relatório consolidado de falhas da usina fotovoltaica UFV - Período: 01 a 14 de Julho</h4>", unsafe_allow_html=True)

# Gráfico interativo com Plotly
fig = px.bar(
    df_total,
    x="Categoria",
    y="Ocorrências",
    color="Categoria",
    color_discrete_map=colors,
    text="Ocorrências",
    title="Falhas por Categoria"
)

fig.update_layout(
    plot_bgcolor="#0e0e0e",
    paper_bgcolor="#0e0e0e",
    font=dict(color="white"),
    title_font=dict(color="#f9f871"),
    xaxis=dict(title="", color="white"),
    yaxis=dict(title="Ocorrências", color="white"),
    legend=dict(font=dict(color="white")),
)

fig.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Ocorrências: %{y}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

# Detalhamento das falhas
st.subheader("📋 Detalhamento de Falhas")
with st.expander("🔎 Clique para ver as falhas detalhadas"):
    st.dataframe(df.style.background_gradient(cmap="cividis"), use_container_width=True)

# Ações executadas
st.subheader("✅ Ações Executadas")
for acao in acoes:
    st.markdown(f"<span style='color:#80ffdb'>- {acao}</span>", unsafe_allow_html=True)

# Observações técnicas
st.subheader("📝 Observações Técnicas")
for obs in observacoes:
    st.markdown(f"<span style='color:#f72585'>- {obs}</span>", unsafe_allow_html=True)
