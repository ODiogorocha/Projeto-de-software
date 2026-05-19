import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
PATH_INFLUD     = '/home/diogo/Documentos/codigos/Projeto-de-software/docs/database/INFLUD19-23-03-2026.csv'
PATH_MUNICIPIOS = '/home/diogo/Documentos/codigos/Projeto-de-software/docs/database/municipios.csv'
PATH_OUTPUT     = 'municipios_risco_doenca.csv'

MIN_CASOS_MUN = 5

# ─────────────────────────────────────────
# 1. CARREGAMENTO
# ─────────────────────────────────────────
print("\n[1/6] Carregando dados...")

use_cols = [
    'FEBRE','TOSSE','GARGANTA','DISPNEIA','DESC_RESP','SATURACAO','DIARREIA','VOMITO',
    'CARDIOPATI','DIABETES','OBESIDADE','ASMA','NEUROLOGIC','PNEUMOPATI','IMUNODEPRE','RENAL','HEPATICA',
    'CS_SEXO','TP_IDADE','COD_IDADE','CS_GESTANT','VACINA',
    'SG_UF_NOT','CO_MUN_RES','CLASSI_FIN'
]

df = pd.read_csv(PATH_INFLUD, sep=';', encoding='latin1', usecols=use_cols)
municipios = pd.read_csv(PATH_MUNICIPIOS)

# ─────────────────────────────────────────
# 2. PRÉ-PROCESSAMENTO
# ─────────────────────────────────────────
print("\n[2/6] Pré-processamento...")

symptom_cols = [
    'FEBRE','TOSSE','GARGANTA','DISPNEIA',
    'DESC_RESP','SATURACAO','DIARREIA','VOMITO'
]

comorbid_cols = [
    'CARDIOPATI','DIABETES','OBESIDADE','ASMA',
    'NEUROLOGIC','PNEUMOPATI','IMUNODEPRE','RENAL','HEPATICA'
]

df_clean = df.copy()

df_clean = df_clean.dropna(subset=['CLASSI_FIN', 'CO_MUN_RES'])
df_clean = df_clean[df_clean['CLASSI_FIN'].isin([1,2,3,4])]

# binário
for col in symptom_cols + comorbid_cols:
    df_clean[col] = (df_clean[col].fillna(2) == 1).astype(int)

df_clean['VACINA'] = (df_clean['VACINA'].fillna(2) == 1).astype(int)
df_clean['CS_SEXO'] = (df_clean['CS_SEXO'] == 'F').astype(int)
df_clean['CS_GESTANT'] = df_clean['CS_GESTANT'].fillna(0)

# ─────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────

def convert_age(tp, age):
    if tp == 1:
        return age / 365
    elif tp == 2:
        return age / 12
    return age

df_clean['idade_anos'] = df_clean.apply(
    lambda x: convert_age(x['TP_IDADE'], x['COD_IDADE']), axis=1
)

df_clean['num_sintomas'] = df_clean[symptom_cols].sum(axis=1)
df_clean['num_comorbidades'] = df_clean[comorbid_cols].sum(axis=1)

# novas features
df_clean['tem_comorbidade'] = (df_clean['num_comorbidades'] > 0).astype(int)

df_clean['caso_grave'] = (
    (df_clean['DISPNEIA'] == 1) |
    (df_clean['SATURACAO'] == 1)
).astype(int)

df_clean['sintomas_respiratorios'] = (
    df_clean['TOSSE'] +
    df_clean['DISPNEIA'] +
    df_clean['DESC_RESP']
)

# remover outliers
df_clean = df_clean[(df_clean['idade_anos'] >= 0) & (df_clean['idade_anos'] <= 110)]

df_clean['target'] = df_clean['CLASSI_FIN'].astype(int) - 1

# one-hot UF
df_clean['SG_UF_NOT'] = df_clean['SG_UF_NOT'].fillna('XX')
df_clean = pd.get_dummies(df_clean, columns=['SG_UF_NOT'], drop_first=True)

# ─────────────────────────────────────────
# FEATURES
# ─────────────────────────────────────────
feature_cols = (
    symptom_cols +
    comorbid_cols +
    ['CS_SEXO','CS_GESTANT','VACINA','idade_anos',
    'num_sintomas','num_comorbidades',
    'tem_comorbidade','caso_grave','sintomas_respiratorios'] +
    [c for c in df_clean.columns if c.startswith('SG_UF_NOT_')]
)

X = df_clean[feature_cols]
y = df_clean['target']

# ─────────────────────────────────────────
# 3. TREINAMENTO
# ─────────────────────────────────────────
print("\n[3/6] Treinando modelo...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# SMOTE
smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# modelo
model = XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ─────────────────────────────────────────
# 4. AVALIAÇÃO
# ─────────────────────────────────────────
print("\n[4/6] Avaliação...")

y_pred = model.predict(X_test)

print(f"\nAcurácia: {accuracy_score(y_test, y_pred):.4f}\n")

labels = ["Influenza","Outro Vírus","Outro Agente","COVID/SRAG"]
print(classification_report(y_test, y_pred, target_names=labels))

# matriz de confusão
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm, display_labels=labels).plot()
plt.title("Matriz de Confusão")
plt.show()

# ─────────────────────────────────────────
# 5. MUNICÍPIOS
# ─────────────────────────────────────────
print("\n[5/6] Risco por município...")

probas = model.predict_proba(X)

df_clean = df_clean.reset_index(drop=True)

for i, cls in enumerate(model.classes_):
    df_clean[f'p{cls}'] = probas[:, i]

mun_scores = df_clean.groupby('CO_MUN_RES').agg(
    total_casos=('target', 'count'),
    prob_influenza=('p0', 'mean'),
    prob_outro_virus=('p1', 'mean'),
    prob_outro_agente=('p2', 'mean'),
    prob_srag_covid=('p3', 'mean')
).reset_index()

municipios['cod_6d'] = (municipios['codigo_ibge'] // 10).astype(int)

mun_final = mun_scores.merge(
    municipios[['codigo_ibge','cod_6d','nome']],
    left_on='CO_MUN_RES',
    right_on='cod_6d',
    how='left'
)

export = mun_final.dropna(subset=['nome'])

for c in ['prob_influenza','prob_outro_virus','prob_outro_agente','prob_srag_covid']:
    export[c] = (export[c] * 100).round(2)

# ─────────────────────────────────────────
# 6. GRÁFICOS
# ─────────────────────────────────────────
def plot_top(df, col, titulo):
    top = df[df['total_casos'] >= MIN_CASOS_MUN].nlargest(10, col).sort_values(col)

    plt.figure()
    plt.barh(top['nome'], top[col])

    for i, v in enumerate(top[col]):
        plt.text(v, i, f" {v:.1f}%", va='center')

    plt.title(titulo)
    plt.xlabel('Probabilidade (%)')
    plt.tight_layout()
    plt.show()

print("\n[6/6] Gráficos...")

plot_top(export, 'prob_influenza', 'Top Municípios - Influenza')
plot_top(export, 'prob_outro_virus', 'Top Municípios - Outros Vírus')
plot_top(export, 'prob_outro_agente', 'Top Municípios - Outros Agentes')
plot_top(export, 'prob_srag_covid', 'Top Municípios - COVID/SRAG')

# salvar
export.to_csv(PATH_OUTPUT, index=False)

print("\nArquivo salvo:", PATH_OUTPUT)