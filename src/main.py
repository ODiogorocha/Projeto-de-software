import pandas as pd
import matplotlib.pyplot as plt

ARQUIVO = "/home/diogo/Documentos/codigos/Projeto-de-software/docs/database/INFLUD19-26-06-2025.csv"

def carregar_dados(caminho):
    print("Carregando dados...")
    df = pd.read_csv(caminho, sep=';', low_memory=False)
    return df

def tratar_dados(df):
    print("Tratando dados...")

    # Seleciona colunas relevantes (podem variar conforme dataset)
    colunas = ["SG_UF", "DT_NOTIFIC", "CLASSI_FIN"]
    df = df[colunas]

    # Remove valores nulos
    df = df.dropna()

    # Converte data
    df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors='coerce')

    # Remove datas inválidas
    df = df.dropna(subset=["DT_NOTIFIC"])

    return df

def casos_por_estado(df):
    print("Gerando gráfico por estado...")

    contagem = df["SG_UF"].value_counts().sort_values(ascending=False)

    plt.figure()
    contagem.plot(kind="bar")
    plt.title("Casos de SRAG por Estado")
    plt.xlabel("Estado")
    plt.ylabel("Número de Casos")
    plt.tight_layout()
    plt.show()

def evolucao_temporal(df):
    print("Gerando série temporal...")

    df["ANO_MES"] = df["DT_NOTIFIC"].dt.to_period("M")
    serie = df.groupby("ANO_MES").size()

    plt.figure()
    serie.plot()
    plt.title("Evolução Temporal dos Casos")
    plt.xlabel("Tempo")
    plt.ylabel("Número de Casos")
    plt.tight_layout()
    plt.show()

def top_municipios(df):
    if "ID_MUNICIP" not in df.columns:
        print("Coluna de município não encontrada no dataset.")
        return

    print("Top municípios...")
    top = df["ID_MUNICIP"].value_counts().head(10)

    plt.figure()
    top.plot(kind="bar")
    plt.title("Top 10 Municípios com Mais Casos")
    plt.xlabel("Município")
    plt.ylabel("Casos")
    plt.tight_layout()
    plt.show()

def main():
    df = carregar_dados(ARQUIVO)
    df = tratar_dados(df)

    casos_por_estado(df)
    evolucao_temporal(df)
    top_municipios(df)

if __name__ == "__main__":
    main()