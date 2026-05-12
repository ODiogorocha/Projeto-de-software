import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

ARQUIVO = "/home/gabriel/Projetos/Projeto-de-software/docs/database/INFLUD19-26-06-2025.csv"


# ========================
# CARREGAMENTO
# ========================

def carregar_dados(caminho):
    print("Carregando dados...")

    colunas = [
        "SG_UF", "DT_NOTIFIC", "CLASSI_FIN",
        "ID_MUNICIP", "CS_SEXO",
        "NU_IDADE_N", "EVOLUCAO"
    ]

    df = pd.read_csv(
        caminho,
        sep=';',
        usecols=colunas,
        encoding='latin1',
        low_memory=False
    )

    print(f"Total de registros: {len(df)}")
    return df


# ========================
# TRATAMENTO
# ========================

def tratar_dados(df):
    print("Tratando dados...")

    df = df.dropna(subset=["SG_UF", "DT_NOTIFIC"])

    df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors='coerce')
    df = df.dropna(subset=["DT_NOTIFIC"])

    df["NU_IDADE_N"] = pd.to_numeric(df["NU_IDADE_N"], errors='coerce')

    # Filtrar COVID
    df = df[df["CLASSI_FIN"] == 5]

    return df


# ========================
# VISUALIZAÇÕES AVANÇADAS
# ========================

def heatmap_estado_mes(df):
    print("Gerando heatmap estado x tempo...")

    df["ANO_MES"] = df["DT_NOTIFIC"].dt.to_period("M").astype(str)

    tabela = pd.crosstab(df["SG_UF"], df["ANO_MES"])

    plt.figure(figsize=(12, 8))
    plt.imshow(tabela, aspect='auto')
    plt.colorbar(label="Casos")

    plt.yticks(range(len(tabela.index)), tabela.index)
    plt.xticks(range(len(tabela.columns)), tabela.columns, rotation=90)

    plt.title("Heatmap: Casos por Estado ao Longo do Tempo")
    plt.tight_layout()
    plt.show()


def heatmap_idade_obito(df):
    print("Heatmap idade x óbito...")

    df["FAIXA_IDADE"] = pd.cut(
        df["NU_IDADE_N"],
        bins=[0, 10, 20, 40, 60, 80, 120]
    )

    tabela = pd.crosstab(df["FAIXA_IDADE"], df["EVOLUCAO"])

    plt.figure()
    plt.imshow(tabela, aspect='auto')
    plt.colorbar()

    plt.yticks(range(len(tabela.index)), tabela.index)
    plt.xticks(range(len(tabela.columns)), tabela.columns)

    plt.title("Heatmap: Idade vs Evolução")
    plt.show()


def grafico_colorido_estado(df):
    contagem = df["SG_UF"].value_counts()

    cores = plt.cm.viridis(np.linspace(0, 1, len(contagem)))

    plt.figure()
    contagem.plot(kind="bar", color=cores)

    plt.title("Casos por Estado (Colorido)")
    plt.xlabel("Estado")
    plt.ylabel("Casos")
    plt.show()


def scatter_idade_tempo(df):
    print("Scatter idade x tempo...")

    plt.figure()

    plt.scatter(
        df["DT_NOTIFIC"],
        df["NU_IDADE_N"],
        alpha=0.3
    )

    plt.title("Idade ao longo do tempo")
    plt.xlabel("Data")
    plt.ylabel("Idade")
    plt.show()


def boxplot_idade(df):
    print("Boxplot idade por desfecho...")

    df.boxplot(column="NU_IDADE_N", by="EVOLUCAO")

    plt.title("Distribuição de idade por evolução")
    plt.suptitle("")
    plt.xlabel("Evolução")
    plt.ylabel("Idade")
    plt.show()


def evolucao_media_movel(df):
    print("Média móvel de casos...")

    df["DATA"] = df["DT_NOTIFIC"]
    serie = df.groupby("DATA").size()

    media = serie.rolling(window=7).mean()

    plt.figure()
    plt.plot(serie, alpha=0.4, label="Diário")
    plt.plot(media, label="Média móvel 7 dias")

    plt.legend()
    plt.title("Evolução com Média Móvel")
    plt.show()


# ========================
# MINERAÇÃO DE DADOS
# ========================

def correlacao(df):
    print("Calculando correlação...")

    df_temp = df.copy()

    df_temp["SEXO"] = df_temp["CS_SEXO"].map({"M": 0, "F": 1})

    matriz = df_temp[["NU_IDADE_N", "SEXO", "EVOLUCAO"]].corr()

    plt.figure()
    plt.imshow(matriz)
    plt.colorbar()

    plt.xticks(range(len(matriz.columns)), matriz.columns)
    plt.yticks(range(len(matriz.index)), matriz.index)

    plt.title("Mapa de Correlação")
    plt.show()

    print("\nMatriz de correlação:")
    print(matriz)


def clusterizacao_simples(df):
    print("Clusterização simples (manual)...")

    df_cluster = df[["NU_IDADE_N", "EVOLUCAO"]].dropna()

    # Criando clusters simples (heurística)
    df_cluster["GRUPO_RISCO"] = pd.cut(
        df_cluster["NU_IDADE_N"],
        bins=[0, 20, 40, 60, 120],
        labels=["Muito Baixo", "Baixo", "Médio", "Alto"]
    )

    print("\nDistribuição por grupo de risco:")
    print(df_cluster["GRUPO_RISCO"].value_counts())


# ========================
# MAIN
# ========================

def main():
    df = carregar_dados(ARQUIVO)
    df = tratar_dados(df)

    if df.empty:
        print("Sem dados.")
        return

    # Visualizações
    grafico_colorido_estado(df)
    heatmap_estado_mes(df)
    heatmap_idade_obito(df)
    scatter_idade_tempo(df)
    boxplot_idade(df)
    evolucao_media_movel(df)

    # Mineração
    correlacao(df)
    clusterizacao_simples(df)


if __name__ == "__main__":
    main()