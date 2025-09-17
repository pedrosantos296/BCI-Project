import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Lê o CSV
df = pd.read_csv("data/onda_real.csv")

# Visualizar as primeiras linhas (opcional)
print(df.head())

# Mapeamento: nomes usados no gráfico → colunas reais no CSV
coluna_mapeamento = {
    "Meditação": "meditation",
    "Concentração": "attention",
}

# Define estilo do seaborn
sns.set(style="whitegrid")

# Criar gráficos para cada métrica
for nome_amigavel, nome_coluna in coluna_mapeamento.items():
    plt.figure(figsize=(12, 5))

    # Histograma
    plt.subplot(1, 2, 1)
    sns.histplot(df[nome_coluna], kde=True, bins=30, color="skyblue")
    plt.title(f"Histograma de {nome_amigavel}")
    plt.xlabel(nome_amigavel)
    plt.ylabel("Frequência")

    # Boxplot
    plt.subplot(1, 2, 2)
    sns.boxplot(x=df[nome_coluna], color="lightgreen")
    plt.title(f"Boxplot de {nome_amigavel}")
    plt.xlabel(nome_amigavel)

    plt.tight_layout()
    plt.show()
