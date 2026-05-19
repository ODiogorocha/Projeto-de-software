import pandas as pd

def carregar_dados(caminho):
    print("Carregando dados...")

    df = pd.read_csv(
        caminho,
        sep=';',
        encoding='latin1',
        low_memory=False
    )

    print(f"Total de registros originais: {len(df)}")
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

# ==========================================
# NOVAS FUNÇÕES PARA O MAPA DE CALOR
# ==========================================

def carregar_coordenadas(caminho_csv_municipios):
    print("Carregando base de coordenadas geográficas (CSV)...")
    try:
        # Lê o CSV. Se der erro de formatação com seu arquivo, tente sep=';'
        df_coords = pd.read_csv(caminho_csv_municipios, sep=',', encoding='utf-8')
        return df_coords
    except Exception as e:
        print(f"Erro ao carregar o arquivo de coordenadas: {e}")
        return None


def mesclar_coordenadas(df_principal, df_coords):
    print("Cruzando dados epidemiológicos pelo Código IBGE...")
    
    if df_coords is not None:

        # Verifica colunas necessárias
        if (
            "CO_MUN_RES" in df_principal.columns and
            "codigo_ibge" in df_coords.columns
        ):

            # Padroniza código IBGE
            df_principal["cod_ibge_join"] = (
                df_principal["CO_MUN_RES"]
                .astype(str)
                .str.replace(r'\.0$', '', regex=True)
                .str[:6]
            )

            df_coords["cod_ibge_join"] = (
                df_coords["codigo_ibge"]
                .astype(str)
                .str.replace(r'\.0$', '', regex=True)
                .str[:6]
            )

            # ==========================================
            # IMPORTANTE:
            # TROQUE "populacao" PELO NOME REAL
            # DA COLUNA NO SEU municipios.csv
            # ==========================================

            df_merged = pd.merge(
                df_principal,
                df_coords[
                    [
                        "cod_ibge_join",
                        "latitude",
                        "longitude",
                        "populacao"
                    ]
                ],
                on="cod_ibge_join",
                how="left"
            )

            # Renomeia para padronizar
            df_merged = df_merged.rename(columns={
                "populacao": "POPULACAO"
            })

            # Remove coluna temporária
            df_merged = df_merged.drop(columns=["cod_ibge_join"])

            print(
                f"Total de registros após mesclar coordenadas: "
                f"{len(df_merged)}"
            )

            return df_merged

        else:
            print(
                "AVISO: Coluna 'CO_MUN_RES' ou "
                "'codigo_ibge' não encontrada."
            )

    return df_principal