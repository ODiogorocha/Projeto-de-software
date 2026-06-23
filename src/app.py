import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import os

from data_loader import carregar_dados, tratar_dados, carregar_coordenadas, mesclar_coordenadas
from styles import carregar_estilos

# ========================
# CONFIGURAÇÕES DA PÁGINA
# ========================
st.set_page_config(layout="wide", page_title="Dashboard SRAG", page_icon="🦠")
st.markdown(carregar_estilos(), unsafe_allow_html=True)

st.markdown("""
<style>
.hide-sidebar section[data-testid="stSidebar"] { display: none !important; }
.hide-sidebar header[data-testid="stHeader"]   { display: none !important; }
[data-testid="metric-container"] > div          { display:flex; flex-direction:column; align-items:center; text-align:center; }
[data-testid="metric-container"] label          { font-size:0.85rem; color:rgba(255,255,255,0.6); letter-spacing:0.05em; text-transform:uppercase; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size:2rem; font-weight:700; color:white; }
</style>
""", unsafe_allow_html=True)

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

# Caminhos Dinâmicos
# Caminhos Dinâmicos
# Descobre a pasta onde o app.py está (a pasta src/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Pasta onde estão os dados da doença
PASTA_DADOS = os.path.join(ROOT_DIR, "docs", "database")

# Pasta onde está o arquivo de cidades (uma pasta antes)
PASTA_DOCS = os.path.join(ROOT_DIR, "docs") 

MAPA = os.path.join(BASE_DIR, "brasil_estados.geojson")
ARQUIVO_ML = os.path.join(ROOT_DIR, "municipios_risco_doenca.csv")

# Agora ele procura corretamente na pasta docs/
cidade_parquet = os.path.join(PASTA_DOCS, "municipios.parquet")
cidade_csv = os.path.join(PASTA_DOCS, "municipios.csv")

if os.path.exists(cidade_parquet):
    ARQUIVO_CIDADES = cidade_parquet
else:
    ARQUIVO_CIDADES = cidade_csv

if st.session_state.pagina == "inicio":

    st.markdown('<style>section[data-testid="stSidebar"]{display:none!important;}header[data-testid="stHeader"]{display:none!important;}</style>', unsafe_allow_html=True)
    st.markdown('<style>.block-container{padding-top:2rem!important;max-width:960px;margin:auto;}</style>', unsafe_allow_html=True)

    CARD = """
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
        border-top:3px solid {cor};border-radius:12px;padding:1.3rem 1.4rem;height:100%;">
        <div style="font-size:1.5rem;margin-bottom:0.5rem;">{icone}</div>
        <div style="color:white;font-weight:700;font-size:0.95rem;margin-bottom:0.45rem;">{titulo}</div>
        <div style="color:rgba(255,255,255,0.55);font-size:0.87rem;line-height:1.65;">{texto}</div>
    </div>"""

    GUIA = """
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
        border-left:3px solid {cor};border-radius:12px;padding:1.3rem 1.4rem;">
        <div style="font-size:1.4rem;margin-bottom:0.45rem;">{icone}</div>
        <div style="color:white;font-weight:700;font-size:0.95rem;margin-bottom:0.4rem;">{titulo}</div>
        <div style="color:rgba(255,255,255,0.55);font-size:0.87rem;line-height:1.65;">{texto}</div>
    </div>"""

    FICHA = """
    <div style="margin-bottom:0.5rem;">
        <div style="color:rgba(255,255,255,0.4);font-size:0.7rem;text-transform:uppercase;
            letter-spacing:0.1em;">{label}</div>
        <div style="color:white;font-weight:600;font-size:0.92rem;">{valor}</div>
    </div>"""

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:3.5rem 0 1.8rem 0;">
        <div style="display:inline-flex;gap:0.5rem;align-items:center;
            background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);
            border-radius:999px;padding:0.35rem 1.2rem;font-size:0.75rem;
            color:rgba(255,255,255,0.5);letter-spacing:0.12em;text-transform:uppercase;
            margin-bottom:1.6rem;">
            OpenDataSUS &nbsp;·&nbsp; SIVEP-Gripe &nbsp;·&nbsp; Ministério da Saúde
        </div>
        <h1 style="color:white;font-size:clamp(1.9rem,4vw,3.1rem);font-weight:800;
            line-height:1.2;margin:0 0 1.1rem 0;">
            Visualização Centralizada de<br>Informações de Saúde (SUS)
        </h1>
        <p style="color:rgba(255,255,255,0.5);font-size:1.05rem;max-width:640px;
            margin:0 auto 0.6rem auto;line-height:1.75;">
            Transformamos grandes volumes de dados públicos em gráficos e análises acessíveis,
            apoiando a compreensão de padrões epidemiológicos e a identificação de
            zonas de maior incidência de doenças respiratórias no Brasil.
        </p>
        <p style="color:rgba(255,255,255,0.3);font-size:0.82rem;margin-bottom:2rem;">
            Projeto acadêmico · Dados abertos · Transparência pública
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_btn = st.columns([1, 2, 1])[1]
    with col_btn:
        if st.button("Acessar o Dashboard →", use_container_width=True, type="primary"):
            st.session_state.pagina = "dashboard"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Objetivos ─────────────────────────────────────────────────────────
    st.markdown('<h2 style="color:white;font-size:1.35rem;font-weight:700;margin-bottom:1rem;">Objetivos do Projeto</h2>', unsafe_allow_html=True)

    col_a, col_b, col_c, col_d = st.columns(4)
    OBJ = """
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
        border-radius:12px;padding:1.1rem 1.2rem;text-align:center;">
        <div style="font-size:1.4rem;margin-bottom:0.5rem;">{icone}</div>
        <div style="color:white;font-weight:600;font-size:0.88rem;line-height:1.5;">{texto}</div>
    </div>"""
    with col_a:
        st.markdown(OBJ.format(icone="🗄️", texto="Centralizar dados de saúde de fontes públicas nacionais"), unsafe_allow_html=True)
    with col_b:
        st.markdown(OBJ.format(icone="📊", texto="Criar visualizações que facilitam a análise epidemiológica"), unsafe_allow_html=True)
    with col_c:
        st.markdown(OBJ.format(icone="📍", texto="Identificar regiões com maior incidência de doenças"), unsafe_allow_html=True)
    with col_d:
        st.markdown(OBJ.format(icone="💡", texto="Apoiar tomadas de decisão baseadas em dados concretos"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── O que é SRAG ──────────────────────────────────────────────────────
    st.markdown('<h2 style="color:white;font-size:1.35rem;font-weight:700;margin-bottom:1rem;">O que é SRAG?</h2>', unsafe_allow_html=True)

    col_e, col_f, col_g = st.columns(3)
    with col_e:
        st.markdown(CARD.format(
            cor="rgba(255,180,50,0.8)", icone="🫁",
            titulo="Síndrome Respiratória Aguda Grave",
            texto="É quando uma infecção respiratória — como gripe ou COVID-19 — se agrava a ponto de exigir internação hospitalar ou causar dificuldade severa para respirar."
        ), unsafe_allow_html=True)
    with col_f:
        st.markdown(CARD.format(
            cor="rgba(80,200,180,0.8)", icone="🔬",
            titulo="Causada por múltiplos vírus",
            texto="Não é uma doença única. A SRAG pode ser causada por Influenza, COVID-19, Vírus Sincicial Respiratório (VSR) e outros agentes respiratórios identificados pelo SIVEP-Gripe."
        ), unsafe_allow_html=True)
    with col_g:
        st.markdown(CARD.format(
            cor="rgba(130,100,255,0.8)", icone="⚠️",
            titulo="Grupos de maior risco",
            texto="Idosos, crianças pequenas, gestantes e pessoas com doenças crônicas (diabetes, hipertensão, doenças pulmonares) têm maior chance de desenvolver a forma grave da síndrome."
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Fontes de dados ───────────────────────────────────────────────────
    st.markdown('<h2 style="color:white;font-size:1.35rem;font-weight:700;margin-bottom:1rem;">Fontes de Dados</h2>', unsafe_allow_html=True)

    col_h, col_i = st.columns([3, 2])
    with col_h:
        st.markdown("""
        <p style="color:rgba(255,255,255,0.65);line-height:1.85;font-size:0.95rem;">
            Os dados utilizados neste projeto são provenientes de bases públicas abertas do governo brasileiro.
            O conjunto principal é o <strong style="color:white;">SRAG 2021–2022</strong>, disponível em
            <strong style="color:white;">dados.gov.br</strong>, coletado pelo sistema
            <strong style="color:white;">SIVEP-Gripe</strong> — o principal sistema nacional de
            vigilância de doenças respiratórias graves, alimentado por hospitais sentinela
            em todo o território nacional.<br><br>
            Os dados possuem granularidade por <strong style="color:white;">município</strong>,
            <strong style="color:white;">estado</strong>,
            <strong style="color:white;">semana epidemiológica</strong> e
            <strong style="color:white;">faixa etária</strong>, permitindo análises
            detalhadas de padrões geográficos e temporais.
        </p>
        """, unsafe_allow_html=True)

    with col_i:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
            border-radius:14px;padding:1.4rem 1.6rem;display:grid;gap:0.75rem;">
            {FICHA.format(label="Fontes", valor="OpenDataSUS · dados.gov.br · Governo do RS")}
            {FICHA.format(label="Sistema de coleta", valor="SIVEP-Gripe / Ministério da Saúde")}
            {FICHA.format(label="Período coberto", valor="2019 – 2026")}
            {FICHA.format(label="Granularidade", valor="Município · Estado · Semana · Faixa etária")}
            {FICHA.format(label="Atualização", valor="Semanal")}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Limitações ────────────────────────────────────────────────────────
    st.markdown('<h2 style="color:white;font-size:1.35rem;font-weight:700;margin-bottom:0.8rem;">Limitações dos Dados</h2>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:rgba(255,255,255,0.5);font-size:0.88rem;line-height:1.7;max-width:780px;">
        Como toda base de dados de saúde pública, este conjunto pode conter
        <strong style="color:rgba(255,255,255,0.75);">erros de preenchimento</strong> nos registros hospitalares,
        <strong style="color:rgba(255,255,255,0.75);">subnotificação</strong> de casos (especialmente em regiões com menos acesso à saúde),
        <strong style="color:rgba(255,255,255,0.75);">atualizações tardias</strong> com dados retroativos, e
        <strong style="color:rgba(255,255,255,0.75);">diferenças de padrão</strong> entre bases estaduais e federais.
        Recomendamos interpretar os resultados com esse contexto em mente.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── O que você vai encontrar ──────────────────────────────────────────
    st.markdown('<h2 style="color:white;font-size:1.35rem;font-weight:700;margin-bottom:1rem;">O que você vai encontrar no painel</h2>', unsafe_allow_html=True)

    col_j, col_k, col_l = st.columns(3)
    with col_j:
        st.markdown(GUIA.format(
            cor="rgba(255,180,50,0.8)", icone="📊",
            titulo="Visão Geral",
            texto="Panorama nacional: quais doenças predominam, quais estados concentram mais casos, distribuição de idade dos pacientes e desfechos clínicos."
        ), unsafe_allow_html=True)
    with col_k:
        st.markdown(GUIA.format(
            cor="rgba(80,200,180,0.8)", icone="🗺️",
            titulo="Visão Geográfica",
            texto="Mapa interativo do Brasil com identificação de zonas críticas (hotspots). Alterne entre mapa por estado e mapa de calor por município normalizado por população."
        ), unsafe_allow_html=True)
    with col_l:
        st.markdown(GUIA.format(
            cor="rgba(130,100,255,0.8)", icone="📈",
            titulo="Evolução Temporal",
            texto="Séries temporais mensais mostrando se os casos estão subindo, estabilizando ou caindo — separados por tipo de doença para comparação direta."
        ), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col_btn2 = st.columns([1, 2, 1])[1]
    with col_btn2:
        if st.button("Explorar os dados →", use_container_width=True, type="primary", key="btn_bottom"):
            st.session_state.pagina = "dashboard"
            st.rerun()

    st.markdown("""
    <p style="text-align:center;color:rgba(255,255,255,0.2);font-size:0.75rem;margin-top:2rem;padding-bottom:2rem;">
        Projeto acadêmico desenvolvido com dados abertos do governo brasileiro · Transparência e ciência de dados a serviço da saúde pública
    </p>
    """, unsafe_allow_html=True)

    st.stop()

# ========================
# CACHE E CARREGAMENTO
# ========================
@st.cache_data
def load_data():
    # Passamos a pasta mãe! O data loader procura os dados inteligentemente.
    df_bruto   = carregar_dados(PASTA_DADOS)
    df_tratado = tratar_dados(df_bruto)
    df_coords  = carregar_coordenadas(ARQUIVO_CIDADES)
    return mesclar_coordenadas(df_tratado, df_coords)

@st.cache_data
def load_mapa():
    try:
        return gpd.read_file(MAPA)
    except:
        return None

df_total = load_data()
df = df_total.copy()
geo = load_mapa()

def aplicar_estilo(fig, altura=450):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white", family="Arial"), margin=dict(t=50, b=20, l=20, r=20), height=altura,
        xaxis=dict(showgrid=False, zeroline=False, color="white"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", zeroline=False, color="white")
    )
    return fig
COR_PRINCIPAL = "Plasma"

# ── Doenças ───────────────────────────────────────────────────────────────
mapa_doencas = {1:"Influenza", 2:"Outros vírus", 3:"Outros agentes",
                4:"SRAG não especificado", 5:"COVID-19"}
df["DOENCA"] = df["CLASSI_FIN"].map(mapa_doencas)
df = df.dropna(subset=["DOENCA"])

# ── Regiões ───────────────────────────────────────────────────────────────
REGIOES = {
    "Norte":        ["AC","AM","AP","PA","RO","RR","TO"],
    "Nordeste":     ["AL","BA","CE","MA","PB","PE","PI","RN","SE"],
    "Centro-Oeste": ["DF","GO","MS","MT"],
    "Sudeste":      ["ES","MG","RJ","SP"],
    "Sul":          ["PR","RS","SC"],
}

# ── Header do dashboard com botão voltar ─────────────────────────────────
col_title, col_back = st.columns([6, 1])
with col_title:
    st.title("Dashboard SRAG — Análise de Doenças Respiratórias")
with col_back:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Início", help="Voltar à página de apresentação"):
        st.session_state.pagina = "inicio"
        st.rerun()

# ========================
# SIDEBAR — FILTROS
# ========================

st.sidebar.header("Filtros")

if st.sidebar.button("Limpar todos os filtros", use_container_width=True):
    st.rerun()

st.sidebar.divider()

todos_estados = sorted(df["SG_UF"].dropna().unique())

st.sidebar.subheader("Localização")

regiao_sel = st.sidebar.multiselect(
    "Região", options=list(REGIOES.keys()), default=[],
    placeholder="Todas as regiões",
    help="Filtre primeiro por região para facilitar a seleção de estados."
)

estados_pre = [e for r in regiao_sel for e in REGIOES[r] if e in todos_estados] if regiao_sel else []

estado = st.sidebar.multiselect(
    "Estado (opcional)", options=todos_estados, default=estados_pre,
    placeholder="Todos os estados",
    help="Deixe em branco para incluir todos os estados."
)

estados_ativos = estado if estado else todos_estados
df = df[df["SG_UF"].isin(estados_ativos)]

st.sidebar.subheader("Doença")

doenca = st.sidebar.multiselect(
    "Tipo de doença", options=sorted(df["DOENCA"].dropna().unique()), default=[],
    placeholder="Todas as doenças",
    help="Deixe em branco para incluir todas as doenças."
)
doencas_ativas = doenca if doenca else sorted(df["DOENCA"].dropna().unique())
df = df[df["DOENCA"].isin(doencas_ativas)]

if "POPULACAO" in df.columns:
    st.sidebar.subheader("Tamanho da Cidade")
    col_pop1, col_pop2 = st.sidebar.columns(2)
    pop_min = col_pop1.number_input("Mínimo (hab.)", min_value=0, max_value=15_000_000, value=0, step=10_000)
    pop_max = col_pop2.number_input("Máximo (hab.)", min_value=0, max_value=15_000_000, value=3_000_000, step=10_000)
    df = df[(df["POPULACAO"] >= pop_min) & (df["POPULACAO"] <= pop_max)]

NOMES_MESES = {
    1:"Janeiro", 2:"Fevereiro", 3:"Março",    4:"Abril",
    5:"Maio",    6:"Junho",     7:"Julho",     8:"Agosto",
    9:"Setembro",10:"Outubro",  11:"Novembro", 12:"Dezembro"
}

if "DT_NOTIFIC" in df.columns:
    st.sidebar.subheader("Período")
    anos_disponiveis = sorted(df["DT_NOTIFIC"].dt.year.dropna().astype(int).unique())
    anos = st.sidebar.multiselect("Ano", options=anos_disponiveis, default=[],
                                  placeholder="Todos os anos")
    meses = st.sidebar.multiselect("Mês", options=list(NOMES_MESES.keys()), default=[],
                                   placeholder="Todos os meses",
                                   format_func=lambda x: NOMES_MESES[x])
    df = df[df["DT_NOTIFIC"].dt.year.isin(anos if anos else anos_disponiveis)]
    df = df[df["DT_NOTIFIC"].dt.month.isin(meses if meses else list(NOMES_MESES.keys()))]

# ── Estado vazio ──────────────────────────────────────────────────────────
if df.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados. Tente ampliar os critérios na barra lateral.")
    st.stop()

# ========================
# KPIs
# ========================

obitos_pct = round((df["OBITO"].sum() / len(df)) * 100, 2) if "OBITO" in df.columns and len(df) > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Casos",   f"{len(df):,}".replace(",", "."),
            help="Total de registros com base nos filtros aplicados.")
col2.metric("Estados",          df["SG_UF"].nunique(),
            help="Número de estados com pelo menos um caso registrado.")
col3.metric("Tipos de Doença",  df["DOENCA"].nunique(),
            help="Quantidade de tipos de doenças presentes nos dados filtrados.")
col4.metric("Letalidade",       f"{obitos_pct}%",
            help="Percentual de pessoas que contraíram a doença e vieram a óbito.")

st.divider()

# ========================
# ABAS
# ========================

tab1, tab2, tab3, tab4= st.tabs(["Visão Geral", "Visão Geográfica", "Evolução Temporal", "IA, provisorio"])

# ── Aba 1 — Visão Geral ───────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        df_pie = df["DOENCA"].value_counts().reset_index()
        df_pie.columns = ["DOENCA", "count"]
        fig = px.bar(df_pie, x="count", y="DOENCA", orientation="h",
                     title="<b>Casos por Tipo de Doença</b>",
                     color="count", color_continuous_scale=COR_PRINCIPAL,
                     labels={"count":"Casos","DOENCA":"Doença"})
        st.plotly_chart(aplicar_estilo(fig, 400), use_container_width=True)

    with col2:
        df_bar = df["SG_UF"].value_counts().reset_index()
        df_bar.columns = ["SG_UF", "count"]
        fig = px.bar(df_bar, x="SG_UF", y="count",
                     title="<b>Casos por Estado</b>",
                     color="count", color_continuous_scale=COR_PRINCIPAL,
                     labels={"count":"Casos","SG_UF":"UF"})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color="white", xaxis={'categoryorder':'total descending'},
                          coloraxis_showscale=False, margin=dict(t=50,b=20,l=20,r=20))
        fig.update_traces(marker_line_color='rgba(0,0,0,0)')
        st.plotly_chart(aplicar_estilo(fig, 400), use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)

    with col3:
        fig = px.histogram(df, x="NU_IDADE_N", nbins=30,
                           title="<b>Distribuição de Idade dos Pacientes</b>",
                           color_discrete_sequence=["#ff7b00"],
                           labels={"NU_IDADE_N":"Idade"})
        st.plotly_chart(aplicar_estilo(fig, 400), use_container_width=True)

    with col4:
        if "OBITO" in df.columns:
            fig = px.box(df, x="OBITO", y="NU_IDADE_N",
                         title="<b>Faixa de Idade por Desfecho</b>",
                         color="OBITO",
                         color_discrete_sequence=["#ef4444","#ffb703"],
                         labels={"NU_IDADE_N":"Idade","OBITO":"Óbito"})
            st.plotly_chart(aplicar_estilo(fig, 400), use_container_width=True)

# ── Aba 2 — Visão Geográfica ──────────────────────────────────────────────
with tab2:
    st.subheader("Visão Geográfica")

    tipo_mapa = st.radio(
        "Escolha o tipo de visualização:",
        options=["Mapa por Estado", "Mapa de Calor por Município"],
        horizontal=True,
        help="Mapa por Estado: coloração por volume total. Mapa de Calor: intensidade por município por 100 mil hab."
    )

    st.divider()

    estados_disponiveis = sorted(df["SG_UF"].dropna().unique())
    estado_geo = st.selectbox("Focar em um estado específico (opcional)",
                              ["Todos"] + estados_disponiveis)

    df_map = df.copy()
    if estado_geo != "Todos":
        df_map = df_map[df_map["SG_UF"] == estado_geo]

    cidade_sel = "Todas"
    if estado_geo != "Todos" and "ID_MN_RESI" in df_map.columns:
        cidade_sel = st.selectbox("Focar em uma cidade específica (opcional)",
                                  ["Todas"] + sorted(df_map["ID_MN_RESI"].dropna().unique()))
        if cidade_sel != "Todas":
            df_map = df_map[df_map["ID_MN_RESI"] == cidade_sel]

    if tipo_mapa == "Mapa por Estado":
        casos_estado = df["SG_UF"].value_counts().reset_index()
        casos_estado.columns = ["SG_UF", "casos"]
        geo_plot = geo.copy().merge(casos_estado, left_on="sigla", right_on="SG_UF", how="left").to_crs(epsg=4326)
        fig = px.choropleth_map(
            geo_plot, geojson=geo_plot.__geo_interface__, locations=geo_plot.index,
            color="casos", hover_name="name", hover_data={"SG_UF":True,"casos":True},
            map_style="carto-positron", zoom=3.3, center={"lat":-15.5,"lon":-55},
            opacity=0.7, color_continuous_scale=COR_PRINCIPAL,
            title="<b>Distribuição de Casos por Estado</b>"
        )
        fig.update_layout(height=750, margin={"r":0,"t":50,"l":0,"b":0},
                          coloraxis_colorbar=dict(title="Nº Casos",thicknessmode="pixels",
                          thickness=15,lenmode="pixels",len=300,yanchor="middle",y=0.5))
        st.plotly_chart(aplicar_estilo(fig, 750), use_container_width=True)

    else:
        if "latitude" not in df_map.columns or "longitude" not in df_map.columns:
            st.warning("Colunas de latitude/longitude não encontradas.")
        elif len(df_map) == 0:
            st.warning("Nenhum dado disponível para os filtros selecionados.")
        else:
            zoom_nivel = 10 if cidade_sel != "Todas" else (5 if estado_geo != "Todos" else 3.5)
            raio       = 50 if cidade_sel != "Todas" else 15
            casos_geo  = (df_map.groupby(["ID_MN_RESI","latitude","longitude","POPULACAO"])
                          .size().reset_index(name="casos"))
            casos_geo["casos_100k"] = (casos_geo["casos"] / casos_geo["POPULACAO"]) * 100000
            fig = px.density_map(
                casos_geo, lat="latitude", lon="longitude", z="casos_100k",
                radius=raio, zoom=zoom_nivel,
                center={"lat":casos_geo["latitude"].mean(),"lon":casos_geo["longitude"].mean()},
                color_continuous_scale=COR_PRINCIPAL, map_style="carto-positron",
                title="<b>Mapa de Calor — Casos por 100 mil Habitantes</b>",
                hover_name="ID_MN_RESI",
                hover_data={"latitude":False,"longitude":False,"casos_100k":":.2f"}
            )
            fig.update_layout(height=750, margin={"r":0,"t":50,"l":0,"b":0},
                              coloraxis_colorbar=dict(title="Intensidade",thicknessmode="pixels",
                              thickness=15,lenmode="pixels",len=300,yanchor="middle",y=0.5))
            st.plotly_chart(aplicar_estilo(fig, 750), use_container_width=True)

    st.divider()
    st.subheader("Cidades com Maior Incidência")

    if "ID_MN_RESI" in df_map.columns and "POPULACAO" in df_map.columns and len(df_map) > 0:
        df_city = (df_map.groupby(["ID_MN_RESI","POPULACAO"]).size().reset_index(name="casos"))
        df_city["casos_100k"] = (df_city["casos"] / df_city["POPULACAO"]) * 100000
        df_city = df_city.sort_values("casos_100k", ascending=False)
        fig = px.bar(df_city.head(20), x="ID_MN_RESI", y="casos_100k",
                     title="<b>Top 20 Municípios por Incidência (por 100 mil hab.)</b>",
                     color="casos_100k", color_continuous_scale="Reds",
                     labels={"ID_MN_RESI":"Cidade","casos_100k":"Casos por 100 mil hab."})
        st.plotly_chart(aplicar_estilo(fig, 450), use_container_width=True)
        cidade_critica = df_city.iloc[0]
        st.info(f"Maior incidência em **{cidade_critica['ID_MN_RESI']}** "
                f"com {cidade_critica['casos_100k']:.2f} casos por 100 mil habitantes.")

# ── Aba 3 — Evolução Temporal ─────────────────────────────────────────────
with tab3:
    if "DT_NOTIFIC" not in df.columns:
        st.warning("Coluna de data não encontrada nos dados.")
    else:
        df_temp = df.dropna(subset=["DT_NOTIFIC"]).copy()
        df_temp["DT_NOTIFIC"] = pd.to_datetime(df_temp["DT_NOTIFIC"], errors="coerce")
        df_temp["ANO_MES"] = df_temp["DT_NOTIFIC"].dt.to_period("M").astype(str)
        serie = df_temp.groupby(["ANO_MES","DOENCA"]).size().reset_index(name="casos")
        fig = px.line(serie, x="ANO_MES", y="casos", color="DOENCA",
                      title="<b>Evolução de Casos ao Longo do Tempo</b>",
                      markers=True,
                      labels={"ANO_MES":"Mês/Ano","casos":"Nº de Casos","DOENCA":"Doença"})
        fig.update_traces(mode="lines+markers", line=dict(width=3))
        st.plotly_chart(aplicar_estilo(fig, 600), use_container_width=True)

# Aba 4: Análise para Especialistas e IA
with tab4:
    st.subheader("Focos de Surto e Machine Learning")
    colC, colD = st.columns(2)
    
    with colC:
        if "DT_NOTIFIC" in df.columns and "SG_UF" in df.columns:
            df_heat = df.copy()
            df_heat["ANO_MES"] = pd.to_datetime(df_heat["DT_NOTIFIC"]).dt.to_period("M").astype(str)
            tab_heat = pd.crosstab(df_heat["SG_UF"], df_heat["ANO_MES"])
            fig_heat = px.imshow(tab_heat, aspect="auto", color_continuous_scale="Viridis", title="<b>Densidade: Focos por Estado</b>")
            st.plotly_chart(aplicar_estilo(fig_heat), use_container_width=True)
            
    with colD:
        if os.path.exists(ARQUIVO_ML):
            df_ml = pd.read_csv(ARQUIVO_ML)
            top_covid = df_ml.nlargest(10, 'prob_srag_covid').sort_values('prob_srag_covid')
            fig_ml = px.bar(top_covid, x="prob_srag_covid", y="nome", orientation='h', title="<b>Ranking XGBoost: Risco de COVID Grave</b>", color="prob_srag_covid", color_continuous_scale="Reds")
            st.plotly_chart(aplicar_estilo(fig_ml), use_container_width=True)
        else:
            st.info("Arquivo de ML não encontrado. Execute o modelo para gerar predições de risco.")