import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

# 1. Adicione as novas funções na importação aqui!
from data_loader import carregar_dados, tratar_dados, carregar_coordenadas, mesclar_coordenadas
from model import treinar_modelo

# ========================
# CONFIGURAÇÃO
# ========================

st.set_page_config(layout="wide", page_title="Dashboard SRAG")
st.title("📊 Dashboard SRAG - Análise Completa")

# ========================
# CAMINHOS
# ========================

# O seu arquivo original
ARQUIVO = r"/home/diogo/Documentos/codigos/Projeto-de-software/docs/database/INFLUD19-26-06-2025.csv"
MAPA = r"/home/diogo/Documentos/codigos/Projeto-de-software/src/brasil_estados.geojson"

# 2. ADICIONE O CAMINHO DO SEU CSV DE MUNICÍPIOS AQUI:
# (Troque pelo caminho real de onde você salvou o arquivo no seu computador)
ARQUIVO_CIDADES = r"/home/diogo/Documentos/codigos/Projeto-de-software/docs/database/municipios.csv" 

# ========================
# DADOS
# ========================

@st.cache_data
def load_data():
    # Carrega e trata os dados principais
    df_bruto = carregar_dados(ARQUIVO)
    df_tratado = tratar_dados(df_bruto)
    
    # Carrega o CSV de coordenadas usando o caminho que você definiu acima
    df_coords = carregar_coordenadas(ARQUIVO_CIDADES)
    
    # Mescla os dois DataFrames
    df_final = mesclar_coordenadas(df_tratado, df_coords)
    
    return df_final

df_total = load_data()
df = df_total.copy()

# ========================
# DOENÇAS
# ========================

mapa_doencas = {
    1: "Influenza",
    2: "Outros vírus",
    3: "Outros agentes",
    4: "SRAG não especificado",
    5: "COVID-19"
}

df["DOENCA"] = df["CLASSI_FIN"].map(mapa_doencas)

# Remover linhas sem DOENCA
df = df.dropna(subset=["DOENCA"])

# ========================
# FILTROS
# ========================

st.sidebar.header("🔎 Filtros")

estado = st.sidebar.multiselect(
    "Estado",
    sorted(df["SG_UF"].dropna().unique()),
    default=sorted(df["SG_UF"].dropna().unique())
)

doenca = st.sidebar.multiselect(
    "Doença",
    sorted(df["DOENCA"].dropna().unique()),
    default=sorted(df["DOENCA"].dropna().unique())
)

df = df[df["SG_UF"].isin(estado)]
df = df[df["DOENCA"].isin(doenca)]

# ========================
# KPIs
# ========================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Casos", len(df))
col2.metric("Estados", df["SG_UF"].nunique())
col3.metric("Doenças", df["DOENCA"].nunique())

if "OBITO" in df.columns and len(df) > 0:
    obitos_pct = round((df["OBITO"].sum() / len(df)) * 100, 2)
else:
    obitos_pct = 0

col4.metric("Óbitos (%)", obitos_pct)

st.divider()

# ========================
# ABAS
# ========================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Geral",
    "🔥 Heatmap",
    "🗺️ Mapa",
    "🌳 Árvore",
    "📈 Temporal",
    "📊 Distribuições"
])

# ========================
# ABA 1 - GERAL
# ========================

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        df_pie = df["DOENCA"].value_counts().reset_index()
        df_pie.columns = ["DOENCA", "count"]

        fig = px.pie(
            df_pie,
            names="DOENCA",
            values="count",
            hole=0.4,
            title="Distribuição por Doença"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_bar = df["SG_UF"].value_counts().reset_index()
        df_bar.columns = ["SG_UF", "count"]

        fig = px.bar(
            df_bar,
            x="SG_UF",
            y="count",
            title="Casos por Estado"
        )
        st.plotly_chart(fig, use_container_width=True)

# ========================
#  ABA 2 - HEATMAP + CIDADES
# ========================

with tab2:
    st.subheader(" Heatmap e Distribuição Geográfica")

    geo = gpd.read_file(MAPA)

    # 1. Filtro de Estado
    estados_disponiveis = sorted(df["SG_UF"].dropna().unique())
    estado_sel = st.selectbox("Estado", ["Todos"] + estados_disponiveis)

    df_map = df.copy()

    if estado_sel != "Todos":
        df_map = df_map[df_map["SG_UF"] == estado_sel]

    # 2. Filtro de Cidade
    if "ID_MN_RESI" in df_map.columns:
        cidades_disponiveis = sorted(df_map["ID_MN_RESI"].dropna().unique())
        cidade_sel = st.selectbox("Cidade", ["Todas"] + cidades_disponiveis)

        if cidade_sel != "Todas":
            df_map = df_map[df_map["ID_MN_RESI"] == cidade_sel]

    # 3. Lógica do Gráfico
    if cidade_sel == "Todas":
        # MAPA POR ESTADO (Visão Geral)
        casos_estado = df_map["SG_UF"].value_counts().reset_index()
        casos_estado.columns = ["SG_UF", "casos"]

        geo_estado = geo.merge(casos_estado, left_on="sigla", right_on="SG_UF", how="left")
        geo_estado = geo_estado.to_crs(epsg=4326)
        
        # Pega o centro do estado para o mapa de calor
        geo_estado["lat"] = geo_estado.geometry.centroid.y
        geo_estado["lon"] = geo_estado.geometry.centroid.x

        fig = px.density_mapbox(
            geo_estado,
            lat="lat",
            lon="lon",
            z="casos",
            radius=40,
            zoom=3.5, # Ajuste fino do zoom para caber o Brasil
            center={"lat": -15.0, "lon": -53.0}, # Coordenadas centrais do Brasil!
            mapbox_style="carto-positron",
            title="Mapa de Calor por Estado"
        )
        # Deixa o mapa mais alto e tira as margens brancas mortas
        fig.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

    else:
        # MAPA POR CIDADE (Visão Específica com Lat/Lon reais)
        st.info(f" Mostrando dados focados em: {cidade_sel}")
            
        
        
        
        # Verifica se as colunas de coordenada existem e não estão vazias para essa cidade
        if "latitude" in df_map.columns and "longitude" in df_map.columns and pd.notna(df_map["latitude"].iloc[0]):
            
            # Conta os casos nessa localidade para definir a intensidade da "mancha" de calor
            casos_cidade = df_map.groupby(["ID_MN_RESI", "latitude", "longitude"]).size().reset_index(name="casos")
            
            # Calcula o meio exato da cidade para a câmera focar nela!
            centro_lat = casos_cidade["latitude"].mean()
            centro_lon = casos_cidade["longitude"].mean()
            
            fig = px.density_mapbox(
                casos_cidade,
                lat="latitude",
                lon="longitude",
                z="casos",
                radius=50,
                zoom=10, # Zoom bem próximo (nível de ruas/bairros)
                center={"lat": centro_lat, "lon": centro_lon}, # Foca na cidade!
                mapbox_style="carto-positron",
                title=f"Densidade de Casos - {cidade_sel}"
            )
            # Mesma formatação de altura e bordas
            fig.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f" Não foi possível encontrar as coordenadas para a cidade de {cidade_sel}. Verifique se o código IBGE dela existe no arquivo municipios.csv.")

    # Gráfico de barras de brinde embaixo do mapa
    st.subheader("📊 Top Casos por Cidade")
    if "ID_MN_RESI" in df_map.columns and len(df_map) > 0:
        df_city = df_map["ID_MN_RESI"].value_counts().reset_index()
        df_city.columns = ["Cidade", "casos"]

        fig = px.bar(
            df_city.head(20),
            x="Cidade",
            y="casos",
            title="Cidades com Mais Casos Filtrados",
            color="casos",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig, use_container_width=True)

# ========================
#  ABA 3 - MAPA COROPLÉTICO
# ========================

with tab3:
    geo = gpd.read_file(MAPA)

    casos_estado = df["SG_UF"].value_counts().reset_index()
    casos_estado.columns = ["SG_UF", "casos"]

    geo = geo.merge(casos_estado, left_on="sigla", right_on="SG_UF", how="left")

    geo = geo.to_crs(epsg=4326)

    fig = px.choropleth_mapbox(
        geo,
        geojson=geo.__geo_interface__,
        locations=geo.index,
        color="casos",
        mapbox_style="open-street-map",
        zoom=3,
        center={"lat": -14, "lon": -51},
        opacity=0.6,
        title="Casos por Estado"
    )

    st.plotly_chart(fig, use_container_width=True)

# ========================
#  ABA 4 - ÁRVORE
# ========================

with tab4:
    st.subheader(" Árvore Hierárquica")

    df_tree = df.copy()

    df_tree = df_tree.dropna(subset=["SG_UF", "ID_MN_RESI", "DOENCA"])

    if len(df_tree) == 0:
        st.warning("Sem dados suficientes para árvore.")
    else:
        df_tree = df_tree.groupby(
            ["SG_UF", "ID_MN_RESI", "DOENCA"]
        ).size().reset_index(name="count")

        fig = px.treemap(
            df_tree,
            path=["SG_UF", "ID_MN_RESI", "DOENCA"],
            values="count",
            title="Hierarquia: Estado → Cidade → Doença"
        )

        st.plotly_chart(fig, use_container_width=True)

# ========================
#  ABA 5 - TEMPORAL
# ========================

with tab5:
    if "DT_NOTIFIC" in df.columns:
        df_temp = df.dropna(subset=["DT_NOTIFIC"]).copy()
        df_temp["DT_NOTIFIC"] = pd.to_datetime(df_temp["DT_NOTIFIC"], errors="coerce")

        df_temp["ANO_MES"] = df_temp["DT_NOTIFIC"].dt.to_period("M").astype(str)

        serie = df_temp.groupby(["ANO_MES", "DOENCA"]).size().reset_index(name="casos")

        fig = px.line(
            serie,
            x="ANO_MES",
            y="casos",
            color="DOENCA",
            title="Evolução Temporal"
        )

        st.plotly_chart(fig, use_container_width=True)

# ========================
#  ABA 6 - DISTRIBUIÇÕES
# ========================

with tab6:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x="NU_IDADE_N",
            nbins=30,
            title="Distribuição de Idade"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "OBITO" in df.columns:
            fig = px.box(
                df,
                x="OBITO",
                y="NU_IDADE_N",
                title="Idade vs Óbito"
            )
            st.plotly_chart(fig, use_container_width=True)

# ========================
# MACHINE LEARNING
# ========================

with st.sidebar.expander("🤖 Machine Learning"):
    if st.button("Treinar modelo"):
        modelo = treinar_modelo(df_total)

        if modelo:
            st.success("Modelo treinado com sucesso!")
        else:
            st.error("Erro ao treinar o modelo.")