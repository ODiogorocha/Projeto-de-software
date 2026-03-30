from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


def preparar_dados_ml(df):
    df_ml = df.copy()

    # Seleciona apenas colunas necessárias
    df_ml = df_ml[["NU_IDADE_N", "SEXO", "OBITO"]]

    # Remove apenas o mínimo necessário
    df_ml = df_ml.dropna(subset=["NU_IDADE_N", "SEXO", "OBITO"])

    return df_ml


def treinar_modelo(df):
    print("Treinando modelo...")

    df_ml = preparar_dados_ml(df)

    if len(df_ml) < 10:
        print("Poucos dados para treino.")
        return None

    X = df_ml[["NU_IDADE_N", "SEXO"]]
    y = df_ml["OBITO"]

    if len(y.unique()) < 2:
        print("Apenas uma classe.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)

    print("\nRelatório:")
    print(classification_report(y_test, y_pred))

    return modelo