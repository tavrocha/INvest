# ==============================
# Projeto DIO - Análise de Ativos Financeiros Brasileiros
# Vinícius Tavares Rocha
# ==============================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ------------------------------
# Função para ler e validar data
# ------------------------------
def ler_data(mensagem):
    while True:
        entrada = input(mensagem).strip()

        if len(entrada) != 8 or not entrada.isdigit():
            print("❌ Digite a data com 8 números no formato DDMMAAAA")
            continue

        dia = entrada[0:2]
        mes = entrada[2:4]
        ano = entrada[4:8]

        try:
            data_obj = datetime.strptime(f"{dia}-{mes}-{ano}", "%d-%m-%Y")

            if data_obj > datetime.now():
                print("❌ A data não pode estar no futuro.")
                continue

            return data_obj.strftime("%Y-%m-%d")

        except ValueError:
            print("❌ Data inválida no calendário.")

# ------------------------------
# Principais ativos do mercado brasileiro
# ------------------------------
ativos = [
    "PETR4.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "BBDC4.SA",
    "BBAS3.SA",
    "WEGE3.SA",
    "SUZB3.SA",
    "CPFE3.SA",
    "TAEE11.SA",
    "PRIO3.SA",
    "MGLU3.SA"
]

# ------------------------------
# Entrada de datas
# ------------------------------
start = ler_data("Digite a data de início (DDMMAAAA): ")
end = ler_data("Digite a data de término (DDMMAAAA): ")

# ------------------------------
# Download dos dados históricos
# ------------------------------
dados = yf.download(ativos, start=start, end=end)

if dados.empty:
    print("⚠ Nenhum dado retornado.")
    exit()

# ------------------------------
# Paleta de cores vibrantes e distintas
# ------------------------------
cores = [
    "#00E5FF",  # ciano neon
    "#FF6D00",  # laranja forte
    "#00C853",  # verde vibrante
    "#D500F9",  # roxo neon
    "#FFD600",  # amarelo ouro
    "#FF1744",  # vermelho vivo
    "#00B0FF",  # azul brilhante
    "#69F0AE",  # verde água
    "#FF9100",  # laranja quente
    "#7C4DFF",  # violeta
    "#F50057"   # pink forte
]

# ------------------------------
# Visualização gráfica dos ativos (TEMA ESCURO PRO)
# ------------------------------
plt.style.use("dark_background")

fig, ax = plt.subplots(figsize=(10, 5))

for i, ativo in enumerate(ativos):
    try:
        serie = dados["Close"][ativo].dropna()

        ax.plot(
            serie.index,
            serie.values,
            linewidth=3.2,
            color=cores[i % len(cores)],
            alpha=0.95,
            label=ativo.replace(".SA", "")
        )

    except:
        print(f"⚠ Não foi possível plotar {ativo}")

ax.set_title("Evolução do preço de fechamento", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Data")
ax.set_ylabel("Preço (R$)")

ax.yaxis.set_major_formatter(
    FuncFormatter(lambda x, _: f"R$ {x:,.0f}")
)

ax.grid(True, linestyle="--", alpha=0.2)
ax.legend(frameon=False, ncol=2, fontsize=9)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ------------------------------
# Gráfico comparativo normalizado
# ------------------------------
print("\n📊 Gerando gráfico comparativo de desempenho...")

fig, ax = plt.subplots(figsize=(10, 5))

for i, ativo in enumerate(ativos):
    try:
        serie = dados["Close"][ativo].dropna()
        normalizado = (serie / serie.iloc[0]) * 100

        ax.plot(
            normalizado.index,
            normalizado.values,
            linewidth=3.2,
            color=cores[i % len(cores)],
            alpha=0.95,
            label=ativo.replace(".SA", "")
        )
    except:
        pass

ax.set_title("Comparação de crescimento dos ativos (Base 100)", fontsize=15, fontweight="bold", pad=12)
ax.set_xlabel("Data")
ax.set_ylabel("Base 100")

ax.grid(True, linestyle="--", alpha=0.2)
ax.legend(frameon=False, ncol=2, fontsize=9)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()

# ------------------------------
# Função de análise por ativo
# ------------------------------
def analisar_ativo(df, ticker):
    fechamento = df["Close"][ticker].dropna()

    preco_medio = fechamento.mean()
    preco_inicial = fechamento.iloc[0]
    preco_final = fechamento.iloc[-1]
    retorno = ((preco_final - preco_inicial) / preco_inicial) * 100
    volatilidade = fechamento.pct_change().std() * 100
    maximo = fechamento.max()
    minimo = fechamento.min()

    return {
        "Ativo": ticker.replace(".SA", ""),
        "Preço Médio": preco_medio,
        "Retorno %": retorno,
        "Volatilidade %": volatilidade,
        "Máximo": maximo,
        "Mínimo": minimo
    }

# ------------------------------
# Construção da tabela comparativa
# ------------------------------
analises = []

for ativo in ativos:
    try:
        resultado = analisar_ativo(dados, ativo)
        analises.append(resultado)
    except:
        print(f"⚠ Falha ao analisar {ativo}")

tabela = pd.DataFrame(analises)

tabela = tabela.sort_values(by="Retorno %", ascending=False)

tabela["Preço Médio"] = tabela["Preço Médio"].round(2)
tabela["Retorno %"] = tabela["Retorno %"].round(2)
tabela["Volatilidade %"] = tabela["Volatilidade %"].round(2)
tabela["Máximo"] = tabela["Máximo"].round(2)
tabela["Mínimo"] = tabela["Mínimo"].round(2)

print("\n📊 Ranking de desempenho no período:\n")
print(tabela.to_string(index=False))

# ------------------------------
# Simulação de investimento em CDB
# ------------------------------
print("\n💰 Simulador de CDB")

try:
    valor_cdb = float(input("Digite o valor investido (R$): "))
    percentual_cdi = float(input("Percentual do CDI (ex: 110 para 110%): "))
    dias = int(input("Período do investimento em dias: "))

    # CDI anual base (100% do CDI) — manter sincronizado com CDI_ANUAL em app_investimentos.py
    taxa_cdi_anual = 0.1065
    taxa_anual_cdb = taxa_cdi_anual * (percentual_cdi / 100)

    valor_final = valor_cdb * (1 + taxa_anual_cdb) ** (dias / 365)
    rendimento = valor_final - valor_cdb

    print("\n📈 Resultado da simulação:")
    print(f"Valor inicial: R$ {valor_cdb:.2f}")
    print(f"Valor final estimado: R$ {valor_final:.2f}")
    print(f"Rendimento bruto: R$ {rendimento:.2f}")

except:
    print("⚠ Entrada inválida na simulação do CDB.")