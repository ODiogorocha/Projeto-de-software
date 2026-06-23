import pandas as pd
import os
import glob

def carregar_dados(caminho):
    print(f"Buscando dados em: {caminho}")
    
    # Colunas essenciais para o dashboard rodar leve
    colunas_uteis = [
        "DT_NOTIFIC", "SG_UF", "CLASSI_FIN", "NU_IDADE_N", 
        "CS_SEXO", "EVOLUCAO", "CO_MUN_RES", "ID_MN_RESI"  # <-- ADICIONAMOS AQUI!
    ]
    
    if os.path.isdir(caminho):
        print("É um diretório! Buscando arquivos lá dentro...")
        
        arquivos_parquet = glob.glob(os.path.join(caminho, "*.parquet"))
        if arquivos_parquet:
            print("Lendo Parquet otimizado...")
            colunas_existentes = pd.read_parquet(arquivos_parquet[0], engine='pyarrow').columns
            cols = [c for c in colunas_uteis if c in colunas_existentes]
            return pd.read_parquet(caminho, engine='pyarrow', columns=cols)
            
        arquivos_csv = glob.glob(os.path.join(caminho, "*.csv"))
        arquivos_csv = [f for f in arquivos_csv if "municipios" not in os.path.basename(f).lower()]
        
        if arquivos_csv:
            print("Lendo CSV otimizado...")
            lista_dfs = []
            for f in arquivos_csv:
                df_temp = pd.read_csv(f, sep=';', encoding='latin1', low_memory=False, usecols=lambda c: c in colunas_uteis)
                lista_dfs.append(df_temp)
            return pd.concat(lista_dfs, ignore_index=True)
            
        return pd.DataFrame()

    elif os.path.isfile(caminho):
        if caminho.endswith('.parquet'):
            colunas_existentes = pd.read_parquet(caminho, engine='pyarrow').columns
            cols = [c for c in colunas_uteis if c in colunas_existentes]
            return pd.read_parquet(caminho, engine='pyarrow', columns=cols)
        elif caminho.endswith('.csv'):
            return pd.read_csv(caminho, sep=';', encoding='latin1', low_memory=False, usecols=lambda c: c in colunas_uteis)
            
    return pd.DataFrame()


def tratar_dados(df):
    print("Tratando dados...")
    if df.empty: return df
    
    if "DT_NOTIFIC" in df.columns:
        df["DT_NOTIFIC"] = pd.to_datetime(df["DT_NOTIFIC"], errors='coerce')
    if "NU_IDADE_N" in df.columns:
        df["NU_IDADE_N"] = pd.to_numeric(df["NU_IDADE_N"], errors='coerce')
    if "CS_SEXO" in df.columns:
        df["SEXO"] = df["CS_SEXO"].map({"M": 0, "F": 1})
    if "EVOLUCAO" in df.columns:
        df["OBITO"] = df["EVOLUCAO"].apply(lambda x: 1 if x == 2 else 0 if pd.notnull(x) else None)
        
    return df


def carregar_coordenadas(caminho):
    print("Carregando base de coordenadas...")
    if os.path.exists(caminho):
        if caminho.endswith('.parquet'):
            return pd.read_parquet(caminho, engine='pyarrow')
        else:
            return pd.read_csv(caminho, sep=',', encoding='utf-8')
    return None


def mesclar_coordenadas(df_principal, df_coords):
    print("Cruzando dados epidemiológicos com coordenadas...")
    
    if df_coords is not None and not df_principal.empty:
        if "CO_MUN_RES" in df_principal.columns and "codigo_ibge" in df_coords.columns:
            
            # Remove a coluna ID_MN_RESI original (se existir) para evitar duplicatas, 
            # pois vamos usar os nomes limpinhos do seu arquivo de municípios!
            if "ID_MN_RESI" in df_principal.columns:
                df_principal = df_principal.drop(columns=["ID_MN_RESI"])
            
            # Cria a chave de cruzamento (6 primeiros dígitos do IBGE)
            df_principal["cod_ibge_join"] = df_principal["CO_MUN_RES"].astype(str).str.replace(r'\.0$', '', regex=True).str[:6]
            df_coords["cod_ibge_join"] = df_coords["codigo_ibge"].astype(str).str.replace(r'\.0$', '', regex=True).str[:6]
            
            # Traz a 'cidade', 'latitude', 'longitude' e 'populacao' do seu CSV
            df_merged = pd.merge(
                df_principal,
                df_coords[["cod_ibge_join", "cidade", "latitude", "longitude", "populacao"]],
                on="cod_ibge_join", 
                how="left"
            )
            
            # Renomeia para o padrão exato que o Dashboard (app.py) espera!
            df_merged = df_merged.rename(columns={
                "populacao": "POPULACAO",
                "cidade": "ID_MN_RESI"
            })
            
            # Limpa a coluna temporária
            return df_merged.drop(columns=["cod_ibge_join"])
            
    return df_principal