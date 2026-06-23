import os
import pandas as pd
import matplotlib.pyplot as plt

# Importando as funções do seu novo data_loader
from data_loader import carregar_dados, tratar_dados

# ========================
# CAMINHOS DINÂMICOS
# ========================
# Descobre a pasta atual onde o main.py está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Verifica se o main.py está dentro da 'src' ou já na raiz do projeto
if os.path.basename(BASE_DIR) == "src":
    ROOT_DIR = os.path.dirname(BASE_DIR)  # Volta uma pasta para a raiz
else:
    ROOT_DIR = BASE_DIR                   # Já está na raiz

# Agora aponta de forma segura para os dados
PASTA_DADOS = os.path.join(ROOT_DIR, "docs", "database")

# ========================
# VISUALIZAÇÕES OFFLINE
# ========================
def heatmap_estado_mes(df):
    print("Gerando heatmap estado x tempo...")
    if "DT_NOTIFIC" not in df.columns or "SG_UF" not in df.columns:
        print("Colunas necessárias não encontradas.")
        return

    df_temp = df.dropna(subset=["DT_NOTIFIC", "SG_UF"]).copy()
    df_temp["ANO_MES"] = df_temp["DT_NOTIFIC"].dt.to_period("M").astype(str)
    
    tabela = pd.crosstab(df_temp["SG_UF"], df_temp["ANO_MES"])
    
    plt.figure(figsize=(12, 8))
    plt.imshow(tabela, aspect='auto', cmap='viridis')
    plt.colorbar(label="Casos")
    
    plt.yticks(range(len(tabela.index)), tabela.index)
    plt.xticks(range(len(tabela.columns)), tabela.columns, rotation=90)
    
    plt.title("Heatmap: Casos por Estado ao Longo do Tempo")
    plt.tight_layout()
    plt.show()

def evolucao_media_movel(df):
    print("Calculando média móvel...")
    if "DT_NOTIFIC" not in df.columns:
        print("Coluna de data não encontrada.")
        return

    df_temp = df.dropna(subset=["DT_NOTIFIC"]).copy()
    serie = df_temp.groupby("DT_NOTIFIC").size()
    
    media = serie.rolling(window=7).mean()
    
    plt.figure(figsize=(10, 5))
    plt.plot(serie, alpha=0.4, label="Diário")
    plt.plot(media, label="Média Móvel (7 dias)", color='red', linewidth=2)
    
    plt.legend()
    plt.title("Evolução com Média Móvel (Geral)")
    plt.show()

# ========================
# MAIN
# ========================
def main():
    print(f"Iniciando exploração offline.\nBuscando dados na pasta: {PASTA_DADOS}")
    
    # 1. Carrega os dados (Vai usar a memória otimizada do data_loader.py)
    df_bruto = carregar_dados(PASTA_DADOS)
    
    if df_bruto.empty:
        print("\nNenhum dado foi carregado. Verifique a pasta docs/database.")
        return
        
    # 2. Trata os dados
    df = tratar_dados(df_bruto)
    
    print(f"\nDados carregados com sucesso! Total de registros na memória: {len(df)}")
    
    # 3. Gera as visualizações
    if not df.empty:
        print("Gerando gráficos...")
        heatmap_estado_mes(df)
        evolucao_media_movel(df)
        
    print("\nRotina finalizada.")

if __name__ == "__main__":
    main()