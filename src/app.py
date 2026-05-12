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
from styles import carregar_estilos
st.set_page_config(layout="wide",
    page_title="Dashboard SRAG",
    page_icon="🦠")
st.markdown(
    carregar_estilos(),
    unsafe_allow_html=True
)

st.set_page_config(layout="wide", page_title="Dashboard SRAG")
st.title("📊 Dashboard SRAG - Análise Completa")

# ========================
# CAMINHOS
# ========================

ARQUIVO = r"/home/gabriel/Projetos/Projeto-de-software/docs/database/INFLUD19-23-03-2026.csv"
MAPA = r"/home/gabriel/Projetos/Projeto-de-software/src/brasil_estados.geojson"

# 2. ADICIONE O CAMINHO DO SEU CSV DE MUNICÍPIOS AQUI:
ARQUIVO_CIDADES = r"/home/gabriel/Projetos/Projeto-de-software/docs/database/municipios.csv" 

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

@st.cache_data
def load_mapa():
    return gpd.read_file(MAPA)

# Executando as funções e salvando nas variáveis globais do app
df_total = load_data()
df = df_total.copy()
geo = load_mapa()

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
# 📊 ABA 1 - GERAL (Refatorada)
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
            hole=0.5, # Aumentado para um visual "Donut" mais moderno
            title="<b>Distribuição por Doença</b>",
            color_discrete_sequence=px.colors.qualitative.Prism # Paleta mais vibrante
        )
        
        # Ajustes de Interatividade e Estilo
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            marker=dict(line=dict(color='#1e293b', width=2)) # Borda para separar fatias
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            showlegend=False, # Labels já estão no gráfico, economiza espaço
            margin=dict(t=50, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_bar = df["SG_UF"].value_counts().reset_index()
        df_bar.columns = ["SG_UF", "count"]

        fig = px.bar(
            df_bar,
            x="SG_UF",
            y="count",
            title="<b>Casos por Estado</b>",
            color="count", # Cor gradiente baseada no volume
            color_continuous_scale="Blues",
            labels={"count": "Casos", "SG_UF": "UF"}
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            xaxis={'categoryorder':'total descending'}, # Garante a ordem do maior para o menor
            coloraxis_showscale=False, # Remove a barra de cores lateral para limpar o visual
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        fig.update_traces(marker_line_color='rgba(0,0,0,0)') # Remove bordas das barras
        st.plotly_chart(fig, use_container_width=True)

# ========================
# 🔥 ABA 2 - HEATMAP + CIDADES
# ========================

with tab2:
    st.subheader("🔥 Heatmap e Distribuição Geográfica")

    # ========================
    # FILTRO DE ESTADO
    # ========================

    estados_disponiveis = sorted(df["SG_UF"].dropna().unique())
    estado_sel = st.selectbox("Estado", ["Todos"] + estados_disponiveis)

    df_map = df.copy()

    if estado_sel != "Todos":
        df_map = df_map[df_map["SG_UF"] == estado_sel]

    # ========================
    # FILTRO DE CIDADE
    # ========================

    cidade_sel = "Todas"

    if "ID_MN_RESI" in df_map.columns:
        cidades_disponiveis = sorted(df_map["ID_MN_RESI"].dropna().unique())

        cidade_sel = st.selectbox(
            "Cidade",
            ["Todas"] + cidades_disponiveis
        )

        if cidade_sel != "Todas":
            df_map = df_map[df_map["ID_MN_RESI"] == cidade_sel]

    # ========================
    # MAPA GERAL POR ESTADO
    # ========================

    if cidade_sel == "Todas":

        st.info("📍 Mostrando densidade térmica por municípios.")

        # Verifica se as colunas de coordenadas existem no DataFrame
        if "latitude" in df_map.columns and "longitude" in df_map.columns:

            # Agrupa os casos por cidade usando as coordenadas exatas
            casos_brasil_cidades = (
                df_map.groupby([
                    "ID_MN_RESI",
                    "latitude",
                    "longitude",
                    "POPULACAO"
                ])
                .size()
                .reset_index(name="casos")
            )

            # Calcula a taxa por 100 mil habitantes para padronizar
            casos_brasil_cidades["casos_100k"] = (
                casos_brasil_cidades["casos"] /
                casos_brasil_cidades["POPULACAO"]
            ) * 100000

            # Cria o Heatmap
            fig = px.density_mapbox(
                casos_brasil_cidades,
                lat="latitude",
                lon="longitude",
                z="casos_100k",
                radius=15, # Raio menor (15-20) evita que o Brasil vire um borrão gigante
                zoom=3.5,
                center={"lat": -15.5, "lon": -55.0}, # Centro do Brasil
                mapbox_style="carto-positron",
                title="<b>Heatmap: Casos por 100 mil hab. (Por Cidade)</b>",
                hover_name="ID_MN_RESI", # O nome da cidade aparece ao passar o mouse!
                hover_data={"latitude": False, "longitude": False, "casos_100k": ':.2f'}
            )

            # Ajustes de layout para ficar com a mesma altura elegante do Mapa Coroplético
            fig.update_layout(
                height=750,
                margin={"r":0, "t":50, "l":0, "b":0},
                coloraxis_colorbar=dict(
                    title="Intensidade",
                    thicknessmode="pixels", thickness=15,
                    lenmode="pixels", len=300,
                    yanchor="middle", y=0.5
                )
            )

            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("⚠️ As colunas 'latitude' e 'longitude' não foram encontradas. Verifique o cruzamento de coordenadas.")

      

    # ========================
    # MAPA POR CIDADE
    # ========================

    else:

        st.info(f"📍 Mostrando dados focados em: {cidade_sel}")

        if (
            "latitude" in df_map.columns and
            "longitude" in df_map.columns and
            len(df_map) > 0 and
            pd.notna(df_map["latitude"].iloc[0])
        ):

            # Casos por cidade
            casos_cidade = (
                df_map.groupby([
                    "ID_MN_RESI",
                    "latitude",
                    "longitude",
                    "POPULACAO"
                ])
                .size()
                .reset_index(name="casos")
            )

            # Casos por 100 mil habitantes
            casos_cidade["casos_100k"] = (
                casos_cidade["casos"] /
                casos_cidade["POPULACAO"]
            ) * 100000

            # Centro da cidade
            centro_lat = casos_cidade["latitude"].mean()
            centro_lon = casos_cidade["longitude"].mean()

            fig = px.density_mapbox(
                casos_cidade,
                lat="latitude",
                lon="longitude",
                z="casos_100k",
                radius=50,
                zoom=10,
                center={
                    "lat": centro_lat,
                    "lon": centro_lon
                },
                mapbox_style="carto-positron",
                title=f"Casos por 100 mil Habitantes - {cidade_sel}"
            )

            fig.update_layout(
                height=600,
                margin={"r":0, "t":40, "l":0, "b":0}
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning(
                f"⚠️ Não foi possível encontrar as coordenadas "
                f"para a cidade de {cidade_sel}."
            )

    # ========================
    # GRÁFICO DE BARRAS
    # ========================

    st.subheader("📊 Top Cidades por Incidência")

    if (
        "ID_MN_RESI" in df_map.columns and
        "POPULACAO" in df_map.columns and
        len(df_map) > 0
    ):

        df_city = (
            df_map.groupby([
                "ID_MN_RESI",
                "POPULACAO"
            ])
            .size()
            .reset_index(name="casos")
        )

        # Casos por 100 mil habitantes
        df_city["casos_100k"] = (
            df_city["casos"] /
            df_city["POPULACAO"]
        ) * 100000

        # Ordena pelas maiores incidências
        df_city = df_city.sort_values(
            by="casos_100k",
            ascending=False
        )

        fig = px.bar(
            df_city.head(20),
            x="ID_MN_RESI",
            y="casos_100k",
            title="Cidades com Maior Incidência (por 100 mil hab.)",
            color="casos_100k",
            color_continuous_scale="Reds",
            labels={
                "ID_MN_RESI": "Cidade",
                "casos_100k": "Casos por 100 mil hab."
            }
        )

        st.plotly_chart(fig, use_container_width=True)

# ========================
# 🗺️ ABA 3 - MAPA COROPLÉTICO
# ========================

with tab3:
    # 1. Preparação dos dados (mantive sua lógica)
    casos_estado = df["SG_UF"].value_counts().reset_index()
    casos_estado.columns = ["SG_UF", "casos"]

    geo = geo.merge(casos_estado, left_on="sigla", right_on="SG_UF", how="left")
    geo = geo.to_crs(epsg=4326)

    # 2. Criação do gráfico
    fig = px.choropleth_mapbox(
        geo,
        geojson=geo.__geo_interface__,
        locations=geo.index,
        color="casos",
        hover_name="name", # Mostra o nome do estado no topo do card
        hover_data={"SG_UF": True, "casos": True}, 
        mapbox_style="carto-positron", # Estilo mais clean e profissional
        zoom=3.3, # Ajuste fino do zoom para o Brasil
        center={"lat": -15.5, "lon": -55}, # Centralizado levemente para a esquerda
        opacity=0.7,
        color_continuous_scale="Blues", # Escala de cor elegante
        title="<b>Distribuição de Casos por Estado</b>"
    )

    # 3. O Pulo do Gato: Ajuste de Altura e Margens
    fig.update_layout(
        height=750, # Aqui você força o formato mais quadrado/vertical
        margin={"r":0,"t":50,"l":0,"b":0}, # Remove bordas inúteis
        coloraxis_colorbar=dict(
            title="Nº Casos",
            thicknessmode="pixels", thickness=15,
            lenmode="pixels", len=300,
            yanchor="middle", y=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# ========================
# 🌳 ABA 4 - ÁRVORE
# ========================

with tab4:
    st.subheader("🌳 Árvore Hierárquica")

    df_tree = df.copy().dropna(subset=["SG_UF", "ID_MN_RESI", "DOENCA"])

    if len(df_tree) == 0:
        st.warning("Sem dados suficientes para árvore.")
    else:
        # Agrupamento
        df_tree = df_tree.groupby(["SG_UF", "ID_MN_RESI", "DOENCA"]).size().reset_index(name="count")
        
        # Opcional: Filtrar apenas cidades com contagem relevante para limpar o gráfico
        # df_tree = df_tree[df_tree['count'] > 5] 

        fig = px.treemap(
            df_tree,
            path=[px.Constant("Brasil"), "SG_UF", "ID_MN_RESI", "DOENCA"], # Adiciona um nó raiz
            values="count",
            color="count", # Cor baseada na quantidade (mais intuitivo)
            color_continuous_scale="Viridis", # Uma paleta mais profissional
            maxdepth=2, # MOSTRA APENAS ESTADOS NO INÍCIO (Clique para aprofundar)
        )

        # Ajustes de layout e interatividade
        fig.update_traces(
            hovertemplate="<b>%{label}</b><br>Casos: %{value}<br>Pai: %{parent}",
            textinfo="label+value" # Mostra o nome e o valor dentro do quadrado
        )

        fig.update_layout(
            margin=dict(t=30, l=10, r=10, b=10),
            height=600 # Aumentar a altura ajuda na legibilidade
        )

        st.plotly_chart(fig, use_container_width=True)

# ========================
# 📈 ABA 5 - TEMPORAL
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
# 📊 ABA 6 - DISTRIBUIÇÕES
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