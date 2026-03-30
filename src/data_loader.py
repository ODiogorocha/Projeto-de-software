import pandas as pd

def carregar_dados(caminho):
    print("Carregando dados...")

    df = pd.read_csv(
        caminho,
        sep=';',
        encoding='latin1',
        low_memory=False
    )

    print(f"Total de registros: {len(df)}")
    return df


def tratar_dados(df):
    print("Tratando dados (sem excluir)...")

    # Data
    df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors='coerce')

    # Idade
    df["NU_IDADE_N"] = pd.to_numeric(df["NU_IDADE_N"], errors='coerce')

    # Sexo → numérico
    df["SEXO"] = df["CS_SEXO"].map({"M": 0, "F": 1})

    # Óbito
    df["OBITO"] = df["EVOLUCAO"].apply(
        lambda x: 1 if x == 2 else 0 if pd.notnull(x) else None
    )

    return df