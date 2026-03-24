
# Visualização Centralizada de Informações de Saúde (SUS)

## Descrição do Projeto

Este projeto tem como objetivo a visualização centralizada de informações de saúde pública utilizando dados abertos do governo brasileiro. A proposta é transformar grandes volumes de dados em gráficos e tabelas, facilitando a análise e identificação de padrões epidemiológicos.

O foco principal é analisar a ocorrência de doenças — especialmente Síndrome Respiratória Aguda Grave (SRAG) — e identificar zonas de maior incidência, auxiliando na compreensão da distribuição geográfica das doenças.

---

## Objetivos

* Centralizar dados de saúde provenientes de fontes públicas
* Criar visualizações (gráficos e tabelas) para facilitar a análise
* Identificar regiões com maior incidência de doenças
* Demonstrar padrões epidemiológicos ao longo do tempo
* Apoiar tomadas de decisão baseadas em dados

---

## Fontes de Dados

Os dados utilizados neste projeto são provenientes de bases públicas:

* OpenDataSUS
* dados.gov.br
* Governo do Estado do Rio Grande do Sul

### Dataset principal

* SRAG (2021–2022):
  [https://dados.gov.br/dados/conjuntos-dados/srag-2021-e-2022](https://dados.gov.br/dados/conjuntos-dados/srag-2021-e-2022)

Esses dados são coletados pelo sistema SIVEP-Gripe, que registra casos de doenças respiratórias em todo o Brasil.

Os dados possuem granularidade por:

* Município
* Estado
* Semana epidemiológica
* Faixa etária

---

## Metodologia

### 1. Coleta de Dados

* Download dos datasets em formato CSV ou JSON
* Integração de múltiplas fontes (SUS e dados estaduais)

### 2. Tratamento de Dados

* Limpeza (remoção de valores nulos ou inconsistentes)
* Padronização de colunas
* Filtragem por doença, período e localização

### 3. Análise Exploratória

* Contagem de casos por região
* Agrupamento por:

  * Município
  * Estado
  * Período (ano ou mês)

### 4. Visualização

Serão utilizados:

* Gráficos de barras para incidência por região
* Séries temporais para evolução dos casos
* Mapas de calor para zonas de ocorrência
* Tabelas para dados detalhados

---

## Exemplos de Visualizações

* Distribuição de casos por estado
* Evolução temporal da doença
* Ranking de municípios com maior incidência
* Identificação de zonas críticas (hotspots)

---

## Tecnologias Utilizadas

* Python

  * Pandas
  * Matplotlib / Seaborn / Plotly
* Git e GitHub

---

## Identificação de Zonas de Ocorrência

Uma das principais funcionalidades do projeto é identificar regiões onde determinada doença ocorre com maior frequência.

### Estratégia

1. Agrupar casos por município
2. Calcular frequência de ocorrência
3. Normalizar por população (opcional)
4. Representar os dados em mapas (heatmaps)

Resultados esperados:

* Identificação de regiões com alta incidência
* Visualização clara de padrões geográficos
* Apoio à vigilância epidemiológica

---

## Limitações dos Dados

* Possíveis erros de preenchimento nos registros
* Subnotificação de casos
* Atualizações tardias (dados retroativos)
* Diferenças entre bases de dados

---

## Possíveis Extensões

* Desenvolvimento de dashboard interativo (Streamlit ou Power BI)
* Aplicação de técnicas de Machine Learning para previsão de surtos
* Integração com dados socioeconômicos
* Comparação entre diferentes doenças

---

## Como Executar

```bash
# Clonar o repositório
git clone https://github.com/ODiogorocha/Projeto-de-software

# Entrar na pasta
cd Projeto-de-software

# Instalar dependências
pip install -r requirements.txt

#criar uma branch
git checkout -b feat/nome-da-branch

#mudar de branch 
git checkout nome-da-branch

#commit 
git add nome-dos-arquivos

git commit -m "o que foi mudado" #colocar feat para criacao e fix para correcao

git push 

```

---
