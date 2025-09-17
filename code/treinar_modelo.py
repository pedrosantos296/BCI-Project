import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# === 1. Carregar dados ===
df = pd.read_csv("data/onda_real.csv")
print("Dados carregados. Total linhas:", len(df))

# === 2. Preparar dados ===
X = df.drop(columns=["timestamp", "label"])
le = LabelEncoder()
y = le.fit_transform(df["label"])

# === 3. Dividir treino/teste ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# === 4. Tuning com GridSearchCV ===
param_grid = {
    'n_estimators': [50, 100, 200], #nº de modelos
    'max_depth': [None, 10, 20], #profundidade
    'min_samples_split': [2, 5], #nº de decisoes
}

clf = RandomForestClassifier(random_state=42)
grid_search = GridSearchCV(clf, param_grid, cv=5, scoring='accuracy', n_jobs=-1) #Cross-Validation = 5 blocos -> treina e depois testa (5 vezes cada bloco)
grid_search.fit(X_train, y_train)

print("Melhores hiperparâmetros:", grid_search.best_params_)

best_clf = grid_search.best_estimator_

# === 5. Avaliar modelo ===
y_pred = best_clf.predict(X_test)
print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

conf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues",
            xticklabels=le.classes_,
            yticklabels=le.classes_)
plt.title("Matriz de Confusão")
plt.xlabel("Previsto")
plt.ylabel("Real")
plt.show()

# === 6. Salvar modelo e encoder ===
joblib.dump(best_clf, "modelo_treinado.joblib")
joblib.dump(le, "label_encoder.joblib")
print("Modelo e LabelEncoder salvos.")
