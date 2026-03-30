import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

from data_loader import carregar_dados, tratar_dados
from model import treinar_modelo

ARQUIVO = "/home/diogo/Documentos/codigos/Projeto-de-software/docs/database/INFLUD19-26-06-2025.cs"
MAPA = "brasil_estados.geojson"

st.set_page_config(layout="wide")
st.title("Dashboard SRAG - Análise Completa")

# ========================
# CARREGAR DADOS
# ========================

df_total = tratar_dados(carregar_dados(ARQUIVO))
df = df_total.copy()

# ========================
# MAPA DE DOENÇAS
# ========================

mapa_doencas = {
    1: "Influenza",
    2: "Outros vírus",
    3: "Outros agentes",
    4: "SRAG não especificado",
    5: "COVID-19"
}

df["DOENCA"] = df["CLASSI_FIN"].map(mapa_doencas)

# ========================
# FILTROS
# ========================

st.sidebar.header("Filtros")

estado = st.sidebar.selectbox(
    "Estado",
    ["Todos"] + sorted(df["SG_UF"].dropna().unique().tolist())
)

if estado != "Todos":
    df = df[df["SG_UF"] == estado]

doenca = st.sidebar.selectbox(
    "Doença",
    ["Todas"] + list(mapa_doencas.values())
)

if doenca != "Todas":
    df = df[df["DOENCA"] == doenca]

# ========================
# MACHINE LEARNING
# ========================

st.sidebar.subheader("Machine Learning")

if st.sidebar.button("Treinar modelo"):
    modelo = treinar_modelo(df_total)

    if modelo:
        st.sidebar.success("Modelo treinado!")
    else:
        st.sidebar.error("Erro no treino.")

# ========================
# DISTRIBUIÇÃO DE DOENÇAS
# ========================

st.subheader("Distribuição de Doenças")

contagem = df["DOENCA"].value_counts().reset_index()
contagem.columns = ["doenca", "casos"]

fig1 = px.pie(
    contagem,
    names="doenca",
    values="casos",
    title="Distribuição de SRAG",
    color_discrete_sequence=px.colors.sequential.RdBu
)

st.plotly_chart(fig1, use_container_width=True)

# ========================
# CASOS POR ESTADO
# ========================

st.subheader("Casos por Estado")

casos_estado = df["SG_UF"].value_counts().reset_index()
casos_estado.columns = ["estado", "casos"]

fig2 = px.bar(
    casos_estado,
    x="estado",
    y="casos",
    color="casos",
    color_continuous_scale="viridis"
)

st.plotly_chart(fig2, use_container_width=True)

# ========================
# MAPA DO BRASIL
# ========================

st.subheader("Mapa do Brasil")

geo = gpd.read_file(MAPA)

casos_estado = df["SG_UF"].value_counts().reset_index()
casos_estado.columns = ["SG_UF", "casos"]

geo = geo.merge(casos_estado, left_on="sigla", right_on="SG_UF", how="left")

fig3 = px.choropleth(
    geo,
    geojson=geo.geometry,
    locations=geo.index,
    color="casos",
    color_continuous_scale="Reds"
)

fig3.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig3, use_container_width=True)

# ========================
# HEATMAP DOENÇA x TEMPO
# ========================

st.subheader("Heatmap Doença x Tempo")

df_heat = df.dropna(subset=["DT_NOTIFIC", "DOENCA"])
df_heat["ANO_MES"] = df_heat["DT_NOTIFIC"].dt.to_period("M").astype(str)

tabela = pd.crosstab(df_heat["DOENCA"], df_heat["ANO_MES"])

fig4 = px.imshow(
    tabela,
    aspect="auto",
    color_continuous_scale="viridis"
)

st.plotly_chart(fig4, use_container_width=True)

# ========================
# EVOLUÇÃO TEMPORAL
# ========================

st.subheader("Evolução das Doenças")

serie = df_heat.groupby(["DT_NOTIFIC", "DOENCA"]).size().reset_index(name="casos")

fig5 = px.line(
    serie,
    x="DT_NOTIFIC",
    y="casos",
    color="DOENCA"
)

st.plotly_chart(fig5, use_container_width=True)

# ========================
# IDADE vs ÓBITO
# ========================

st.subheader("Idade vs Óbito")

df_box = df.dropna(subset=["NU_IDADE_N", "OBITO"])

fig6 = px.box(
    df_box,
    x="OBITO",
    y="NU_IDADE_N",
    color="OBITO"
)

st.plotly_chart(fig6, use_container_width=True)