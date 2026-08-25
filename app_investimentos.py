# =============================================================================
# INvest — v3.0
# Autor: Vinícius Tavares Rocha
# Descrição: Dashboard de análise de ações da B3, com carteira pessoal, CDBs,
#            histórico de patrimônio e Assistente da Carteira local (sem custo).
# Tecnologias: Python 3.10+, Tkinter, yFinance, Matplotlib, SQLite3
# GitHub: github.com/tavrocha/INvest
# =============================================================================

import tkinter as tk
from tkinter import ttk
import yfinance as yf
from datetime import datetime
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import os
import json
import sqlite3
import unicodedata
import sys

# ==============================
# CONFIGURAÇÃO DE CORES
# ==============================
BG      = "#111111"
CARD    = "#1c1c1c"
TXT     = "#e0e0e0"
BTN     = "#2e2e2e"
ACCENT  = "#cc0000"
CDB_BG  = "#1c1c1c"

CORES_ATIVOS = [
    "#00E5FF", "#FF9100", "#FF1744", "#76FF03", "#D500F9",
    "#FFD600", "#00BFA5", "#FF6D00", "#64DD17", "#2979FF",
    "#FF4081", "#F50057", "#69F0AE", "#EEFF41", "#FF6E40",
    "#40C4FF", "#B2FF59", "#EA80FC", "#FF80AB", "#CCFF90",
]

# ==============================
# CATÁLOGO DE ATIVOS — base curada para a busca com autocomplete
# ==============================
# Lista fixa/curada (não é dado de mercado — preço, variação e histórico de
# QUALQUER ativo aqui, ou digitado manualmente, sempre vêm ao vivo do yfinance).
# "popular": True marca os que aparecem pré-marcados ao abrir o app e em
# destaque quando a busca está vazia.
CATALOGO_ATIVOS = [
    # ── Ações — popular ──
    {"ticker": "PETR4", "nome": "Petrobras PN",              "tipo": "Ação", "popular": True},
    {"ticker": "VALE3", "nome": "Vale ON",                    "tipo": "Ação", "popular": True},
    {"ticker": "ITUB4", "nome": "Itaú Unibanco PN",           "tipo": "Ação", "popular": True},
    {"ticker": "BBDC4", "nome": "Bradesco PN",                "tipo": "Ação", "popular": True},
    {"ticker": "BBAS3", "nome": "Banco do Brasil ON",         "tipo": "Ação", "popular": True},
    {"ticker": "WEGE3", "nome": "WEG ON",                     "tipo": "Ação", "popular": True},
    {"ticker": "SUZB3", "nome": "Suzano ON",                  "tipo": "Ação", "popular": True},
    {"ticker": "CPFE3", "nome": "CPFL Energia ON",            "tipo": "Ação", "popular": True},
    {"ticker": "TAEE11","nome": "Taesa Unit",                 "tipo": "Ação", "popular": True},
    {"ticker": "PRIO3", "nome": "PRIO ON",                    "tipo": "Ação", "popular": True},
    {"ticker": "MGLU3", "nome": "Magazine Luiza ON",          "tipo": "Ação", "popular": True},
    # ── Ações — catálogo geral ──
    {"ticker": "PETR3", "nome": "Petrobras ON",               "tipo": "Ação", "popular": False},
    {"ticker": "ITSA4", "nome": "Itaúsa PN",                  "tipo": "Ação", "popular": False},
    {"ticker": "BBDC3", "nome": "Bradesco ON",                "tipo": "Ação", "popular": False},
    {"ticker": "ABEV3", "nome": "Ambev ON",                   "tipo": "Ação", "popular": False},
    {"ticker": "B3SA3", "nome": "B3 ON",                      "tipo": "Ação", "popular": False},
    {"ticker": "RENT3", "nome": "Localiza ON",                "tipo": "Ação", "popular": False},
    {"ticker": "LREN3", "nome": "Lojas Renner ON",            "tipo": "Ação", "popular": False},
    {"ticker": "RADL3", "nome": "Raia Drogasil ON",           "tipo": "Ação", "popular": False},
    {"ticker": "RDOR3", "nome": "Rede D'Or ON",               "tipo": "Ação", "popular": False},
    {"ticker": "HAPV3", "nome": "Hapvida ON",                 "tipo": "Ação", "popular": False},
    {"ticker": "GGBR4", "nome": "Gerdau PN",                  "tipo": "Ação", "popular": False},
    {"ticker": "CSNA3", "nome": "CSN ON",                     "tipo": "Ação", "popular": False},
    {"ticker": "USIM5", "nome": "Usiminas PNA",               "tipo": "Ação", "popular": False},
    {"ticker": "CSAN3", "nome": "Cosan ON",                   "tipo": "Ação", "popular": False},
    {"ticker": "ELET3", "nome": "Eletrobras ON",              "tipo": "Ação", "popular": False},
    {"ticker": "ELET6", "nome": "Eletrobras PNB",             "tipo": "Ação", "popular": False},
    {"ticker": "SBSP3", "nome": "Sabesp ON",                  "tipo": "Ação", "popular": False},
    {"ticker": "CMIG4", "nome": "Cemig PN",                   "tipo": "Ação", "popular": False},
    {"ticker": "BBSE3", "nome": "BB Seguridade ON",           "tipo": "Ação", "popular": False},
    {"ticker": "SANB11","nome": "Santander Unit",             "tipo": "Ação", "popular": False},
    {"ticker": "KLBN11","nome": "Klabin Unit",                "tipo": "Ação", "popular": False},
    {"ticker": "EMBR3", "nome": "Embraer ON",                 "tipo": "Ação", "popular": False},
    {"ticker": "JBSS3", "nome": "JBS ON",                     "tipo": "Ação", "popular": False},
    {"ticker": "MRFG3", "nome": "Marfrig ON",                 "tipo": "Ação", "popular": False},
    {"ticker": "BEEF3", "nome": "Minerva ON",                 "tipo": "Ação", "popular": False},
    {"ticker": "CYRE3", "nome": "Cyrela ON",                  "tipo": "Ação", "popular": False},
    {"ticker": "MRVE3", "nome": "MRV ON",                     "tipo": "Ação", "popular": False},
    {"ticker": "EZTC3", "nome": "Eztec ON",                   "tipo": "Ação", "popular": False},
    {"ticker": "ARZZ3", "nome": "Arezzo ON",                  "tipo": "Ação", "popular": False},
    {"ticker": "NTCO3", "nome": "Natura ON",                  "tipo": "Ação", "popular": False},
    {"ticker": "PCAR3", "nome": "Pão de Açúcar ON",           "tipo": "Ação", "popular": False},
    {"ticker": "CRFB3", "nome": "Carrefour Brasil ON",        "tipo": "Ação", "popular": False},
    {"ticker": "RAIL3", "nome": "Rumo ON",                    "tipo": "Ação", "popular": False},
    {"ticker": "CCRO3", "nome": "CCR ON",                     "tipo": "Ação", "popular": False},
    {"ticker": "AZUL4", "nome": "Azul PN",                    "tipo": "Ação", "popular": False},
    {"ticker": "GOLL4", "nome": "Gol PN",                     "tipo": "Ação", "popular": False},
    {"ticker": "TOTS3", "nome": "Totvs ON",                   "tipo": "Ação", "popular": False},
    {"ticker": "VIVT3", "nome": "Telefônica Brasil ON",       "tipo": "Ação", "popular": False},
    {"ticker": "TIMS3", "nome": "TIM ON",                     "tipo": "Ação", "popular": False},
    {"ticker": "IRBR3", "nome": "IRB Brasil ON",              "tipo": "Ação", "popular": False},
    {"ticker": "BPAC11","nome": "BTG Pactual Unit",           "tipo": "Ação", "popular": False},
    {"ticker": "YDUQ3", "nome": "Yduqs ON",                   "tipo": "Ação", "popular": False},
    {"ticker": "COGN3", "nome": "Cogna ON",                   "tipo": "Ação", "popular": False},
    {"ticker": "CVCB3", "nome": "CVC ON",                     "tipo": "Ação", "popular": False},
    {"ticker": "ALPA4", "nome": "Alpargatas PN",              "tipo": "Ação", "popular": False},
    {"ticker": "SLCE3", "nome": "SLC Agrícola ON",            "tipo": "Ação", "popular": False},
    {"ticker": "SMTO3", "nome": "São Martinho ON",            "tipo": "Ação", "popular": False},
    {"ticker": "AGRO3", "nome": "BrasilAgro ON",              "tipo": "Ação", "popular": False},
    {"ticker": "CASH3", "nome": "Méliuz ON",                  "tipo": "Ação", "popular": False},
    {"ticker": "ENGI11","nome": "Energisa Unit",              "tipo": "Ação", "popular": False},
    # ── FIIs — popular ──
    {"ticker": "MXRF11","nome": "Maxi Renda FII",             "tipo": "FII", "popular": True},
    # ── FIIs — catálogo geral ──
    {"ticker": "HGLG11","nome": "CSHG Logística FII",         "tipo": "FII", "popular": False},
    {"ticker": "KNRI11","nome": "Kinea Renda Imobiliária FII","tipo": "FII", "popular": False},
    {"ticker": "XPLG11","nome": "XP Log FII",                 "tipo": "FII", "popular": False},
    {"ticker": "VISC11","nome": "Vinci Shopping Centers FII", "tipo": "FII", "popular": False},
    {"ticker": "KNCR11","nome": "Kinea Rendimentos FII",      "tipo": "FII", "popular": False},
    {"ticker": "BCFF11","nome": "FoF Brasil Plural FII",      "tipo": "FII", "popular": False},
    {"ticker": "HGRU11","nome": "CSHG Renda Urbana FII",      "tipo": "FII", "popular": False},
    {"ticker": "XPML11","nome": "XP Malls FII",               "tipo": "FII", "popular": False},
    {"ticker": "VILG11","nome": "Vinci Logística FII",        "tipo": "FII", "popular": False},
    {"ticker": "IRDM11","nome": "Iridium Recebíveis FII",     "tipo": "FII", "popular": False},
    {"ticker": "RECT11","nome": "REC Recebíveis FII",         "tipo": "FII", "popular": False},
    {"ticker": "BTLG11","nome": "BTG Pactual Logística FII",  "tipo": "FII", "popular": False},
    {"ticker": "KNIP11","nome": "Kinea Índices de Preços FII","tipo": "FII", "popular": False},
    {"ticker": "HFOF11","nome": "Hedge Top FOFII 3 FII",      "tipo": "FII", "popular": False},
    {"ticker": "ALZR11","nome": "Alianza Trust Renda FII",    "tipo": "FII", "popular": False},
    {"ticker": "VRTA11","nome": "Fator Verita FII",           "tipo": "FII", "popular": False},
    {"ticker": "HGBS11","nome": "CSHG Brasil Shopping FII",   "tipo": "FII", "popular": False},
    {"ticker": "MALL11","nome": "Malls Brasil Plural FII",    "tipo": "FII", "popular": False},
    # ── ETFs — popular ──
    {"ticker": "BOVA11","nome": "iShares Ibovespa ETF",       "tipo": "ETF", "popular": True},
    # ── ETFs — catálogo geral ──
    {"ticker": "IVVB11","nome": "iShares S&P 500 ETF",        "tipo": "ETF", "popular": False},
    {"ticker": "SMAL11","nome": "iShares Small Cap ETF",      "tipo": "ETF", "popular": False},
    {"ticker": "DIVO11","nome": "iShares Dividendos ETF",     "tipo": "ETF", "popular": False},
    {"ticker": "GOLD11","nome": "Trend Ouro ETF",             "tipo": "ETF", "popular": False},
    {"ticker": "FIND11","nome": "iShares Financials ETF",     "tipo": "ETF", "popular": False},
    {"ticker": "BRAX11","nome": "iShares Brasil Amplo ETF",   "tipo": "ETF", "popular": False},
]

_TIPO_ICONE = {"Ação": "📈", "FII": "🏢", "ETF": "📊"}

# ==============================
# ESTADO
# ==============================
ativos_vars  = {}
ativos_ordem = []

# ==============================
# MÁSCARA DE DATA — lógica corrigida
# ==============================
class MascaraData:
    """
    Aplica máscara DD/MM/AAAA num Entry do tkinter.
    Funciona extraindo só os dígitos digitados, limitando a 8,
    e remontando a string com as barras nas posições certas.
    Usa um flag para evitar recursão ao setar o valor.
    """
    def __init__(self, entry):
        self.entry    = entry
        self._editing = False
        self.entry.bind("<KeyRelease>", self._aplicar)
        self.entry.bind("<BackSpace>",  self._aplicar)

    def _aplicar(self, event=None):
        if self._editing:
            return
        self._editing = True

        # 1. Pega o conteúdo atual e extrai só dígitos
        texto = self.entry.get()
        digitos = "".join(ch for ch in texto if ch.isdigit())

        # 2. Limita a 8 dígitos
        digitos = digitos[:8]

        # 3. Remonta com barras: DD/MM/AAAA
        resultado = ""
        for i, ch in enumerate(digitos):
            if i == 2 or i == 4:
                resultado += "/"
            resultado += ch

        # 4. Substitui o conteúdo do entry
        self.entry.delete(0, tk.END)
        self.entry.insert(0, resultado)
        self.entry.icursor(tk.END)

        self._editing = False

    def get_data_yf(self):
        """Retorna a data no formato YYYY-MM-DD para o yfinance, ou None se inválida."""
        digitos = "".join(ch for ch in self.entry.get() if ch.isdigit())
        if len(digitos) != 8:
            return None
        try:
            data = datetime.strptime(digitos, "%d%m%Y")
            if data > datetime.now():
                return None
            return data.strftime("%Y-%m-%d")
        except ValueError:
            return None


# ==============================
# HELPERS
# ==============================
def nome_exibicao(ticker):
    return ticker.replace(".SA", "").upper()

def _fmt_num_br(valor, casas=2, forcar_sinal=False):
    """
    Formata número no padrão BR: 1.234,56 (vírgula decimal, ponto de milhar —
    inverso do :,.2f nativo do Python). Sem prefixo de moeda — usar em colunas
    de tabela onde o cabeçalho já indica "(R$)". Com forcar_sinal=True, sempre
    mostra + ou - na frente (útil para lucro/prejuízo).
    """
    sinal = "-" if valor < 0 else ("+" if forcar_sinal else "")
    texto = f"{abs(valor):,.{casas}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}{texto}"

def _fmt_brl(valor, casas=2, forcar_sinal=False):
    """Formata valor em Real brasileiro com o prefixo, sinal antes do R$: -R$ 500,50 / +R$ 850,33."""
    sinal = "-" if valor < 0 else ("+" if forcar_sinal else "")
    return f"{sinal}R$ {_fmt_num_br(abs(valor), casas=casas)}"

def limpar_entry_placeholder(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg=TXT)

def restaurar_placeholder(entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)
        entry.config(fg="#aaaaaa")

def _normalizar_texto(txt):
    """Minúsculas, sem acentos, sem pontuação — facilita busca e casamento por palavras-chave."""
    txt = txt.lower().strip()
    txt = "".join(
        c for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    )
    return txt

# ==============================
# BUSCA DE ATIVOS (catálogo curado + fallback manual)
# ==============================
def _buscar_no_catalogo(query_normalizada, limite=8, apenas_disponiveis=True):
    """
    Busca no CATALOGO_ATIVOS por ticker ou nome.
    Prioridade: ticker idêntico > ticker começa com > ticker contém > nome contém
    > todas as palavras da busca aparecem em qualquer ordem (ex: "etf ouro" bate
    com "Trend Ouro ETF"). Com busca vazia, retorna os marcados como populares.
    Se apenas_disponiveis=False, inclui também ativos já adicionados (usado só
    para diferenciar "não existe no catálogo" de "já está na sua lista").
    """
    base = CATALOGO_ATIVOS
    if apenas_disponiveis:
        base = [a for a in base if (a["ticker"] + ".SA") not in ativos_vars]

    if not query_normalizada:
        return [a for a in base if a["popular"]][:limite]

    palavras_busca = query_normalizada.split()
    exatos, prefixo, contem_ticker, contem_nome, todas_palavras = [], [], [], [], []
    for ativo in base:
        ticker_norm = _normalizar_texto(ativo["ticker"])
        nome_norm   = _normalizar_texto(ativo["nome"])
        combinado   = f"{ticker_norm} {nome_norm}"
        if ticker_norm == query_normalizada:
            exatos.append(ativo)
        elif ticker_norm.startswith(query_normalizada):
            prefixo.append(ativo)
        elif query_normalizada in ticker_norm:
            contem_ticker.append(ativo)
        elif query_normalizada in nome_norm:
            contem_nome.append(ativo)
        elif len(palavras_busca) > 1 and all(p in combinado for p in palavras_busca):
            todas_palavras.append(ativo)

    return (exatos + prefixo + contem_ticker + contem_nome + todas_palavras)[:limite]

def _renderizar_resultados_busca(texto_busca=""):
    """Redesenha a lista de resultados abaixo do campo de busca."""
    for w in frame_resultados_busca.winfo_children():
        w.destroy()

    query_norm  = _normalizar_texto(texto_busca)
    resultados  = _buscar_no_catalogo(query_norm)

    if query_norm and not resultados:
        # Existe no catálogo mas já foi adicionado? Mensagem diferente de "não encontrado".
        ja_adicionado = _buscar_no_catalogo(query_norm, apenas_disponiveis=False)
        if ja_adicionado:
            nomes = ", ".join(a["ticker"] for a in ja_adicionado[:3])
            tk.Label(frame_resultados_busca, text=f"✔ {nomes} já está na sua lista.",
                     bg=CARD, fg="#aaaaaa", font=("Arial", 8, "italic"), wraplength=190, justify="left"
                     ).pack(anchor="w", padx=4, pady=(2, 4))
            return

        tk.Label(frame_resultados_busca, text="Nenhum resultado no catálogo.",
                 bg=CARD, fg="#aaaaaa", font=("Arial", 8, "italic")
                 ).pack(anchor="w", padx=4, pady=(2, 0))
        texto_original = texto_busca.strip().upper()
        tk.Button(frame_resultados_busca, text=f"➕ Adicionar \"{texto_original}\" mesmo assim",
                  bg=BTN, fg=TXT, font=("Arial", 8), relief="flat", cursor="hand2",
                  anchor="w", command=lambda: _adicionar_ativo_manual(texto_original)
                  ).pack(fill="x", padx=4, pady=2)
        return

    if not query_norm:
        if not resultados:
            tk.Label(frame_resultados_busca,
                     text="✔ Todos os populares já estão na sua lista.\nBusque outro ativo acima.",
                     bg=CARD, fg="#aaaaaa", font=("Arial", 7, "italic"), justify="left"
                     ).pack(anchor="w", padx=4, pady=(2, 4))
            return
        tk.Label(frame_resultados_busca, text="⭐ Populares", bg=CARD, fg="#aaaaaa",
                 font=("Arial", 7, "bold")).pack(anchor="w", padx=4, pady=(2, 0))

    for ativo in resultados:
        icone = _TIPO_ICONE.get(ativo["tipo"], "")
        texto = f"{icone} {ativo['ticker']} — {ativo['nome']}"
        tk.Button(frame_resultados_busca, text=texto, bg=BTN, fg=TXT,
                  font=("Arial", 8), relief="flat", cursor="hand2", anchor="w",
                  command=lambda a=ativo: _adicionar_do_catalogo(a)
                  ).pack(fill="x", padx=4, pady=1)

def _on_busca_ativo_change(event=None):
    texto = entry_busca_ativo.get()
    if texto == PLACEHOLDER_BUSCA:
        texto = ""
    _renderizar_resultados_busca(texto)

def _adicionar_do_catalogo(ativo):
    """Adiciona um ativo do catálogo curado — sem checagem de rede (já é conhecido/válido)."""
    ticker = ativo["ticker"] + ".SA"
    if ticker in ativos_vars:
        return
    var = tk.BooleanVar(value=True)
    ativos_vars[ticker] = var
    ativos_ordem.append(ticker)
    _criar_checkbox(ticker, var)
    entry_busca_ativo.delete(0, tk.END)
    label_status.config(text=f"✔ {ativo['ticker']} adicionado!", fg=ACCENT)
    _renderizar_resultados_busca("")

def _adicionar_ativo_manual(raw_text):
    """Fallback: ticker fora do catálogo — valida no yfinance antes de adicionar (como antes)."""
    raw = raw_text.strip().upper()
    if not raw:
        return
    ticker = raw if raw.endswith(".SA") else raw + ".SA"
    if ticker in ativos_vars:
        label_status.config(text=f"{nome_exibicao(ticker)} já está na lista.", fg=ACCENT)
        return

    label_status.config(text=f"Verificando {nome_exibicao(ticker)}...", fg="#aaaaaa")

    def verificar():
        valido = False
        try:
            hist = yf.download(ticker, period="5d", auto_adjust=True, progress=False)
            valido = not hist.empty
        except Exception:
            valido = False
        root.after(0, lambda: _pos_verificacao_manual(ticker, valido))

    threading.Thread(target=verificar, daemon=True).start()

def _pos_verificacao_manual(ticker, valido):
    if not valido:
        label_status.config(text=f"❌ {nome_exibicao(ticker)} não encontrado.", fg="#FF5252")
        return
    var = tk.BooleanVar(value=True)
    ativos_vars[ticker] = var
    ativos_ordem.append(ticker)
    _criar_checkbox(ticker, var)
    entry_busca_ativo.delete(0, tk.END)
    label_status.config(text=f"✔ {nome_exibicao(ticker)} adicionado!", fg=ACCENT)
    _renderizar_resultados_busca("")

def _criar_checkbox(ticker, var):
    idx = ativos_ordem.index(ticker)
    cor = CORES_ATIVOS[idx % len(CORES_ATIVOS)]

    row_frame = tk.Frame(frame_lista_ativos, bg=CARD)
    row_frame.pack(anchor="w", padx=6, pady=1)

    c = tk.Canvas(row_frame, width=12, height=12, bg=CARD, highlightthickness=0)
    c.create_rectangle(0, 0, 12, 12, fill=cor, outline="")
    c.pack(side="left", padx=(0, 4))

    tk.Checkbutton(
        row_frame, text=nome_exibicao(ticker), variable=var,
        bg=CARD, fg=TXT, selectcolor=BTN,
        activebackground=CARD, activeforeground=TXT,
        font=("Arial", 9), cursor="hand2"
    ).pack(side="left")

def selecionar_todos():
    for v in ativos_vars.values(): v.set(True)

def desmarcar_todos():
    for v in ativos_vars.values(): v.set(False)

# ==============================
# GERAR GRÁFICO
# ==============================
import matplotlib.dates as mdates
import numpy as np

# estado global do gráfico para tooltip
_estado_grafico = {
    "ax": None, "canvas": None,
    "series": {},   # ticker -> (xs_num, ys, cor)
    "modo": "preco" # "preco" ou "base100"
}

def _montar_grafico(dados, selecionados, modo):
    """Monta a figura matplotlib e retorna (fig, series_dict)."""
    fig = plt.figure(figsize=(11, 4.2))
    fig.patch.set_facecolor(BG)

    ax = fig.add_axes([0.07, 0.16, 0.68, 0.74])
    ax.set_facecolor(BG)

    ax_leg = fig.add_axes([0.77, 0.05, 0.22, 0.90])
    ax_leg.set_facecolor(CARD)
    ax_leg.set_xticks([]); ax_leg.set_yticks([])
    for spine in ax_leg.spines.values():
        spine.set_edgecolor(ACCENT); spine.set_linewidth(1.2)

    linhas, nomes, series = [], [], {}

    for ativo in selecionados:
        cor = CORES_ATIVOS[ativos_ordem.index(ativo) % len(CORES_ATIVOS)]
        try:
            raw = (dados["Close"] if len(selecionados) == 1
                   else dados["Close"][ativo]).dropna()

            if modo == "base100":
                serie = (raw / raw.iloc[0]) * 100
            else:
                serie = raw

            xs_num = mdates.date2num(serie.index.to_pydatetime())
            ys     = serie.values.astype(float)

            linha, = ax.plot(serie.index, ys, linewidth=2.5,
                             color=cor, label=nome_exibicao(ativo))
            linhas.append(linha)
            nomes.append(nome_exibicao(ativo))
            series[ativo] = (xs_num, ys, cor)

            # Média móvel (se ativada)
            mm = _mm_estado.get("periodo", 0)
            if mm > 0 and len(serie) >= mm:
                mm_serie = serie.rolling(window=mm).mean().dropna()
                ax.plot(mm_serie.index, mm_serie.values,
                        linewidth=1.2, color=cor, linestyle="--", alpha=0.5)
        except Exception:
            pass

    titulo = "Desempenho Relativo (Base 100)" if modo == "base100" else "Evolução dos Ativos"
    ylabel = "Retorno (Base 100)" if modo == "base100" else "Preço (R$)"

    ax.set_title(titulo, color=TXT, fontsize=13, fontweight="bold")
    ax.set_ylabel(ylabel, color=TXT)

    if modo == "preco":
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: _fmt_brl(x)))
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.1f}"))
        ax.axhline(100, color="#444", linewidth=0.8, linestyle="--")

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%Y"))
    ax.tick_params(axis="x", colors="#FFF", rotation=35, labelsize=8)
    ax.tick_params(axis="y", colors="#FFF")
    for spine in ax.spines.values(): spine.set_color("#444")

    ax_leg.text(0.5, 0.97, "Ativos", transform=ax_leg.transAxes,
                color=ACCENT, fontsize=10, fontweight="bold", ha="center", va="top")
    leg = ax_leg.legend(handles=linhas, labels=nomes, loc="upper center",
                        bbox_to_anchor=(0.5, 0.90), frameon=False, ncol=1,
                        fontsize=9, handlelength=1.5, labelspacing=0.5)
    for t in leg.get_texts(): t.set_color("#FFF")

    return fig, ax, series


def _conectar_tooltip(fig, ax, canvas, series, modo):
    """
    Tooltip robusto — mede distância em PIXELS para cada série,
    só ativa se o cursor estiver a menos de 25px de alguma linha.
    """
    annot = ax.annotate(
        "", xy=(0, 0), xytext=(15, 15),
        xycoords="data", textcoords="offset points",
        fontsize=9, color="#000000", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.45", facecolor=ACCENT,
                  alpha=0.92, edgecolor="none"),
        zorder=10, visible=False
    )
    dot, = ax.plot([], [], "o", markersize=8, zorder=11, visible=False,
                   markeredgecolor="#000000", markeredgewidth=0.5)

    LIMIAR_PX = 25

    def on_move(event):
        if event.inaxes != ax or not series or event.xdata is None:
            annot.set_visible(False)
            dot.set_visible(False)
            canvas.draw_idle()
            return

        cx, cy = event.x, event.y

        melhor_ticker = None
        melhor_dist   = float("inf")
        melhor_xd = melhor_yd = 0.0
        melhor_cor = ACCENT

        for ticker, (xs_num, ys, cor) in series.items():
            pts_px = ax.transData.transform(np.column_stack([xs_num, ys]))
            dists  = np.sqrt((pts_px[:, 0] - cx)**2 + (pts_px[:, 1] - cy)**2)
            idx    = int(np.argmin(dists))
            d      = dists[idx]
            if d < melhor_dist:
                melhor_dist   = d
                melhor_ticker = ticker
                melhor_xd     = xs_num[idx]
                melhor_yd     = ys[idx]
                melhor_cor    = cor

        if melhor_ticker is None or melhor_dist > LIMIAR_PX:
            annot.set_visible(False)
            dot.set_visible(False)
            canvas.draw_idle()
            return

        data_str = mdates.num2date(melhor_xd).strftime("%d/%m/%Y")
        val_str  = (f"{melhor_yd:.2f}" if modo == "base100"
                    else _fmt_brl(melhor_yd))

        annot.set_text(
            f"  {nome_exibicao(melhor_ticker)}\n"
            f"  Data: {data_str}\n"
            f"  Valor: {val_str}  "
        )
        annot.get_bbox_patch().set_facecolor(melhor_cor)
        annot.xy = (melhor_xd, melhor_yd)

        xlim  = ax.get_xlim()
        off_x = -120 if melhor_xd > xlim[0] + (xlim[1] - xlim[0]) * 0.72 else 15
        annot.set_position((off_x, 15))
        annot.set_visible(True)

        dot.set_data([melhor_xd], [melhor_yd])
        dot.set_color(melhor_cor)
        dot.set_visible(True)
        canvas.draw_idle()

    canvas.mpl_connect("motion_notify_event", on_move)


def _montar_tabela(dados, selecionados, frame_pai):
    """Cria tabela de análise dentro de frame_pai — usa grid no frame mestre."""
    for w in frame_pai.winfo_children(): w.destroy()

    colunas  = ["Ativo", "Início", "Fim", "Retorno %", "Var. Dia", "Volatil. %", "Risco", "Máximo", "Mínimo"]
    larguras = [80, 85, 85, 85, 75, 85, 70, 85, 85]

    # Frame mestre com grid
    tbl = tk.Frame(frame_pai, bg=CARD)
    tbl.pack(fill="x", padx=8)

    # Cabeçalho
    for c, (col, w) in enumerate(zip(colunas, larguras)):
        tk.Label(tbl, text=col, bg=CARD, fg=ACCENT,
                 font=("Arial", 8, "bold"), width=w//8,
                 anchor="center").grid(row=0, column=c, padx=1, pady=3, sticky="ew")

    # Separador
    sep = tk.Frame(tbl, bg=BTN, height=1)
    sep.grid(row=1, column=0, columnspan=len(colunas), sticky="ew", pady=0)

    # Linhas de dados
    for idx_a, ativo in enumerate(selecionados):
        try:
            serie = (dados["Close"] if len(selecionados) == 1
                     else dados["Close"][ativo]).dropna()

            inicio    = float(serie.iloc[0])
            fim       = float(serie.iloc[-1])
            retorno   = ((fim - inicio) / inicio) * 100
            vol       = serie.pct_change().std() * 100
            maximo    = float(serie.max())
            minimo    = float(serie.min())
            cor_ativo = CORES_ATIVOS[ativos_ordem.index(ativo) % len(CORES_ATIVOS)]
            cor_ret   = "#00C896" if retorno >= 0 else "#FF5252"
            row_bg    = "#161616" if idx_a % 2 == 0 else "#202020"

            risco_txt, cor_risco = _classificar_risco(vol)
            # Variação do último dia disponível
            if len(serie) >= 2:
                var_dia     = (serie.iloc[-1] / serie.iloc[-2] - 1) * 100
                var_dia_txt = f"{var_dia:+.2f}%"
                cor_var_dia = "#00C896" if var_dia >= 0 else "#FF5252"
            else:
                var_dia_txt = "—"; cor_var_dia = "#aaaaaa"
            valores = [
                (nome_exibicao(ativo), cor_ativo),
                (_fmt_brl(inicio),     TXT),
                (_fmt_brl(fim),        TXT),
                (f"{retorno:+.2f}%",   cor_ret),
                (var_dia_txt,          cor_var_dia),
                (f"{vol:.2f}%",        TXT),
                (risco_txt,            cor_risco),
                (_fmt_brl(maximo),     TXT),
                (_fmt_brl(minimo),     TXT),
            ]
            r = idx_a + 2   # +2 por causa do header e separador
            for c, (val, fg) in enumerate(valores):
                tk.Label(tbl, text=val, bg=row_bg, fg=fg,
                         font=("Arial", 8), width=larguras[c]//8,
                         anchor="center").grid(row=r, column=c, padx=1, pady=2, sticky="ew")
        except Exception:
            pass


# Estado da média móvel
_mm_estado = {"periodo": 0}   # 0 = desligada

def _toggle_mm(periodo):
    """Liga/desliga média móvel e re-renderiza."""
    if _mm_estado["periodo"] == periodo:
        _mm_estado["periodo"] = 0
    else:
        _mm_estado["periodo"] = periodo
    _atualizar_btn_mm()
    if _cache["dados"] is not None:
        _renderizar(_estado_grafico["modo"])

def _atualizar_btn_mm():
    p = _mm_estado["periodo"]
    btn_mm20.config(bg=ACCENT if p == 20 else BTN,
                    fg="#000000" if p == 20 else TXT)
    btn_mm50.config(bg=ACCENT if p == 50 else BTN,
                    fg="#000000" if p == 50 else TXT)

# ── Análise inteligente ──
def _calcular_analise(dados, selecionados):
    """Calcula métricas de todos os ativos e retorna lista de dicts."""
    analises = []
    for ativo in selecionados:
        try:
            serie = (dados["Close"] if len(selecionados) == 1
                     else dados["Close"][ativo]).dropna()
            inicio  = float(serie.iloc[0])
            fim     = float(serie.iloc[-1])
            retorno = ((fim - inicio) / inicio) * 100
            vol     = serie.pct_change().std() * 100
            analises.append({
                "ticker":  ativo,
                "nome":    nome_exibicao(ativo),
                "retorno": retorno,
                "vol":     vol,
                "cor":     CORES_ATIVOS[ativos_ordem.index(ativo) % len(CORES_ATIVOS)]
            })
        except Exception:
            pass
    return analises

def _classificar_risco(vol):
    if vol < 1.5:
        return ("Baixo",  "#00C896")   # verde
    elif vol < 2.5:
        return ("Médio",  "#FFD600")   # amarelo
    else:
        return ("Alto",   "#FF5252")   # vermelho


# ==============================
# SETORES DOS ATIVOS (para detecção de concentração)
# ==============================
SETORES = {
    "PETR4.SA": "Energia",    "PETR3.SA": "Energia",
    "PRIO3.SA": "Energia",    "CSAN3.SA": "Energia",
    "VALE3.SA": "Mineração",  "CSNA3.SA": "Siderurgia",
    "GGBR4.SA": "Siderurgia",
    "ITUB4.SA": "Banco",      "BBDC4.SA": "Banco",
    "BBAS3.SA": "Banco",      "SANB11.SA":"Banco",
    "BBSE3.SA": "Seguros",
    "WEGE3.SA": "Indústria",  "EMBR3.SA": "Indústria",
    "SUZB3.SA": "Papel/Celulose","KLBN11.SA":"Papel/Celulose",
    "CPFE3.SA": "Elétrico",   "TAEE11.SA":"Elétrico",
    "EGIE3.SA": "Elétrico",   "ENGI11.SA":"Elétrico",
    "MGLU3.SA": "Varejo",     "VIIA3.SA": "Varejo",
    "LREN3.SA": "Varejo",
    "RENT3.SA": "Aluguel de Veículos",
    "RADL3.SA": "Farmácia",
    "HAPV3.SA": "Saúde",      "RDOR3.SA": "Saúde",
}

# CDI anual base (atualizar conforme necessário)
CDI_ANUAL = 0.1065

# ==============================
# 5. "#FFD600" DE TENDÊNCIA
# ==============================
def _tendencia_ativo(serie):
    """
    Compara preço atual com MM20.
    Retorna ('Alta', cor) / ('Queda', cor) / ('Lateral', cor)
    """
    if len(serie) < 20:
        return ("N/D", "#aaaaaa")
    mm20_atual = serie.rolling(20).mean().iloc[-1]
    preco_atual = serie.iloc[-1]
    diff = (preco_atual - mm20_atual) / mm20_atual * 100
    if diff > 1.5:
        return ("↑ Alta",   ACCENT)
    elif diff < -1.5:
        return ("↓ Queda",  "#FF5252")
    else:
        return ("→ Lateral",ACCENT)

# ==============================
# 6. SCORE GERAL DA CARTEIRA (0–10)
# ==============================
def _calcular_score(analises):
    """
    Nota de 0 a 10 baseada em:
    - 60% retorno médio normalizado
    - 40% risco (vol) médio invertido
    """
    if not analises:
        return 0.0
    ret_medio = sum(a["retorno"] for a in analises) / len(analises)
    vol_medio = sum(a["vol"]     for a in analises) / len(analises)

    # Normaliza retorno: -20% → 0, +20% → 10
    score_ret = max(0, min(10, (ret_medio + 20) / 4))
    # Normaliza risco: vol 0% → 10, vol 4%+ → 0
    score_vol = max(0, min(10, 10 - vol_medio * 2.5))

    return round(score_ret * 0.6 + score_vol * 0.4, 1)

def _cor_score(score):
    if score >= 7:   return "#00C896"   # verde
    elif score >= 4: return "#FFD600"   # amarelo
    else:            return "#FF5252"   # vermelho

# ==============================
# 7. COMPARAÇÃO COM CDI
# ==============================
def _retorno_cdi_periodo(start_str, end_str):
    """Calcula quanto o CDI rendeu no período selecionado."""
    try:
        d1 = datetime.strptime(start_str, "%Y-%m-%d")
        d2 = datetime.strptime(end_str,   "%Y-%m-%d")
        dias = (d2 - d1).days
        return ((1 + CDI_ANUAL) ** (dias / 365) - 1) * 100
    except Exception:
        return None

# ==============================
# 8. DETECÇÃO DE CONCENTRAÇÃO SETORIAL
# ==============================
def _detectar_concentracao(selecionados):
    """Retorna lista de alertas de concentração (setor com 2+ ativos)."""
    contagem = {}
    for t in selecionados:
        setor = SETORES.get(t, "Outros")
        contagem[setor] = contagem.get(setor, []) + [nome_exibicao(t)]
    alertas = []
    for setor, nomes in contagem.items():
        if len(nomes) >= 2:
            alertas.append(f"{setor}: {', '.join(nomes)}")
    return alertas

# ==============================
# 9. MELHOR MÊS DA CARTEIRA
# ==============================
def _melhor_mes(dados, selecionados):
    """Retorna o mês com maior retorno médio da carteira."""
    try:
        import pandas as pd
        frames = []
        for ativo in selecionados:
            s = (dados["Close"] if len(selecionados)==1
                 else dados["Close"][ativo]).dropna()
            frames.append(s.pct_change().dropna())

        carteira = pd.concat(frames, axis=1, sort=False).mean(axis=1)
        mensais  = carteira.resample("ME").sum() * 100
        if mensais.empty:
            return None, None
        idx_max  = mensais.idxmax()
        return idx_max.strftime("%B/%Y"), round(float(mensais.max()), 2)
    except Exception:
        return None, None

# ==============================
# 10. EXPORTAR RELATÓRIO PDF
# ==============================
def exportar_pdf():
    """Gera PDF com gráfico + tabela de análise + insights."""
    from tkinter import filedialog
    import io, textwrap

    fig = _fig_atual.get("fig")
    dados        = _cache.get("dados")
    selecionados = _cache.get("selecionados")

    if fig is None or dados is None:
        btn_pdf.config(text="⚠ Gere o gráfico primeiro", fg="#FF5252")
        root.after(3000, lambda: btn_pdf.config(text="📄 Exportar PDF", fg=TXT))
        return

    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile="relatorio_investimentos.pdf",
        title="Salvar relatório PDF..."
    )
    if not caminho:
        return

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Image, Table, TableStyle)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        # Salva gráfico em buffer
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor=BG)
        buf.seek(0)

        doc   = SimpleDocTemplate(caminho, pagesize=A4,
                                   leftMargin=1.5*cm, rightMargin=1.5*cm,
                                   topMargin=1.5*cm, bottomMargin=1.5*cm)
        story = []
        styles = getSampleStyleSheet()

        titulo_style = ParagraphStyle("titulo", fontSize=16, fontName="Helvetica-Bold",
                                       alignment=TA_CENTER, spaceAfter=4)
        sub_style    = ParagraphStyle("sub",    fontSize=9,  fontName="Helvetica",
                                       alignment=TA_CENTER, textColor=colors.grey, spaceAfter=12)
        sec_style    = ParagraphStyle("sec",    fontSize=11, fontName="Helvetica-Bold",
                                       spaceBefore=12, spaceAfter=4)
        body_style   = ParagraphStyle("body",   fontSize=8,  fontName="Helvetica",
                                       spaceAfter=3, leading=12)

        # Cabeçalho
        story.append(Paragraph("INvest", titulo_style))
        story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", sub_style))

        # Gráfico
        story.append(Paragraph("Evolução dos Ativos", sec_style))
        img = Image(buf, width=16*cm, height=7*cm)
        story.append(img)
        story.append(Spacer(1, 0.3*cm))

        # Tabela de análise
        story.append(Paragraph("Análise do Período", sec_style))
        analises = _calcular_analise(dados, selecionados)

        header = ["Ativo", "Retorno %", "Volatil. %", "Risco", "Máximo", "Mínimo"]
        rows   = [header]
        for a in analises:
            try:
                serie  = (dados["Close"] if len(selecionados)==1
                          else dados["Close"][a["ticker"]]).dropna()
                rows.append([
                    a["nome"],
                    f"{a['retorno']:+.2f}%",
                    f"{a['vol']:.2f}%",
                    _classificar_risco(a["vol"])[0],
                    _fmt_brl(float(serie.max())),
                    _fmt_brl(float(serie.min())),
                ])
            except Exception:
                pass

        tbl = Table(rows, colWidths=[3*cm,2.5*cm,2.5*cm,2*cm,3*cm,3*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor(CARD)),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.HexColor(ACCENT)),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 8),
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [colors.HexColor("#161616"), colors.HexColor("#202020")]),
            ("TEXTCOLOR",  (0,1), (-1,-1), colors.white),
            ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor(BTN)),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.4*cm))

        # Score + CDI
        score = _calcular_score(analises)
        start_yf = _cache.get("start"); end_yf = _cache.get("end")
        story.append(Paragraph("Inteligência do Período", sec_style))
        story.append(Paragraph(f"Score da carteira: {score}/10", body_style))

        # Insights
        frases = _gerar_insights_completo(analises, dados, selecionados,
                                           _cache.get("start"), _cache.get("end"))
        for f in frases:
            story.append(Paragraph(f"• {f['titulo']}: {f['texto']}", body_style))

        doc.build(story)
        btn_pdf.config(text="✔ PDF Salvo!", fg=ACCENT)
        root.after(3000, lambda: btn_pdf.config(text="📄 Exportar PDF", fg=TXT))

    except ImportError:
        # reportlab não instalado
        import subprocess, sys
        subprocess.run([sys.executable, "-m", "pip", "install", "reportlab", "--quiet"])
        btn_pdf.config(text="Instalando... tente novamente", fg=ACCENT)
        root.after(4000, lambda: btn_pdf.config(text="📄 Exportar PDF", fg=TXT))
    except Exception as e:
        btn_pdf.config(text=f"⚠ Erro", fg="#FF5252")
        root.after(3000, lambda: btn_pdf.config(text="📄 Exportar PDF", fg=TXT))

def _gerar_insights_completo(analises, dados, selecionados, start_str, end_str):
    """Gera frases automáticas completas incluindo tendência, CDI, concentração e melhor mês."""
    if not analises: return []

    por_retorno = sorted(analises, key=lambda x: x["retorno"], reverse=True)
    por_vol     = sorted(analises, key=lambda x: x["vol"],     reverse=True)
    por_estab   = sorted(analises, key=lambda x: x["vol"])

    melhor   = por_retorno[0]
    pior     = por_retorno[-1]
    mais_vol = por_vol[0]
    mais_est = por_estab[0]

    frases = []

    # 🏆 Top performer
    sinal = "+" if melhor["retorno"] >= 0 else ""
    frases.append({"icone":"🏆","titulo":"Top performer",
        "texto": f"{melhor['nome']} apresentou o maior retorno no período ({sinal}{melhor['retorno']:.2f}%).",
        "cor":"#FFD600"})

    # 📉 Pior desempenho
    sinal2 = "+" if pior["retorno"] >= 0 else ""
    frases.append({"icone":"📉","titulo":"Menor retorno",
        "texto": f"{pior['nome']} teve o menor desempenho ({sinal2}{pior['retorno']:.2f}%).",
        "cor":"#FF5252"})

    # ⚠ Mais arriscado
    risco_txt, _ = _classificar_risco(mais_vol["vol"])
    frases.append({"icone":"⚠","titulo":"Maior risco",
        "texto": f"{mais_vol['nome']} possui alta volatilidade ({mais_vol['vol']:.2f}%) — risco {risco_txt}.",
        "cor":"#FF9100"})

    # 🛡 Mais estável
    frases.append({"icone":"🛡","titulo":"Mais estável",
        "texto": f"{mais_est['nome']} foi o ativo mais estável (vol. {mais_est['vol']:.2f}%).",
        "cor":"#00E5FF"})

    # 📊 Visão geral de retornos
    positivos = sum(1 for a in analises if a["retorno"] > 0)
    total = len(analises)
    frases.append({"icone":"📊","titulo":"Visão geral",
        "texto": f"{positivos} de {total} ativos ({positivos/total*100:.0f}%) tiveram retorno positivo.",
        "cor":"#aaaaaa"})

    # 5. Tendência por ativo
    tendencias = {"↑ Alta": [], "↓ Queda": [], "→ Lateral": []}
    for a in analises:
        try:
            serie = (dados["Close"] if len(selecionados)==1
                     else dados["Close"][a["ticker"]]).dropna()
            tend, _ = _tendencia_ativo(serie)
            if tend in tendencias:
                tendencias[tend].append(a["nome"])
        except: pass
    partes = []
    if tendencias["↑ Alta"]:    partes.append(f"alta: {', '.join(tendencias['↑ Alta'])}")
    if tendencias["↓ Queda"]:   partes.append(f"queda: {', '.join(tendencias['↓ Queda'])}")
    if tendencias["→ Lateral"]: partes.append(f"lateral: {', '.join(tendencias['→ Lateral'])}")
    if partes:
        frases.append({"icone":"📡","titulo":"Tendências (MM20)",
            "texto": "  |  ".join(partes).capitalize() + ".",
            "cor":"#B2FF59"})

    # 6. Score da carteira
    score = _calcular_score(analises)
    cor_s = _cor_score(score)
    frases.append({"icone":"⭐","titulo":"Score da carteira",
        "texto": f"{score}/10 — baseado em retorno médio e nível de risco dos ativos.",
        "cor": cor_s})

    # 7. Comparação com CDI
    if start_str and end_str:
        cdi_pct = _retorno_cdi_periodo(start_str, end_str)
        if cdi_pct is not None:
            ret_medio = sum(a["retorno"] for a in analises) / len(analises)
            diff = ret_medio - cdi_pct
            sinal_cdi = "acima" if diff >= 0 else "abaixo"
            cor_cdi   = "#00C896" if diff >= 0 else "#FF5252"
            frases.append({"icone":"🏦","titulo":"vs CDI",
                "texto": f"Retorno médio da carteira ({ret_medio:+.2f}%) ficou {abs(diff):.2f}% {sinal_cdi} do CDI ({cdi_pct:.2f}%) no período.",
                "cor": cor_cdi})

    # 8. Concentração setorial
    alertas = _detectar_concentracao(selecionados)
    if alertas:
        frases.append({"icone":"⚡","titulo":"Concentração setorial",
            "texto": "Atenção: " + "; ".join(alertas) + ". Considere diversificar.",
            "cor":"#FFD600"})

    # 9. Melhor mês
    mes, ret_mes = _melhor_mes(dados, selecionados)
    if mes:
        frases.append({"icone":"▸","titulo":"Melhor mês",
            "texto": f"O melhor mês da carteira foi {mes} com retorno médio de {ret_mes:+.2f}%.",
            "cor":"#FFD600"})

    return frases


def _gerar_insights(analises):
    """Wrapper simples (sem dados extras) para compatibilidade."""
    return _gerar_insights_completo(analises, _cache.get("dados"), _cache.get("selecionados"),
                                     _cache.get("start"), _cache.get("end"))


def _desenhar_score_bar(parent, score, cor):
    """Desenha barra visual de progresso do score (0-10) ao lado do título."""
    BAR_W = 120
    BAR_H = 10

    c = tk.Canvas(parent, width=BAR_W, height=BAR_H,
                  bg="#202020", highlightthickness=0)
    c.pack(side="left", padx=(8, 0), pady=1)

    # Fundo
    c.create_rectangle(0, 0, BAR_W, BAR_H,
                        fill=BTN, outline="")
    # Preenchimento proporcional
    fill_w = int((score / 10) * BAR_W)
    if fill_w > 0:
        c.create_rectangle(0, 0, fill_w, BAR_H,
                            fill=cor, outline="")
    # Texto da nota à direita
    tk.Label(parent, text=f"{score}/10", bg="#202020", fg=cor,
             font=("Arial", 8, "bold")).pack(side="left", padx=(4, 0))


def _montar_insights(analises, frame_pai):
    """Renderiza o card de insights."""
    for w in frame_pai.winfo_children(): w.destroy()
    frases = _gerar_insights(analises)

    if not frases:
        tk.Label(frame_pai, text="📈  Gere um gráfico para ver os insights da carteira.",
                 bg="#202020", fg=ACCENT, font=("Arial", 9, "italic"),
                 pady=14).pack()
        return

    for f in frases:
        row = tk.Frame(frame_pai, bg="#202020")
        row.pack(fill="x", padx=8, pady=2)

        tk.Label(row, text=f["icone"], bg="#202020", fg=f["cor"],
                 font=("Arial", 11), width=2).pack(side="left", padx=(0,6))

        col = tk.Frame(row, bg="#202020")
        col.pack(side="left", fill="x", expand=True)

        # Linha do título + score bar (se for score)
        titulo_row = tk.Frame(col, bg="#202020")
        titulo_row.pack(fill="x")

        tk.Label(titulo_row, text=f["titulo"], bg="#202020", fg=f["cor"],
                 font=("Arial", 8, "bold"), anchor="w").pack(side="left")

        # Barra de progresso só para o score
        if f["titulo"] == "Score da carteira":
            try:
                score_val = float(f["texto"].split("/")[0])
                _desenhar_score_bar(titulo_row, score_val, f["cor"])
            except Exception:
                pass

        tk.Label(col, text=f["texto"], bg="#202020", fg=TXT,
                 font=("Arial", 8), anchor="w", wraplength=780).pack(fill="x")


# Cache dos dados para alternar entre modos sem rebaixar
_cache = {"dados": None, "selecionados": None}

def _renderizar(modo):
    """Renderiza gráfico + tabela no modo especificado."""
    dados       = _cache["dados"]
    selecionados= _cache["selecionados"]
    if dados is None: return

    _estado_grafico["modo"] = modo

    # Limpa área do gráfico
    for w in frame_grafico.winfo_children(): w.destroy()

    fig, ax, series = _montar_grafico(dados, selecionados, modo)
    _fig_atual["fig"] = fig   # guarda para exportar
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    _conectar_tooltip(fig, ax, canvas, series, modo)

    # Atualiza botões de modo
    if modo == "preco":
        btn_preco.config(bg=ACCENT, fg="#000000")
        btn_base100.config(bg=BTN, fg=TXT)
    else:
        btn_base100.config(bg=ACCENT, fg="#000000")
        btn_preco.config(bg=BTN, fg=TXT)

    # Tabela
    _montar_tabela(dados, selecionados, frame_tabela)

    # Insights
    analises = _calcular_analise(dados, selecionados)
    _montar_insights(analises, frame_insights)


# figura atual (para exportar PNG)
_fig_atual = {"fig": None}

def exportar_png():
    """Salva o gráfico atual como PNG via diálogo de arquivo."""
    fig = _fig_atual.get("fig")
    if fig is None:
        return
    from tkinter import filedialog
    caminho = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("Imagem PNG", "*.png"), ("Todos os arquivos", "*.*")],
        initialfile="grafico_investimentos.png",
        title="Salvar gráfico como..."
    )
    if caminho:
        fig.savefig(caminho, dpi=150, bbox_inches="tight",
                    facecolor=BG, edgecolor="none")
        btn_exportar.config(text="✔ Salvo!", fg=ACCENT)
        root.after(2500, lambda: btn_exportar.config(text="📥 Exportar PNG", fg=TXT))


def _mostrar_loading():
    """Exibe spinner animado no frame_grafico enquanto baixa os dados."""
    for w in frame_grafico.winfo_children(): w.destroy()
    for w in frame_tabela.winfo_children(): w.destroy()

    frame_load = tk.Frame(frame_grafico, bg=CARD)
    frame_load.pack(expand=True)

    lbl = tk.Label(frame_load, text="⏳  Baixando dados...", bg=CARD, fg=ACCENT,
                   font=("Arial", 13, "bold"))
    lbl.pack(pady=30)

    dots = ["", ".", "..", "..."]
    estado = {"i": 0, "ativo": True}

    def animar():
        if not estado["ativo"]: return
        lbl.config(text=f"⏳  Baixando dados{dots[estado['i'] % 4]}")
        estado["i"] += 1
        root.after(400, animar)

    animar()
    return estado   # retorna para poder parar a animação


def gerar_grafico():
    start = mascara_inicio.get_data_yf()
    end   = mascara_fim.get_data_yf()

    if not start or not end:
        for w in frame_grafico.winfo_children(): w.destroy()
        tk.Label(frame_grafico, text="Data inválida. Use DD/MM/AAAA.",
                 fg="#FF5252", bg=CARD).pack(pady=20); return
    if start >= end:
        for w in frame_grafico.winfo_children(): w.destroy()
        tk.Label(frame_grafico, text="Data final deve ser maior que a inicial.",
                 fg="#FF5252", bg=CARD).pack(pady=20); return

    selecionados = [t for t in ativos_ordem if ativos_vars[t].get()]
    if not selecionados:
        for w in frame_grafico.winfo_children(): w.destroy()
        tk.Label(frame_grafico, text="Selecione ao menos um ativo.",
                 fg=ACCENT, bg=CARD).pack(pady=20); return

    # Mostra loading e desabilita botão
    estado_load = _mostrar_loading()
    btn_gerar.config(state="disabled", text="Carregando...")

    def _baixar():
        try:
            dados = yf.download(selecionados, start=start, end=end, auto_adjust=True)
        except Exception:
            dados = None
        root.after(0, lambda: _pos_download(dados, selecionados, estado_load, start, end))

    threading.Thread(target=_baixar, daemon=True).start()


def _pos_download(dados, selecionados, estado_load, start, end):
    """Chamado na thread principal após o download terminar."""
    estado_load["ativo"] = False
    btn_gerar.config(state="normal", text="  Gerar Gráfico  ")

    for w in frame_grafico.winfo_children(): w.destroy()

    if dados is None or dados.empty:
        tk.Label(frame_grafico, text="Nenhum dado retornado.",
                 fg="#FF5252", bg=CARD).pack(pady=20); return

    _cache["dados"]        = dados
    _cache["selecionados"] = selecionados
    _cache["start"]        = start
    _cache["end"]          = end
    _renderizar("preco")

# ==============================
# COTAÇÕES — MOEDAS + BITCOIN
# ==============================
MOEDAS = [
    ("BTC",  "BTC-USD",  "₿",  "#F7931A"),
    ("USD",  "USDBRL=X", "$",  ACCENT),
    ("EUR",  "EURBRL=X", "€",  "#448AFF"),
    ("GBP",  "GBPBRL=X", "£",  "#E040FB"),
    ("JPY",  "JPYBRL=X", "¥",  "#FF4081"),
    ("CHF",  "CHFBRL=X", "₣",  "#FFFFFF"),
    ("CNY",  "CNYBRL=X", "¥",  "#FF1744"),
    ("AUD",  "AUDBRL=X", "A$", ACCENT),
    ("CAD",  "CADBRL=X", "C$", "#FFD600"),
    ("BRL",  None,        "R$", ACCENT),  # referência fixa
]

# Guarda os Labels para atualizar
_labels_cotacao = {}   # sigla -> (label_valor, label_var)

def _buscar_cotacoes():
    """Roda em thread — busca preços via history() e atualiza labels."""
    for sigla, ticker_yf, simbolo, cor in MOEDAS:
        if ticker_yf is None:
            root.after(0, lambda s=sigla, sm=simbolo, c=cor:
                       _atualizar_label_moeda(s, 1.0, sm, c, 0.0))
            continue
        try:
            hist = yf.Ticker(ticker_yf).history(period="2d")
            if hist.empty or len(hist) < 1:
                continue

            preco = float(hist["Close"].iloc[-1])
            prev  = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else preco
            var   = ((preco - prev) / prev * 100) if prev else 0.0

            root.after(0, lambda s=sigla, p=preco, sm=simbolo, c=cor, v=var:
                       _atualizar_label_moeda(s, p, sm, c, v))
        except Exception:
            pass

def _atualizar_label_moeda(sigla, preco, simbolo, cor, variacao):
    if sigla not in _labels_cotacao:
        return
    lbl_val, lbl_var = _labels_cotacao[sigla]

    if sigla == "BTC":
        texto = _fmt_brl(preco, casas=0)
    elif sigla in ("JPY", "CNY"):
        texto = _fmt_brl(preco, casas=4)
    elif sigla == "BRL":
        texto = "R$ 1,00"
    else:
        texto = _fmt_brl(preco, casas=4)

    lbl_val.config(text=texto, fg=cor)

    sinal = "▲" if variacao >= 0 else "▼"
    cor_var = "#00C896" if variacao >= 0 else "#FF5252"
    lbl_var.config(text=f"{sinal} {abs(variacao):.2f}%", fg=cor_var)

def atualizar_cotacoes():
    """Dispara busca em background e agenda próxima atualização em 60s."""
    for _, lbl_val, lbl_var in [(k, v[0], v[1]) for k, v in _labels_cotacao.items()]:
        lbl_val.config(text="...")
    threading.Thread(target=_buscar_cotacoes, daemon=True).start()
    root.after(300_000, atualizar_cotacoes)

# ==============================
# SIMULADOR CDB
# ==============================
def simular_cdb():
    try:
        valor      = float(entry_valor.get())
        percentual = float(entry_cdi.get())
        dias       = int(entry_dias.get())
        if valor <= 0 or percentual <= 0 or dias <= 0:
            raise ValueError
        taxa  = CDI_ANUAL * (percentual / 100)
        final = valor * (1 + taxa) ** (dias / 365)
        lucro = final - valor
        resultado_cdb.config(
            text=f"▸  Valor final: {_fmt_brl(final)}   |   Lucro: {_fmt_brl(lucro)}",
            fg="#00C896")
    except Exception:
        resultado_cdb.config(text="⚠  Preencha os campos com números válidos", fg="#FF5252")

# ==============================
# CALCULADORA REVERSA CDB
# Dado: meta, % CDI e aporte mensal → tempo necessário
# Dado: meta, % CDI e prazo → aporte mensal necessário
# ==============================
def calcular_meta():
    try:
        meta       = float(entry_meta.get())
        percentual = float(entry_meta_cdi.get())
        if meta <= 0 or percentual <= 0:
            raise ValueError

        taxa_anual  = CDI_ANUAL * (percentual / 100)
        taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1

        modo = modo_var.get()  # "aporte" ou "prazo"

        if modo == "aporte":
            # Usuário informou o aporte mensal → calcula quantos meses
            aporte = float(entry_aporte_ou_prazo.get())
            if aporte <= 0:
                raise ValueError

            # Fórmula: n = log(1 + meta*r/PMT) / log(1+r)
            if taxa_mensal == 0:
                meses = meta / aporte
            else:
                meses = math.log(1 + (meta * taxa_mensal) / aporte) / math.log(1 + taxa_mensal)

            meses = int(math.ceil(meses))
            anos  = meses // 12
            resto = meses % 12

            if anos > 0 and resto > 0:
                tempo_str = f"{anos} ano(s) e {resto} mês(es)  ({meses} meses)"
            elif anos > 0:
                tempo_str = f"{anos} ano(s)  ({meses} meses)"
            else:
                tempo_str = f"{meses} mês(es)"

            resultado_meta.config(
                text=f"⏱  Tempo necessário: {tempo_str}",
                fg="#00C896")

        else:
            # Usuário informou o prazo em meses → calcula aporte mensal
            meses = int(entry_aporte_ou_prazo.get())
            if meses <= 0:
                raise ValueError

            # Fórmula PMT: aporte = meta * r / ((1+r)^n - 1)
            if taxa_mensal == 0:
                aporte = meta / meses
            else:
                aporte = meta * taxa_mensal / ((1 + taxa_mensal) ** meses - 1)

            resultado_meta.config(
                text=f"💸  Aporte mensal necessário: {_fmt_brl(aporte)}",
                fg="#00C896")

    except Exception:
        resultado_meta.config(text="⚠  Preencha os campos corretamente", fg="#FF5252")

def _atualizar_label_modo(*args):
    if modo_var.get() == "aporte":
        label_aporte_ou_prazo.config(text="Aporte mensal (R$)")
        entry_aporte_ou_prazo.delete(0, tk.END)
        entry_aporte_ou_prazo.insert(0, "500")
    else:
        label_aporte_ou_prazo.config(text="Prazo (meses)")
        entry_aporte_ou_prazo.delete(0, tk.END)
        entry_aporte_ou_prazo.insert(0, "24")

# ==============================
# JANELA PRINCIPAL
# ==============================
# Corrige interface borrada no Windows com escala de tela >100% (125%, 150% etc.).
# Sem isso, o Windows "estica" a janela do Tkinter como bitmap em vez de
# renderizar nativamente na resolução real — daí o efeito de texto borrado.
# Só roda no Windows; em outros sistemas (Linux/Mac) o bloco é ignorado.
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # fallback p/ Windows mais antigos
        except Exception:
            pass  # se falhar, app continua funcionando — só sem a correção de DPI

root = tk.Tk()
root.title("INvest")
root.geometry("1280x800")
try:
    # Sincroniza a escala do Tk com o DPI real da tela — complementa o
    # SetProcessDpiAwareness acima, evitando texto pequeno demais em telas
    # de alta resolução depois que o Windows para de "esticar" a janela.
    _dpi_tela = root.winfo_fpixels("1i")
    root.tk.call("tk", "scaling", _dpi_tela / 72.0)
except Exception:
    pass
try:
    root.wm_iconname("📊")
except Exception:
    pass
root.configure(bg=BG)

frame_main = tk.Frame(root, bg=BG)
frame_main.pack(fill="both", expand=True)

# ── SIDEBAR ──
frame_sidebar = tk.Frame(frame_main, bg=CARD, width=210)
frame_sidebar.pack(side="left", fill="y", padx=(10, 0), pady=10)
frame_sidebar.pack_propagate(False)

tk.Label(frame_sidebar, text="📋  Ativos", bg=CARD, fg=ACCENT,
         font=("Arial", 11, "bold")).pack(pady=(10, 4))

frame_btns_sel = tk.Frame(frame_sidebar, bg=CARD)
frame_btns_sel.pack(fill="x", padx=6, pady=(0, 6))
tk.Button(frame_btns_sel, text="Todos", bg=BTN, fg=TXT, font=("Arial", 8),
          relief="flat", cursor="hand2", command=selecionar_todos
          ).pack(side="left", expand=True, fill="x", padx=(0, 2))
tk.Button(frame_btns_sel, text="Nenhum", bg=BTN, fg=TXT, font=("Arial", 8),
          relief="flat", cursor="hand2", command=desmarcar_todos
          ).pack(side="left", expand=True, fill="x")

frame_scroll_container = tk.Frame(frame_sidebar, bg=CARD)
frame_scroll_container.pack(fill="both", expand=True, padx=4)

canvas_scroll = tk.Canvas(frame_scroll_container, bg=CARD, highlightthickness=0)
scrollbar = ttk.Scrollbar(frame_scroll_container, orient="vertical",
                          command=canvas_scroll.yview)
canvas_scroll.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas_scroll.pack(side="left", fill="both", expand=True)

frame_lista_ativos = tk.Frame(canvas_scroll, bg=CARD)
canvas_scroll.create_window((0, 0), window=frame_lista_ativos, anchor="nw")
frame_lista_ativos.bind("<Configure>",
    lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
canvas_scroll.bind_all("<MouseWheel>",
    lambda e: canvas_scroll.yview_scroll(int(-1*(e.delta/120)), "units"))

tk.Frame(frame_sidebar, bg=BTN, height=1).pack(fill="x", padx=6, pady=6)
tk.Label(frame_sidebar, text="🔍 Buscar ativo:", bg=CARD, fg="#aaaaaa",
         font=("Arial", 8)).pack(padx=6, anchor="w")

PLACEHOLDER_BUSCA = "ex: MXRF11, Vale, BOVA11..."

frame_busca_ativo = tk.Frame(frame_sidebar, bg=CARD)
frame_busca_ativo.pack(fill="x", padx=6, pady=(2, 0))

entry_busca_ativo = tk.Entry(frame_busca_ativo, bg=BTN, fg="#aaaaaa",
                              insertbackground=TXT, font=("Arial", 9))
entry_busca_ativo.insert(0, PLACEHOLDER_BUSCA)
entry_busca_ativo.bind("<FocusIn>", lambda e: (
    limpar_entry_placeholder(entry_busca_ativo, PLACEHOLDER_BUSCA),
    _renderizar_resultados_busca(entry_busca_ativo.get())
))
entry_busca_ativo.bind("<FocusOut>", lambda e: restaurar_placeholder(entry_busca_ativo, PLACEHOLDER_BUSCA))
entry_busca_ativo.bind("<KeyRelease>", _on_busca_ativo_change)
entry_busca_ativo.pack(fill="x")

frame_resultados_busca = tk.Frame(frame_sidebar, bg=CARD)
frame_resultados_busca.pack(fill="x", padx=2, pady=(4, 0))

label_status = tk.Label(frame_sidebar, text="", bg=CARD, fg=ACCENT,
                         font=("Arial", 8), wraplength=160)
label_status.pack(padx=6, pady=4)

# Popula a lista de "⭐ Populares" assim que a sidebar existe
_renderizar_resultados_busca("")

# ── PAINEL DE COTAÇÕES ──
tk.Frame(frame_sidebar, bg=BTN, height=1).pack(fill="x", padx=6, pady=(4, 0))

frame_cab_cotacao = tk.Frame(frame_sidebar, bg=CARD)
frame_cab_cotacao.pack(fill="x", padx=6, pady=(4, 2))

tk.Label(frame_cab_cotacao, text="💱  Cotações vs BRL", bg=CARD, fg=ACCENT,
         font=("Arial", 9, "bold")).pack(side="left")

tk.Button(frame_cab_cotacao, text="↻", bg=BTN, fg=ACCENT,
          font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
          command=atualizar_cotacoes).pack(side="right")

frame_cotacoes = tk.Frame(frame_sidebar, bg=CARD)
frame_cotacoes.pack(fill="x", padx=6, pady=(0, 6))

for sigla, ticker_yf, simbolo, cor in MOEDAS:
    row = tk.Frame(frame_cotacoes, bg=CARD)
    row.pack(fill="x", pady=1)

    # Ícone colorido + sigla
    tk.Label(row, text=f"{simbolo} {sigla}", bg=CARD, fg=cor,
             font=("Arial", 8, "bold"), width=7, anchor="w").pack(side="left")

    # Valor
    lbl_val = tk.Label(row, text="...", bg=CARD, fg=cor,
                       font=("Arial", 8), width=10, anchor="e")
    lbl_val.pack(side="left")

    # Variação %
    lbl_var = tk.Label(row, text="", bg=CARD, fg="#aaaaaa",
                       font=("Arial", 7), width=8, anchor="e")
    lbl_var.pack(side="left")

    _labels_cotacao[sigla] = (lbl_val, lbl_var)

# Inicia cotações ao abrir
root.after(500, atualizar_cotacoes)

# ── CONTEÚDO DIREITO com scroll vertical ──
frame_direito = tk.Frame(frame_main, bg=BG)
frame_direito.pack(side="left", fill="both", expand=True)

# Topo fixo (datas + botões) — FORA do scroll
frame_topo = tk.Frame(frame_direito, bg=BG)
frame_topo.pack(fill="x", padx=10, pady=(10, 6))

# Canvas de scroll para o resto
_scroll_canvas = tk.Canvas(frame_direito, bg=BG, highlightthickness=0)
_scroll_vbar   = ttk.Scrollbar(frame_direito, orient="vertical", command=_scroll_canvas.yview)
_scroll_canvas.configure(yscrollcommand=_scroll_vbar.set)
_scroll_vbar.pack(side="right", fill="y")
_scroll_canvas.pack(side="left", fill="both", expand=True)

frame_conteudo = tk.Frame(_scroll_canvas, bg=BG)
_scroll_window = _scroll_canvas.create_window((0, 0), window=frame_conteudo, anchor="nw")

def _on_conteudo_configure(e):
    _scroll_canvas.configure(scrollregion=_scroll_canvas.bbox("all"))
def _on_canvas_configure(e):
    _scroll_canvas.itemconfig(_scroll_window, width=e.width)
frame_conteudo.bind("<Configure>", _on_conteudo_configure)
_scroll_canvas.bind("<Configure>", _on_canvas_configure)
_scroll_canvas.bind_all("<MouseWheel>",
    lambda e: _scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

# Data início
tk.Label(frame_topo, text="Data início", bg=BG, fg=TXT,
         font=("Arial", 9)).pack(side="left", padx=(0, 4))
entry_inicio = tk.Entry(frame_topo, width=12, bg=BTN, fg="#aaaaaa",
                        insertbackground=TXT, font=("Arial", 9))
entry_inicio.insert(0, "DD/MM/AAAA")
entry_inicio.bind("<FocusIn>",  lambda e: limpar_entry_placeholder(entry_inicio, "DD/MM/AAAA"))
entry_inicio.bind("<FocusOut>", lambda e: restaurar_placeholder(entry_inicio, "DD/MM/AAAA"))
entry_inicio.pack(side="left")
mascara_inicio = MascaraData(entry_inicio)

# Data fim
tk.Label(frame_topo, text="Data fim", bg=BG, fg=TXT,
         font=("Arial", 9)).pack(side="left", padx=(12, 4))
entry_fim = tk.Entry(frame_topo, width=12, bg=BTN, fg="#aaaaaa",
                     insertbackground=TXT, font=("Arial", 9))
entry_fim.insert(0, "DD/MM/AAAA")
entry_fim.bind("<FocusIn>",  lambda e: limpar_entry_placeholder(entry_fim, "DD/MM/AAAA"))
entry_fim.bind("<FocusOut>", lambda e: restaurar_placeholder(entry_fim, "DD/MM/AAAA"))
entry_fim.pack(side="left")
mascara_fim = MascaraData(entry_fim)

btn_gerar = tk.Button(frame_topo, text="  Gerar Gráfico  ", bg=ACCENT, fg="#000000",
                      font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
                      command=gerar_grafico)
btn_gerar.pack(side="left", padx=(0, 6))

btn_exportar = tk.Button(frame_topo, text="📥 Exportar PNG", bg=BTN, fg=TXT,
                         font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
                         command=exportar_png)
btn_exportar.pack(side="left", padx=(0, 3))

btn_pdf = tk.Button(frame_topo, text="📄 Exportar PDF", bg=BTN, fg=TXT,
                    font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
                    command=exportar_pdf)
btn_pdf.pack(side="left", padx=(0, 14))

# Botões de alternância de modo
btn_preco = tk.Button(frame_topo, text="Preço (R$)", bg=ACCENT, fg="#000000",
                      font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
                      command=lambda: _renderizar("preco"))
btn_preco.pack(side="left", padx=(0, 3))

btn_base100 = tk.Button(frame_topo, text="Base 100 (%)", bg=BTN, fg=TXT,
                        font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
                        command=lambda: _renderizar("base100"))
btn_base100.pack(side="left")

# Botões média móvel
tk.Label(frame_topo, text="|", bg=BG, fg="#444").pack(side="left", padx=6)
tk.Label(frame_topo, text="MM:", bg=BG, fg="#aaaaaa",
         font=("Arial", 8)).pack(side="left", padx=(0, 3))

btn_mm20 = tk.Button(frame_topo, text="20", bg=BTN, fg=TXT,
                     font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
                     command=lambda: _toggle_mm(20))
btn_mm20.pack(side="left", padx=(0, 2))

btn_mm50 = tk.Button(frame_topo, text="50", bg=BTN, fg=TXT,
                     font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
                     command=lambda: _toggle_mm(50))
btn_mm50.pack(side="left")

# -- GRÁFICO --
frame_grafico = tk.Frame(frame_conteudo, bg=CARD)
frame_grafico.pack(fill="both", expand=True)

# -- TABELA DE ANÁLISE --
frame_tabela_outer = tk.Frame(frame_conteudo, bg=CARD)
frame_tabela_outer.pack(fill="x", pady=(4, 0))

tk.Label(frame_tabela_outer, text="📊  Análise do Período",
         bg=CARD, fg=ACCENT, font=("Arial", 9, "bold"),
         pady=4).pack(anchor="w", padx=8)

frame_tabela = tk.Frame(frame_tabela_outer, bg=CARD)
frame_tabela.pack(fill="x", padx=4, pady=(0, 4))

# -- CARD DE INSIGHTS --
frame_insights_outer = tk.Frame(frame_conteudo, bg=ACCENT)
frame_insights_outer.pack(fill="x", pady=(6, 0))

frame_insights_inner = tk.Frame(frame_insights_outer, bg="#202020")
frame_insights_inner.pack(fill="both", expand=True, padx=2, pady=2)

cab_ins = tk.Frame(frame_insights_inner, bg="#0d0d0d")
cab_ins.pack(fill="x")
tk.Label(cab_ins, text="🧠  Inteligência do Período", bg="#0d0d0d", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=6).pack(side="left", padx=12)

frame_insights = tk.Frame(frame_insights_inner, bg="#202020")
frame_insights.pack(fill="x", pady=(4, 8))

# -- ÁREA DOS DOIS CARDS (CDB + META) --
frame_cards = tk.Frame(frame_conteudo, bg=BG)
frame_cards.pack(fill="x", pady=(10, 0))

# ── CARD ESQUERDO: Simulador CDB ──
frame_cdb_outer = tk.Frame(frame_cards, bg=ACCENT)
frame_cdb_outer.pack(side="left", fill="both", expand=True, padx=(0, 5))

frame_cdb = tk.Frame(frame_cdb_outer, bg=CDB_BG)
frame_cdb.pack(fill="both", expand=True, padx=2, pady=2)

cab_cdb = tk.Frame(frame_cdb, bg="#0a2235")
cab_cdb.pack(fill="x")
tk.Label(cab_cdb, text="💵  Simulador de CDB", bg="#0a2235", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=6).pack(side="left", padx=10)

linha_inputs = tk.Frame(frame_cdb, bg=CDB_BG)
linha_inputs.pack(pady=6)

def make_label(parent, text):
    tk.Label(parent, text=text, bg=CDB_BG, fg="#aaaaaa", font=("Arial", 8)).pack()

def limpar_cdb(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg=TXT)

col1 = tk.Frame(linha_inputs, bg=CDB_BG); col1.pack(side="left", padx=8)
make_label(col1, "Valor (R$)")
entry_valor = tk.Entry(col1, width=11, bg=BTN, fg=TXT, insertbackground=TXT, justify="center")
entry_valor.insert(0, "2000")
entry_valor.bind("<FocusIn>", lambda e: limpar_cdb(entry_valor, "2000"))
entry_valor.pack()

col2 = tk.Frame(linha_inputs, bg=CDB_BG); col2.pack(side="left", padx=8)
make_label(col2, "% do CDI")
entry_cdi = tk.Entry(col2, width=11, bg=BTN, fg=TXT, insertbackground=TXT, justify="center")
entry_cdi.insert(0, "110")
entry_cdi.bind("<FocusIn>", lambda e: limpar_cdb(entry_cdi, "110"))
entry_cdi.pack()

col3 = tk.Frame(linha_inputs, bg=CDB_BG); col3.pack(side="left", padx=8)
make_label(col3, "Dias")
entry_dias = tk.Entry(col3, width=11, bg=BTN, fg=TXT, insertbackground=TXT, justify="center")
entry_dias.insert(0, "365")
entry_dias.bind("<FocusIn>", lambda e: limpar_cdb(entry_dias, "365"))
entry_dias.pack()

col4 = tk.Frame(linha_inputs, bg=CDB_BG); col4.pack(side="left", padx=8)
make_label(col4, " ")
tk.Button(col4, text=" Simular ", bg=ACCENT, fg="#000000",
          font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
          command=simular_cdb).pack()

resultado_cdb = tk.Label(frame_cdb, text="", bg=CDB_BG, fg=ACCENT,
                          font=("Arial", 10, "bold"), pady=5)
resultado_cdb.pack()

# ── CARD DIREITO: Calculadora de Meta ──
frame_meta_outer = tk.Frame(frame_cards, bg=ACCENT)
frame_meta_outer.pack(side="left", fill="both", expand=True, padx=(5, 0))

META_BG = "#1a1a0a"
frame_meta = tk.Frame(frame_meta_outer, bg=META_BG)
frame_meta.pack(fill="both", expand=True, padx=2, pady=2)

cab_meta = tk.Frame(frame_meta, bg="#2a2a00")
cab_meta.pack(fill="x")
tk.Label(cab_meta, text="🎯  Calculadora de Meta", bg="#2a2a00", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=6).pack(side="left", padx=10)

# Modo: calcular prazo OU calcular aporte
modo_var = tk.StringVar(value="aporte")
modo_var.trace_add("write", _atualizar_label_modo)

frame_modo = tk.Frame(frame_meta, bg=META_BG)
frame_modo.pack(pady=(5, 2))

tk.Label(frame_modo, text="Quero calcular:", bg=META_BG, fg="#aaaaaa",
         font=("Arial", 8)).pack(side="left", padx=(8, 6))

tk.Radiobutton(frame_modo, text="Tempo necessário", variable=modo_var, value="aporte",
               bg=META_BG, fg=TXT, selectcolor="#2a2a10", activebackground=META_BG,
               font=("Arial", 8), cursor="hand2").pack(side="left", padx=4)

tk.Radiobutton(frame_modo, text="Aporte mensal", variable=modo_var, value="prazo",
               bg=META_BG, fg=TXT, selectcolor="#2a2a10", activebackground=META_BG,
               font=("Arial", 8), cursor="hand2").pack(side="left", padx=4)

linha_meta = tk.Frame(frame_meta, bg=META_BG)
linha_meta.pack(pady=6)

def make_label_meta(parent, text):
    tk.Label(parent, text=text, bg=META_BG, fg="#aaaaaa", font=("Arial", 8)).pack()

# Meta (R$)
m1 = tk.Frame(linha_meta, bg=META_BG); m1.pack(side="left", padx=8)
make_label_meta(m1, "Meta (R$)")
entry_meta = tk.Entry(m1, width=11, bg=BTN, fg=TXT, insertbackground=TXT, justify="center")
entry_meta.insert(0, "30000")
entry_meta.pack()

# % CDI
m2 = tk.Frame(linha_meta, bg=META_BG); m2.pack(side="left", padx=8)
make_label_meta(m2, "% do CDI")
entry_meta_cdi = tk.Entry(m2, width=11, bg=BTN, fg=TXT, insertbackground=TXT, justify="center")
entry_meta_cdi.insert(0, "110")
entry_meta_cdi.pack()

# Aporte ou Prazo (dinâmico)
m3 = tk.Frame(linha_meta, bg=META_BG); m3.pack(side="left", padx=8)
label_aporte_ou_prazo = tk.Label(m3, text="Aporte mensal (R$)", bg=META_BG,
                                  fg="#aaaaaa", font=("Arial", 8))
label_aporte_ou_prazo.pack()
entry_aporte_ou_prazo = tk.Entry(m3, width=11, bg=BTN, fg=TXT,
                                  insertbackground=TXT, justify="center")
entry_aporte_ou_prazo.insert(0, "500")
entry_aporte_ou_prazo.pack()

# Botão
m4 = tk.Frame(linha_meta, bg=META_BG); m4.pack(side="left", padx=8)
make_label_meta(m4, " ")
tk.Button(m4, text=" Calcular ", bg=ACCENT, fg="#161616",
          font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
          command=calcular_meta).pack()

resultado_meta = tk.Label(frame_meta, text="", bg=META_BG, fg=ACCENT,
                           font=("Arial", 10, "bold"), pady=5)
resultado_meta.pack()


# ======================================================
# ETAPA 5 — CARTEIRA PESSOAL (Tópicos 1-5)
# ======================================================
import math

CARTEIRA_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carteira.json")

# ── 1b. Histórico de patrimônio (SQLite3) ──
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historico.db")

def _init_db():
    """Cria o banco SQLite e a tabela de histórico se não existirem."""
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico_patrimonio (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            data        TEXT    NOT NULL,
            custo_total REAL    NOT NULL,
            patrimonio  REAL    NOT NULL,
            lucro_rs    REAL    NOT NULL,
            lucro_pct   REAL    NOT NULL,
            n_ativos    INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def _registrar_patrimonio(custo_total, patrimonio, lucro_rs, lucro_pct, n_ativos):
    """
    Salva um snapshot do patrimônio atual no banco.
    Chamado automaticamente após cada atualização da carteira.
    Evita duplicatas — só registra uma vez por dia.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        hoje = datetime.now().strftime("%Y-%m-%d")
        # Verifica se já registrou hoje
        cur.execute("SELECT id FROM historico_patrimonio WHERE data = ?", (hoje,))
        if cur.fetchone():
            # Atualiza o registro de hoje em vez de duplicar
            cur.execute("""
                UPDATE historico_patrimonio
                SET custo_total=?, patrimonio=?, lucro_rs=?, lucro_pct=?, n_ativos=?
                WHERE data=?
            """, (custo_total, patrimonio, lucro_rs, lucro_pct, n_ativos, hoje))
        else:
            cur.execute("""
                INSERT INTO historico_patrimonio
                    (data, custo_total, patrimonio, lucro_rs, lucro_pct, n_ativos)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (hoje, custo_total, patrimonio, lucro_rs, lucro_pct, n_ativos))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[SQLite] Erro ao registrar patrimônio: {e}")

def _buscar_historico(dias=90):
    """
    Retorna os últimos N dias do histórico como lista de dicts.
    Usado para plotar a evolução do patrimônio ao longo do tempo.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        cur.execute("""
            SELECT data, custo_total, patrimonio, lucro_rs, lucro_pct, n_ativos
            FROM historico_patrimonio
            ORDER BY data DESC
            LIMIT ?
        """, (dias,))
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "data":        r[0],
                "custo_total": r[1],
                "patrimonio":  r[2],
                "lucro_rs":    r[3],
                "lucro_pct":   r[4],
                "n_ativos":    r[5],
            }
            for r in reversed(rows)  # ordem cronológica
        ]
    except Exception as e:
        print(f"[SQLite] Erro ao buscar histórico: {e}")
        return []

# Inicializa o banco na inicialização do app
_init_db()

# ── 1. Persistência JSON ──
def _carregar_carteira():
    """Carrega carteira do JSON com validação de campos."""
    if os.path.exists(CARTEIRA_JSON):
        try:
            with open(CARTEIRA_JSON, encoding="utf-8") as f:
                dados = json.load(f)
            if not isinstance(dados, dict):
                return {}
            validos = {}
            for ticker, pos in dados.items():
                ticker = ticker.strip()
                if not ticker:
                    continue
                if all(k in pos for k in ("qtd","preco_medio","data_compra")):
                    pos["qtd"]         = float(pos["qtd"])
                    pos["preco_medio"] = float(pos["preco_medio"])
                    validos[ticker]    = pos
            return validos
        except Exception:
            try:
                import shutil
                shutil.copy(CARTEIRA_JSON, CARTEIRA_JSON + ".bak")
            except Exception:
                pass
            return {}
    return {}

def _salvar_carteira(carteira):
    with open(CARTEIRA_JSON, "w", encoding="utf-8") as f:
        json.dump(carteira, f, ensure_ascii=False, indent=2)
    try:
        n = len(carteira)
        root.title(f"INvest — {n} ativo{'s' if n!=1 else ''} na carteira")
    except Exception:
        pass

_carteira = _carregar_carteira()

# Cache dos dados calculados na última atualização da carteira (P&L, indicadores de
# risco) — o Assistente da Carteira consulta isso em vez de reprocessar/rebaixar dados.
_cache_analitico = {"rows": [], "indicadores": {}, "atualizado_em": None}

# ── 2 & 3. Busca preço atual + cálculo de P&L ──

# ======================================================
# CARTEIRA — CDBs
# ======================================================
CDB_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carteira_cdbs.json")

def _carregar_cdbs():
    """Carrega CDBs do JSON com validação de campos."""
    if os.path.exists(CDB_JSON):
        try:
            with open(CDB_JSON, encoding="utf-8") as f:
                dados = json.load(f)
            # Valida que é lista e cada item tem os campos necessários
            if not isinstance(dados, list):
                return []
            validos = []
            for item in dados:
                if all(k in item for k in ("nome","valor","pct_cdi","data")):
                    # Garante tipos corretos
                    item["valor"]   = float(item["valor"])
                    item["pct_cdi"] = float(item["pct_cdi"])
                    validos.append(item)
            return validos
        except Exception:
            # JSON corrompido — faz backup e começa do zero
            try:
                import shutil
                shutil.copy(CDB_JSON, CDB_JSON + ".bak")
            except Exception:
                pass
            return []
    return []   # lista de dicts: {nome, valor, pct_cdi, data}

def _salvar_cdbs(cdbs):
    with open(CDB_JSON, "w", encoding="utf-8") as f:
        json.dump(cdbs, f, ensure_ascii=False, indent=2)

_cdbs = _carregar_cdbs()

def _calcular_rendimento_cdb(valor, pct_cdi, data_str):
    """Calcula rendimento bruto acumulado do CDB até hoje."""
    try:
        d1   = datetime.strptime(data_str, "%d/%m/%Y")
        dias = max((datetime.now() - d1).days, 0)
        taxa_periodo = ((1 + CDI_ANUAL * (pct_cdi/100)) ** (dias/365)) - 1
        rendimento   = valor * taxa_periodo
        total        = valor + rendimento
        return rendimento, total, dias
    except Exception:
        return 0.0, float(valor), 0

def _adicionar_cdb():
    nome_s  = entry_cdb_nome.get().strip()
    valor_s = entry_cdb_valor.get().strip()
    pct_s   = entry_cdb_pct.get().strip()
    data_s  = entry_cdb_data.get().strip()

    if not nome_s or nome_s == "ex: Nubank CDB":
        lbl_cdb_status.config(text="⚠ Digite um nome para o CDB.", fg="#FF5252"); return
    try:
        valor = float(valor_s.replace(",", "."))
        pct   = float(pct_s.replace(",", "."))
        if valor <= 0 or pct <= 0: raise ValueError
    except ValueError:
        lbl_cdb_status.config(text="⚠ Valor e % CDI devem ser números positivos.", fg="#FF5252"); return
    try:
        datetime.strptime(data_s, "%d/%m/%Y")
    except ValueError:
        lbl_cdb_status.config(text="⚠ Data inválida. Use DD/MM/AAAA.", fg="#FF5252"); return

    venc_s = entry_cdb_venc.get().strip()
    venc_val = venc_s if (venc_s and venc_s != "DD/MM/AAAA") else "—"
    _cdbs.append({"nome": nome_s, "valor": valor, "pct_cdi": pct, "data": data_s, "vencimento": venc_val})
    _salvar_cdbs(_cdbs)
    lbl_cdb_status.config(text=f"✔ CDB '{nome_s}' adicionado!", fg=ACCENT)
    _renderizar_cdbs()

def _remover_cdb(idx):
    if 0 <= idx < len(_cdbs):
        del _cdbs[idx]
        _salvar_cdbs(_cdbs)
        _renderizar_cdbs()

def _renderizar_cdbs():
    """Renderiza tabela de CDBs da carteira."""
    for w in frame_cdb_cart_tabela.winfo_children(): w.destroy()

    if not _cdbs:
        tk.Label(frame_cdb_cart_tabela,
                 text="Nenhum CDB registrado. Adicione acima.",
                 bg="#161616", fg=ACCENT, font=("Arial", 9, "italic"), pady=10).pack()
        return

    CAB_BG = CARD
    cols   = ["Nome/Banco", "Aplicado (R$)", "% CDI", "Data", "Vencimento", "Dias", "Rendimento R$", "Total R$", "Rent. %", "Alerta", "Ação"]
    widths = [12, 10, 5, 10, 10, 5, 12, 10, 7, 7, 5]

    tbl = tk.Frame(frame_cdb_cart_tabela, bg=CAB_BG)
    tbl.pack(fill="x", padx=6)

    for c, (col, w) in enumerate(zip(cols, widths)):
        tk.Label(tbl, text=col, bg=CAB_BG, fg=ACCENT,
                 font=("Arial", 8, "bold"), width=w,
                 anchor="center").grid(row=0, column=c, padx=1, pady=3, sticky="ew")

    tk.Frame(tbl, bg=BTN, height=1).grid(
        row=1, column=0, columnspan=len(cols), sticky="ew")

    total_aplicado = total_rendimento = total_atual = 0

    for idx, cdb in enumerate(_cdbs):
        rend, total, dias = _calcular_rendimento_cdb(
            cdb["valor"], cdb["pct_cdi"], cdb["data"])
        rent_pct = (rend / cdb["valor"] * 100) if cdb["valor"] > 0 else 0
        row_bg   = "#161616" if idx % 2 == 0 else "#202020"
        cor_rend = "#00C896"
        ri       = idx + 2

        # Alerta de vencimento
        venc = cdb.get("vencimento", "—")
        alerta_venc = ""
        cor_alerta  = "#aaaaaa"
        if venc and venc != "—":
            try:
                dv = datetime.strptime(venc, "%d/%m/%Y")
                dias_venc = (dv - datetime.now()).days
                if dias_venc < 0:
                    alerta_venc = "VENCIDO"; cor_alerta = "#FF5252"
                elif dias_venc <= 30:
                    alerta_venc = f"{dias_venc}d ⚠"; cor_alerta = "#FFD600"
                elif dias_venc <= 90:
                    alerta_venc = f"{dias_venc}d"; cor_alerta = ACCENT
                else:
                    alerta_venc = f"{dias_venc}d"; cor_alerta = ACCENT
            except: pass
        dados_row = [
            (cdb["nome"],                ACCENT),
            (_fmt_num_br(cdb['valor']),   TXT),
            (f"{cdb['pct_cdi']:.0f}%",  TXT),
            (cdb["data"],                TXT),
            (venc,                       "#aaaaaa"),
            (str(dias),                  "#aaaaaa"),
            (_fmt_num_br(rend, forcar_sinal=True), cor_rend),
            (_fmt_num_br(total),          cor_rend),
            (f"{rent_pct:.2f}%",         cor_rend),
            (alerta_venc,                cor_alerta),
        ]
        for c, (val, fg) in enumerate(dados_row):
            tk.Label(tbl, text=val, bg=row_bg, fg=fg,
                     font=("Arial", 8), width=widths[c],
                     anchor="center").grid(row=ri, column=c, padx=1, pady=2, sticky="ew")

        tk.Button(tbl, text="✕", bg="#2a0000", fg="#FF5252",
                  font=("Arial", 8, "bold"), relief="flat", cursor="hand2", width=2,
                  command=lambda i=idx: _remover_cdb(i)
                  ).grid(row=ri, column=10, padx=1, pady=2)

        total_aplicado  += cdb["valor"]
        total_rendimento += rend
        total_atual      += total

    # Linha de totais
    rent_total_pct = (total_rendimento / total_aplicado * 100) if total_aplicado > 0 else 0
    sep_r = len(_cdbs) + 2
    tk.Frame(tbl, bg=BTN, height=1).grid(
        row=sep_r, column=0, columnspan=len(cols), sticky="ew", pady=2)
    tot_row = sep_r + 1
    resumo = [
        ("TOTAL",                     ACCENT),
        (_fmt_num_br(total_aplicado), ACCENT),
        ("", "#aaaaaa"), ("", "#aaaaaa"), ("", "#aaaaaa"), ("", "#aaaaaa"),
        (_fmt_num_br(total_rendimento, forcar_sinal=True), ACCENT),
        (_fmt_num_br(total_atual),    ACCENT),
        (f"{rent_total_pct:.2f}%",    ACCENT),
        ("", "#aaaaaa"), ("", ""),
    ]
    for c, (val, fg) in enumerate(resumo):
        tk.Label(tbl, text=val, bg=CARD, fg=fg,
                 font=("Arial", 8, "bold"), width=widths[c],
                 anchor="center").grid(row=tot_row, column=c, padx=1, pady=3, sticky="ew")


# ======================================================
# ETAPA 5 — Tópicos 6 a 10
# ======================================================

# ── 6. Indicadores de Risco Avançados ──
def _calcular_beta(serie_ativo, serie_ibov):
    try:
        import pandas as pd
        ret_a = serie_ativo.pct_change().dropna()
        ret_b = serie_ibov.pct_change().dropna()
        df = pd.concat([ret_a, ret_b], axis=1, sort=False).dropna()
        if len(df) < 10: return None
        cov = df.iloc[:,0].cov(df.iloc[:,1])
        var = df.iloc[:,1].var()
        return round(cov/var, 2) if var != 0 else None
    except: return None

def _calcular_sharpe(serie):
    try:
        ret_d = serie.pct_change().dropna()
        if len(ret_d) < 2: return None
        ret_a = float(ret_d.mean() * 252)
        vol_a = float(ret_d.std() * (252**0.5))
        if vol_a == 0 or vol_a != vol_a: return None  # vol_a != vol_a detecta NaN
        resultado = round((ret_a - CDI_ANUAL) / vol_a, 2)
        return resultado if resultado == resultado else None  # descarta NaN
    except: return None

def _calcular_drawdown_max(serie):
    try:
        if serie is None or len(serie) < 2: return None
        pico = serie.cummax()
        dd   = (serie - pico) / pico * 100
        resultado = round(float(dd.min()), 2)
        return resultado if resultado == resultado else None  # descarta NaN
    except: return None

def _buscar_ibov_para_carteira(start, end):
    try:
        d = yf.download("^BVSP", start=start, end=end,
                        auto_adjust=True, progress=False)
        return d["Close"].dropna() if not d.empty else None
    except: return None

def _calcular_indicadores_avancados_carteira(carteira, precos):
    """Calcula Beta, Sharpe e Drawdown para cada ativo da carteira."""
    if not carteira: return {}
    datas = []
    for pos in carteira.values():
        try: datas.append(datetime.strptime(pos["data_compra"], "%d/%m/%Y"))
        except: pass
    if not datas: return {}
    start = min(datas).strftime("%Y-%m-%d")
    end   = datetime.now().strftime("%Y-%m-%d")
    tickers = list(carteira.keys())
    try:
        dados = yf.download(tickers, start=start, end=end,
                            auto_adjust=True, progress=False)
        if dados.empty: return {}
    except: return {}
    serie_ibov = _buscar_ibov_para_carteira(start, end)
    result = {}
    for ticker in tickers:
        try:
            serie = (dados["Close"] if len(tickers)==1
                     else dados["Close"][ticker]).dropna()
            result[ticker] = {
                "beta":     _calcular_beta(serie, serie_ibov) if serie_ibov is not None else None,
                "sharpe":   _calcular_sharpe(serie),
                "drawdown": _calcular_drawdown_max(serie),
            }
        except: pass
    return result

def _grafico_evolucao_com_dados(dados, carteira, frame_pai):
    """Plota evolução do patrimônio com dados já baixados."""
    for w in frame_pai.winfo_children(): w.destroy()
    tickers = list(carteira.keys())
    try:
        import pandas as pd
        patrimonio_total = pd.Series(dtype=float)
        for ticker, pos in carteira.items():
            try:
                serie = (dados["Close"] if len(tickers)==1
                         else dados["Close"][ticker]).dropna()
                patrimonio_total = patrimonio_total.add(serie * float(pos["qtd"]), fill_value=0)
            except: pass
        if patrimonio_total.empty:
            return
        fig = plt.figure(figsize=(11, 3.0)); fig.patch.set_facecolor(BG)
        ax  = fig.add_axes([0.07, 0.20, 0.88, 0.70]); ax.set_facecolor("#161616")
        ax.fill_between(patrimonio_total.index, patrimonio_total.values, alpha=0.2, color=ACCENT)
        ax.plot(patrimonio_total.index, patrimonio_total.values, color=ACCENT, linewidth=2, label="Patrimônio")
        # Linha de custo total investido
        custo_total = sum(float(p["qtd"])*float(p["preco_medio"]) for p in carteira.values())
        ax.axhline(custo_total, color="#FFD600", linewidth=1.2, linestyle="--", alpha=0.8, label=f"Custo {_fmt_brl(custo_total, casas=0)}")
        leg = ax.legend(loc="upper left", frameon=False, fontsize=7)
        for t in leg.get_texts(): t.set_color("#FFF")
        ax.set_title("Evolução do Patrimônio", color=TXT, fontsize=10, fontweight="bold")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_: _fmt_brl(x, casas=0)))
        import matplotlib.dates as md3
        ax.xaxis.set_major_locator(md3.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(md3.DateFormatter("%b/%Y"))
        ax.tick_params(axis="x", colors="#FFF", rotation=30, labelsize=7)
        ax.tick_params(axis="y", colors="#FFF")
        for spine in ax.spines.values(): spine.set_color("#333")
        canvas = FigureCanvasTkAgg(fig, master=frame_pai)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
    except Exception as e:
        tk.Label(frame_pai, text=f"Erro no gráfico: {e}", bg="#161616",
                 fg="#FF5252", font=("Arial",8)).pack()

def _renderizar_tabela_risco(indicadores, frame_pai):
    for w in frame_pai.winfo_children(): w.destroy()
    if not indicadores:
        tk.Label(frame_pai, text="Não foi possível calcular indicadores.",
                 bg="#161616", fg=ACCENT, font=("Arial", 8, "italic"), pady=8).pack()
        return
    CAB_BG = CARD
    cols   = ["Ativo", "Beta", "Sharpe", "Drawdown Máx."]
    widths = [10, 8, 8, 14]
    tbl = tk.Frame(frame_pai, bg=CAB_BG); tbl.pack(fill="x", padx=6)
    for c,(col,w) in enumerate(zip(cols,widths)):
        tk.Label(tbl, text=col, bg=CAB_BG, fg=ACCENT,
                 font=("Arial",8,"bold"), width=w,
                 anchor="center").grid(row=0,column=c,padx=1,pady=3,sticky="ew")
    tk.Frame(tbl, bg="#2a1a2a", height=1).grid(row=1,column=0,columnspan=4,sticky="ew")
    for idx,(ticker,ind) in enumerate(indicadores.items()):
        row_bg = "#161616" if idx%2==0 else "#202020"
        ri     = idx+2
        beta_s = f"{ind['beta']:.2f}"  if ind['beta']    is not None else "N/D"
        shar_s = f"{ind['sharpe']:.2f}" if ind['sharpe'] is not None else "N/D"
        dd_s   = f"{ind['drawdown']:.1f}%" if ind['drawdown'] is not None else "N/D"
        cor_beta  = ACCENT if ind['beta'] is not None and ind['beta']<1 else "#FF5252" if ind['beta'] is not None else "#888"
        cor_sharp = ACCENT if ind['sharpe'] is not None and ind['sharpe']>0 else "#FF5252" if ind['sharpe'] is not None else "#888"
        cor_dd    = ACCENT if ind['drawdown'] is not None and ind['drawdown']>-15 else "#FF5252" if ind['drawdown'] is not None else "#888"
        dados_row = [(nome_exibicao(ticker),TXT),(beta_s,cor_beta),(shar_s,cor_sharp),(dd_s,cor_dd)]
        for c,(val,fg) in enumerate(dados_row):
            tk.Label(tbl,text=val,bg=row_bg,fg=fg,
                     font=("Arial",8),width=widths[c],
                     anchor="center").grid(row=ri,column=c,padx=1,pady=2,sticky="ew")

    # Legenda
    leg = tk.Frame(frame_pai, bg="#161616"); leg.pack(fill="x", padx=8, pady=4)
    tk.Label(leg, text="Beta<1 = menos volátil que o mercado  |  Sharpe>0 = retorno acima do risco  |  Drawdown = maior queda do pico",
             bg="#161616", fg=ACCENT, font=("Arial", 7), anchor="w").pack(fill="x")

# ── 7. Comparativo com Benchmarks ──
def _renderizar_benchmark(dados, ibov, carteira, frame_pai, start, end):
    import pandas as pd, numpy as np
    for w in frame_pai.winfo_children(): w.destroy()
    fig = plt.figure(figsize=(11, 3.0)); fig.patch.set_facecolor(BG)
    ax  = fig.add_axes([0.07, 0.20, 0.88, 0.70]); ax.set_facecolor("#161616")
    tickers = list(carteira.keys())
    # Carteira ponderada por custo
    try:
        total_custo = sum(float(p["qtd"])*float(p["preco_medio"]) for p in carteira.values())
        cart_serie  = None
        for ticker, pos in carteira.items():
            serie = (dados["Close"] if len(tickers)==1 else dados["Close"][ticker]).dropna()
            peso  = (float(pos["qtd"])*float(pos["preco_medio"]))/total_custo if total_custo>0 else 1/len(tickers)
            base  = (serie/serie.iloc[0])*100*peso
            cart_serie = base if cart_serie is None else cart_serie.add(base, fill_value=0)
        if cart_serie is not None:
            ax.plot(cart_serie.index, cart_serie.values, color=ACCENT, linewidth=2.5, label="Minha Carteira")
    except: pass
    # Ibovespa
    if not ibov.empty:
        s = ibov["Close"].dropna(); s = (s/s.iloc[0])*100
        ax.plot(s.index, s.values, color="#aaaaaa", linewidth=1.5, linestyle="--", label="IBOV")
    # CDI sintético
    try:
        datas_cdi = pd.date_range(start, end, freq="B")
        td = (1+CDI_ANUAL)**(1/252)-1
        cdi_vals = 100*np.cumprod([1+td]*len(datas_cdi))
        ax.plot(datas_cdi, cdi_vals, color=ACCENT, linewidth=1.2, linestyle=":", label="CDI")
    except: pass
    ax.set_title("Carteira vs Benchmarks (Base 100)", color=TXT, fontsize=10, fontweight="bold")
    ax.axhline(100, color="#333", linewidth=0.7, linestyle="-")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_: f"{x:.0f}"))
    import matplotlib.dates as md2
    ax.xaxis.set_major_locator(md2.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(md2.DateFormatter("%b/%Y"))
    ax.tick_params(axis="x", colors="#FFF", rotation=30, labelsize=7)
    ax.tick_params(axis="y", colors="#FFF")
    for spine in ax.spines.values(): spine.set_color("#333")
    leg = ax.legend(loc="upper left", frameon=False, fontsize=8)
    for t in leg.get_texts(): t.set_color("#FFF")
    canvas = FigureCanvasTkAgg(fig, master=frame_pai)
    canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)

# ── 8. Alertas Automáticos ──
def _gerar_alertas_carteira(rows):
    """Gera lista de alertas baseados na posição atual da carteira."""
    alertas = []
    for r in rows:
        # Queda acentuada
        if r["lucro_pct"] <= -15:
            alertas.append(("🔴", f"{r['nome']} caiu {r['lucro_pct']:.1f}% desde sua compra — avalie sua posição.", "#FF5252"))
        elif r["lucro_pct"] <= -8:
            alertas.append(("🟡", f"{r['nome']} está {r['lucro_pct']:.1f}% abaixo do preço médio.", ACCENT))
        # Alta expressiva
        if r["lucro_pct"] >= 30:
            alertas.append(("🟢", f"{r['nome']} valorizou {r['lucro_pct']:.1f}% — considere realizar parte do lucro.", ACCENT))
        # Comparação com CDI
        try:
            cdi = _cdi_desde_compra(r["data_compra"])
            if cdi and r["lucro_pct"] < cdi:
                diff = cdi - r["lucro_pct"]
                alertas.append(("💛", f"{r['nome']} está {diff:.1f}% abaixo do CDI no mesmo período.", ACCENT))
        except: pass
    # Concentração setorial
    setores = {}
    for r in rows:
        s = SETORES.get(r["ticker"], "Outros")
        setores[s] = setores.get(s,[]) + [r["nome"]]
    for setor, nomes in setores.items():
        if len(nomes) >= 2:
            alertas.append(("⚡", f"Concentração em {setor}: {', '.join(nomes)}. Considere diversificar.", "#FFD600"))
    if not alertas:
        alertas.append(("✅", "Nenhum alerta no momento. Carteira dentro dos parâmetros normais.", ACCENT))
    return alertas

def _montar_alertas(rows, frame_pai):
    for w in frame_pai.winfo_children(): w.destroy()
    if not rows:
        tk.Label(frame_pai, text="Adicione ações à carteira para ver os alertas.",
                 bg="#161616", fg=ACCENT, font=("Arial", 8, "italic"), pady=8).pack()
        return
    alertas = _gerar_alertas_carteira(rows)
    for icone, texto, cor in alertas:
        row = tk.Frame(frame_pai, bg="#161616"); row.pack(fill="x", padx=8, pady=2)
        tk.Label(row, text=icone, bg="#161616", font=("Arial",10), width=2).pack(side="left")
        tk.Label(row, text=texto, bg="#161616", fg=cor,
                 font=("Arial",8), anchor="w", wraplength=900).pack(side="left", fill="x", expand=True)

# ── 9. Score de Diversificação ──
def _calcular_score_diversificacao(carteira):
    """Nota 0–10 baseada em qtd de ativos, setores e concentração."""
    if not carteira: return 0.0, "Carteira vazia."
    n_ativos  = len(carteira)
    setores   = set(SETORES.get(t,"Outros") for t in carteira)
    n_setores = len(setores)
    # Concentração: % do maior ativo pelo custo
    custos = {t: float(p["qtd"])*float(p["preco_medio"]) for t,p in carteira.items()}
    total  = sum(custos.values())
    maior_pct = max(custos.values())/total*100 if total>0 else 100
    # Score
    score_ativos  = min(10, n_ativos * 1.2)
    score_setores = min(10, n_setores * 2.0)
    score_conc    = max(0, 10 - (maior_pct - 20) * 0.2) if maior_pct > 20 else 10
    score = round((score_ativos*0.3 + score_setores*0.4 + score_conc*0.3), 1)
    if score >= 8:   msg = "✅ Carteira bem diversificada!"
    elif score >= 6: msg = "⚠ Diversificação razoável — considere adicionar mais setores."
    elif score >= 4: msg = "🔶 Diversificação baixa — carteira concentrada."
    else:            msg = "🔴 Carteira muito concentrada — alto risco não sistemático."
    return score, msg

def _montar_score_div(carteira, frame_pai):
    for w in frame_pai.winfo_children(): w.destroy()
    score, msg = _calcular_score_diversificacao(carteira)
    cor = ACCENT if score>=8 else ACCENT if score>=5 else "#FF5252"
    # Linha com barra
    row = tk.Frame(frame_pai, bg="#161616"); row.pack(fill="x", padx=10, pady=6)
    tk.Label(row, text="Score de Diversificação:", bg="#161616", fg="#aaaaaa",
             font=("Arial",9,"bold")).pack(side="left")
    BAR_W = 160
    c_bar = tk.Canvas(row, width=BAR_W, height=12, bg="#161616", highlightthickness=0)
    c_bar.pack(side="left", padx=8)
    c_bar.create_rectangle(0,0,BAR_W,12,fill=BTN,outline="")
    c_bar.create_rectangle(0,0,int(score/10*BAR_W),12,fill=cor,outline="")
    tk.Label(row, text=f"{score}/10", bg="#161616", fg=cor,
             font=("Arial",9,"bold")).pack(side="left", padx=4)
    tk.Label(frame_pai, text=msg, bg="#161616", fg=cor,
             font=("Arial",8), anchor="w", padx=10).pack(fill="x")

# ── 10. Resumo Executivo ──
def _gerar_resumo_executivo(rows, carteira):
    """Gera parágrafo descritivo do estado atual da carteira."""
    if not rows: return "Adicione ativos à carteira para ver o resumo executivo."
    total_custo  = sum(r["custo"]      for r in rows)
    total_patrim = sum(r["patrimonio"] for r in rows)
    total_lucro  = sum(r["lucro_rs"]   for r in rows)
    total_pct    = (total_lucro/total_custo*100) if total_custo>0 else 0
    melhor = max(rows, key=lambda r: r["lucro_pct"])
    pior   = min(rows, key=lambda r: r["lucro_pct"])
    score_div, _ = _calcular_score_diversificacao(carteira)
    nivel_div = "bem diversificada" if score_div>=8 else "moderadamente diversificada" if score_div>=5 else "concentrada"
    sinal = "positivo" if total_lucro>=0 else "negativo"
    resumo = (
        f"Sua carteira é composta por {len(rows)} ativo(s), com custo total de "
        f"{_fmt_brl(total_custo)} e patrimônio atual de {_fmt_brl(total_patrim)}. "
        f"O resultado acumulado é {sinal}: {_fmt_brl(total_lucro, forcar_sinal=True)} ({total_pct:+.2f}%). "
        f"O ativo com melhor desempenho é {melhor['nome']} ({melhor['lucro_pct']:+.2f}%) "
        f"e o que mais preocupa é {pior['nome']} ({pior['lucro_pct']:+.2f}%). "
        f"A carteira está {nivel_div} (score {score_div}/10)."
    )
    return resumo

def _montar_resumo_executivo(rows, carteira, frame_pai):
    for w in frame_pai.winfo_children(): w.destroy()
    if not rows:
        tk.Label(frame_pai, text="Adicione ativos à carteira para ver o resumo executivo.",
                 bg="#161616", fg=ACCENT, font=("Arial", 8, "italic"), pady=8).pack()
        return
    texto = _gerar_resumo_executivo(rows, carteira)
    tk.Label(frame_pai, text=texto, bg="#161616", fg=TXT,
             font=("Arial", 9), anchor="w", justify="left",
             wraplength=1100, padx=12, pady=10).pack(fill="x")

def _buscar_precos_carteira(tickers):
    """Retorna dict {ticker: preco_atual} — ignora ativos inválidos/delistados."""
    precos = {}
    for t in tickers:
        t = t.strip()  # remove espaços extras que corrompem o yfinance
        if not t:
            continue
        try:
            hist = yf.Ticker(t).history(period="2d")
            if hist is not None and not hist.empty and "Close" in hist.columns:
                preco = float(hist["Close"].dropna().iloc[-1])
                if preco > 0:
                    precos[t] = preco
        except Exception:
            pass  # ignora 404, delistados, sem dados
    return precos

def _calcular_pl(carteira, precos):
    """Retorna lista de dicts com P&L por ativo. Ignora ativos sem preço."""
    rows = []
    for ticker, pos in carteira.items():
        preco_atual = precos.get(ticker)
        if preco_atual is None or preco_atual <= 0:
            continue  # ativo delistado ou sem dados — ignora silenciosamente
        qtd         = float(pos["qtd"])
        pm          = float(pos["preco_medio"])
        custo       = qtd * pm
        patrimonio  = qtd * preco_atual
        lucro_rs    = patrimonio - custo
        lucro_pct   = (lucro_rs / custo * 100) if custo > 0 else 0
        # Tendência vs preço médio
        diff_pm = ((preco_atual - pm) / pm * 100) if pm > 0 else 0
        if diff_pm > 2:
            tendencia = ("↑ Alta",    "#00C896")
        elif diff_pm < -2:
            tendencia = ("↓ Queda",   "#FF5252")
        else:
            tendencia = ("→ Lateral", ACCENT)
        rows.append({
            "ticker":     ticker,
            "nome":       nome_exibicao(ticker),
            "qtd":        qtd,
            "pm":         pm,
            "preco_atual":preco_atual,
            "custo":      custo,
            "patrimonio": patrimonio,
            "lucro_rs":   lucro_rs,
            "lucro_pct":  lucro_pct,
            "data_compra":pos.get("data_compra", "—"),
            "tendencia":  tendencia,
        })
    return rows

# ── 4. Comparativo com CDI ──
def _cdi_desde_compra(data_compra_str):
    """Retorna quanto o CDI rendeu desde a data de compra até hoje."""
    try:
        d1   = datetime.strptime(data_compra_str, "%d/%m/%Y")
        dias = (datetime.now() - d1).days
        return ((1 + CDI_ANUAL) ** (dias / 365) - 1) * 100
    except Exception:
        return None

# ── UI: funções de ação ──
def _adicionar_posicao():
    """Valida e adiciona posição à carteira."""
    raw    = entry_cart_ticker.get().strip().upper()
    qtd_s  = entry_cart_qtd.get().strip()
    pm_s   = entry_cart_pm.get().strip()
    data_s = entry_cart_data.get().strip()

    if not raw or raw == "EX: PETR4":
        lbl_cart_status.config(text="⚠ Digite o ticker.", fg="#FF5252"); return
    ticker = raw if raw.endswith(".SA") else raw + ".SA"

    try:
        qtd = float(qtd_s.replace(",", "."))
        pm  = float(pm_s.replace(",", "."))
        if qtd <= 0 or pm <= 0: raise ValueError
    except ValueError:
        lbl_cart_status.config(text="⚠ Qtd e preço devem ser números positivos.", fg="#FF5252"); return

    try:
        datetime.strptime(data_s, "%d/%m/%Y")
    except ValueError:
        lbl_cart_status.config(text="⚠ Data inválida. Use DD/MM/AAAA.", fg="#FF5252"); return

    # Se já existe, soma a posição (preço médio ponderado)
    if ticker in _carteira:
        old = _carteira[ticker]
        qtd_total = float(old["qtd"]) + qtd
        pm_novo   = (float(old["qtd"])*float(old["preco_medio"]) + qtd*pm) / qtd_total
        _carteira[ticker] = {"qtd": qtd_total, "preco_medio": round(pm_novo,4),
                              "data_compra": old["data_compra"]}
        msg = f"✔ Posição de {nome_exibicao(ticker)} atualizada!"
    else:
        _carteira[ticker] = {"qtd": qtd, "preco_medio": pm, "data_compra": data_s}
        msg = f"✔ {nome_exibicao(ticker)} adicionado à carteira!"

    _salvar_carteira(_carteira)
    lbl_cart_status.config(text=msg, fg=ACCENT)
    _atualizar_carteira_ui()

def _remover_posicao(ticker):
    if ticker in _carteira:
        del _carteira[ticker]
        _salvar_carteira(_carteira)
        _atualizar_carteira_ui()

def _atualizar_carteira_ui():
    """Busca TODOS os dados em uma thread e renderiza tudo de uma vez."""
    lbl_cart_status.config(text="⏳ Buscando dados...", fg="#aaaaaa")
    btn_atualizar_cart.config(state="disabled", text="Carregando...")

    def _buscar_tudo():
        resultado = {"precos": {}, "ibov": None, "dados_hist": None,
                     "indicadores": {}, "start": None, "end": None, "erro": None}
        try:
            tickers = list(_carteira.keys())
            if not tickers:
                root.after(0, lambda: _aplicar_resultados(resultado))
                return

            # 1. Preços atuais
            resultado["precos"] = _buscar_precos_carteira(tickers)

            # 2. Dados históricos para gráficos e indicadores
            datas = []
            for pos in _carteira.values():
                try: datas.append(datetime.strptime(pos["data_compra"], "%d/%m/%Y"))
                except: pass

            if datas:
                start = min(datas).strftime("%Y-%m-%d")
                end   = datetime.now().strftime("%Y-%m-%d")
                resultado["start"] = start
                resultado["end"]   = end
                try:
                    resultado["dados_hist"] = yf.download(
                        tickers, start=start, end=end,
                        auto_adjust=True, progress=False)
                except: pass
                try:
                    resultado["ibov"] = yf.download(
                        "^BVSP", start=start, end=end,
                        auto_adjust=True, progress=False)
                except: pass
                # 3. Indicadores de risco
                try:
                    ind = {}
                    serie_ibov = resultado["ibov"]["Close"].dropna() if resultado["ibov"] is not None and not resultado["ibov"].empty else None
                    dados_h = resultado["dados_hist"]
                    for ticker in tickers:
                        try:
                            s = (dados_h["Close"] if len(tickers)==1
                                 else dados_h["Close"][ticker]).dropna()
                            ind[ticker] = {
                                "beta":     _calcular_beta(s, serie_ibov) if serie_ibov is not None else None,
                                "sharpe":   _calcular_sharpe(s),
                                "drawdown": _calcular_drawdown_max(s),
                            }
                        except: pass
                    resultado["indicadores"] = ind
                except: pass

        except Exception as e:
            resultado["erro"] = str(e)

        root.after(0, lambda: _aplicar_resultados(resultado))

    threading.Thread(target=_buscar_tudo, daemon=True).start()

def _renderizar_secoes_vazias():
    """Placeholder para as 5 seções avançadas quando não há ativos na carteira."""
    for frame, msg in [
        (frame_risco,     "Adicione ativos para ver indicadores de risco."),
        (frame_benchmark, "Adicione ações para ver a comparação com benchmarks."),
    ]:
        for w in frame.winfo_children(): w.destroy()
        tk.Label(frame, text=msg, bg="#161616", fg=ACCENT,
                 font=("Arial", 8, "italic"), pady=8).pack()
    _montar_alertas([], frame_alertas)
    _montar_score_div({}, frame_score_div)
    _montar_resumo_executivo([], {}, frame_resumo)


def _aplicar_resultados(resultado):
    """Chamada na thread principal com todos os dados prontos."""
    btn_atualizar_cart.config(state="normal", text="↻ Atualizar")

    precos      = resultado["precos"]
    dados_hist  = resultado["dados_hist"]
    ibov        = resultado["ibov"]
    indicadores = resultado["indicadores"]
    start       = resultado.get("start")
    end         = resultado.get("end")

    # Renderiza tabela P&L
    _renderizar_carteira(precos)

    if not _carteira:
        _renderizar_secoes_vazias()
        lbl_cart_status.config(text="", fg="#aaaaaa")
        return

    rows = _calcular_pl(_carteira, precos)

    # Cache para o Assistente da Carteira consultar sem reprocessar/rebaixar dados
    _cache_analitico["rows"]         = rows
    _cache_analitico["indicadores"]  = indicadores
    _cache_analitico["atualizado_em"] = datetime.now()

    # Indicadores de risco (Beta / Sharpe / Drawdown) — reaproveita dados já baixados
    _renderizar_tabela_risco(indicadores, frame_risco)

    # Carteira vs Ibovespa vs CDI — reaproveita dados já baixados, sem novo download
    if dados_hist is not None and not dados_hist.empty and ibov is not None and start and end:
        _renderizar_benchmark(dados_hist, ibov, _carteira, frame_benchmark, start, end)
    else:
        for w in frame_benchmark.winfo_children(): w.destroy()
        tk.Label(frame_benchmark, text="Não foi possível carregar os benchmarks.",
                 bg="#161616", fg=ACCENT, font=("Arial", 8, "italic"), pady=8).pack()

    # Alertas automáticos
    _montar_alertas(rows, frame_alertas)

    # Score de diversificação
    _montar_score_div(_carteira, frame_score_div)

    # Resumo executivo
    _montar_resumo_executivo(rows, _carteira, frame_resumo)

    if not rows:
        lbl_cart_status.config(text="⚠ Nenhum preço encontrado para os ativos cadastrados.", fg=ACCENT)
        return

    # Gráfico evolução
    if dados_hist is not None and not dados_hist.empty:
        _grafico_evolucao_com_dados(dados_hist, _carteira, frame_cart_grafico)

    lbl_cart_status.config(text=f"✔ Carteira atualizada — {len(rows)} ativo(s)", fg=ACCENT)

def _renderizar_carteira(precos):
    """Renderiza tabela P&L + totais + gráfico."""
    # Limpa tabela
    for w in frame_cart_tabela.winfo_children(): w.destroy()

    rows = _calcular_pl(_carteira, precos)

    if not rows:
        for w in frame_cart_tabela.winfo_children(): w.destroy()
        tk.Label(frame_cart_tabela,
                 text="Nenhum ativo adicionado. Use o formulário acima para adicionar ações.",
                 bg="#161616", fg=ACCENT, font=("Arial", 9, "italic"), pady=16).pack()
        lbl_cart_status.config(text="", fg="#aaaaaa")
        return

    # Cabeçalho da tabela
    CAB_BG = CARD
    cols   = ["Ativo","Tend.","Qtd","P.M. (R$)","Atual (R$)","Custo (R$)","Patrim. (R$)","Lucro R$","Lucro %","CDI%","Ação"]
    widths = [7,8,4,8,8,10,10,10,8,7,4]

    tbl = tk.Frame(frame_cart_tabela, bg=CAB_BG)
    tbl.pack(fill="x", padx=6)

    for c,(col,w) in enumerate(zip(cols,widths)):
        tk.Label(tbl, text=col, bg=CAB_BG, fg=ACCENT,
                 font=("Arial",8,"bold"), width=w,
                 anchor="center").grid(row=0,column=c,padx=1,pady=3,sticky="ew")

    tk.Frame(tbl, bg=BTN, height=1).grid(
        row=1, column=0, columnspan=len(cols), sticky="ew")

    total_custo = total_patrim = total_lucro = 0

    for idx, r in enumerate(rows):
        row_bg  = "#161616" if idx%2==0 else "#202020"
        cor_ret = "#00C896" if r["lucro_rs"] >= 0 else "#FF5252"
        cdi_ret = _cdi_desde_compra(r["data_compra"])
        cdi_txt = f"{cdi_ret:.2f}%" if cdi_ret else "—"
        ri      = idx + 2

        tend_txt, tend_cor = r.get("tendencia", ("—", "#aaaaaa"))
        dados_row = [
            (nome_exibicao(r["ticker"]), CORES_ATIVOS[list(_carteira.keys()).index(r["ticker"]) % len(CORES_ATIVOS)]),
            (tend_txt,                   tend_cor),
            (f"{r['qtd']:.0f}",          TXT),
            (_fmt_num_br(r['pm']),           TXT),
            (_fmt_num_br(r['preco_atual']),  TXT),
            (_fmt_num_br(r['custo']),        TXT),
            (_fmt_num_br(r['patrimonio']),   TXT),
            (_fmt_num_br(r['lucro_rs'], forcar_sinal=True), cor_ret),
            (f"{r['lucro_pct']:+.2f}%",  cor_ret),
            (cdi_txt,                    "#aaaaaa"),
        ]
        for c,(val,fg) in enumerate(dados_row):
            tk.Label(tbl, text=val, bg=row_bg, fg=fg,
                     font=("Arial",8), width=widths[c],
                     anchor="center").grid(row=ri,column=c,padx=1,pady=2,sticky="ew")

        # Botão remover (coluna 10 = última)
        tk.Button(tbl, text="✕", bg="#2a0000", fg="#FF5252",
                  font=("Arial",8,"bold"), relief="flat", cursor="hand2", width=2,
                  command=lambda t=r["ticker"]: _remover_posicao(t)
                  ).grid(row=ri, column=10, padx=1, pady=2)

        total_custo   += r["custo"]
        total_patrim  += r["patrimonio"]
        total_lucro   += r["lucro_rs"]

    # Totais
    total_pct = (total_lucro/total_custo*100) if total_custo>0 else 0
    cor_tot   = "#00C896" if total_lucro>=0 else "#FF5252"
    sep_r     = len(rows)+2
    tk.Frame(tbl, bg=BTN, height=1).grid(
        row=sep_r, column=0, columnspan=len(cols), sticky="ew", pady=2)
    tot_row = sep_r+1
    COR_VAZIO = CARD  # mesma cor do fundo = invisível
    resumo = [
        ("TOTAL",ACCENT),("",COR_VAZIO),("",COR_VAZIO),("",COR_VAZIO),("",COR_VAZIO),
        (_fmt_num_br(total_custo),ACCENT),
        (_fmt_num_br(total_patrim),ACCENT),
        (_fmt_num_br(total_lucro, forcar_sinal=True),cor_tot),
        (f"{total_pct:+.2f}%",cor_tot),
        ("",COR_VAZIO),("",COR_VAZIO),
    ]
    for c,(val,fg) in enumerate(resumo):
        tk.Label(tbl, text=val, bg=CARD, fg=fg,
                 font=("Arial",8,"bold"), width=widths[c],
                 anchor="center").grid(row=tot_row,column=c,padx=1,pady=3,sticky="ew")

    # Registra snapshot no histórico SQLite
    try:
        _registrar_patrimonio(
            custo_total = total_custo,
            patrimonio  = total_patrim,
            lucro_rs    = total_lucro,
            lucro_pct   = (total_lucro / total_custo * 100) if total_custo > 0 else 0,
            n_ativos    = len(rows),
        )
    except Exception as e:
        print(f"[SQLite] Erro no registro automático: {e}")
    lbl_cart_status.config(text=f"⏳ Calculando seções avançadas...", fg="#aaaaaa")

# ======================================================
# UI — CARD CARTEIRA PESSOAL (Etapa 5)
# ======================================================
CART_BG  = "#161616"
CART_ACC = ACCENT
CART_BORDER = ACCENT

frame_cart_outer = tk.Frame(frame_conteudo, bg=ACCENT)
frame_cart_outer.pack(fill="x", pady=(10, 0))

frame_cart = tk.Frame(frame_cart_outer, bg=CART_BG)
frame_cart.pack(fill="both", expand=True, padx=2, pady=2)

# Cabeçalho
cab_cart = tk.Frame(frame_cart, bg="#0d0d0d")
cab_cart.pack(fill="x")
tk.Label(cab_cart, text="💼  Carteira Pessoal", bg="#0d0d0d", fg=CART_ACC,
         font=("Arial", 11, "bold"), pady=6).pack(side="left", padx=12)
btn_atualizar_cart = tk.Button(cab_cart, text="↻ Atualizar", bg=BTN, fg=CART_ACC,
          font=("Arial", 8, "bold"), relief="flat", cursor="hand2",
          command=_atualizar_carteira_ui)
btn_atualizar_cart.pack(side="right", padx=10)

# Formulário de adição
frame_cart_form = tk.Frame(frame_cart, bg=CART_BG)
frame_cart_form.pack(fill="x", padx=10, pady=(8,4))

def _mk(parent, texto):
    tk.Label(parent, text=texto, bg=CART_BG, fg="#aaaaaa",
             font=("Arial", 7)).pack(anchor="w")

col_t = tk.Frame(frame_cart_form, bg=CART_BG); col_t.pack(side="left", padx=(0,6))
_mk(col_t, "Ticker")
entry_cart_ticker = tk.Entry(col_t, width=9, bg=BTN, fg="#aaaaaa",
                              insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cart_ticker.insert(0, "ex: PETR4")
entry_cart_ticker.bind("<FocusIn>",  lambda e: limpar_entry_placeholder(entry_cart_ticker, "ex: PETR4"))
entry_cart_ticker.bind("<FocusOut>", lambda e: restaurar_placeholder(entry_cart_ticker, "ex: PETR4"))
entry_cart_ticker.pack()

col_q = tk.Frame(frame_cart_form, bg=CART_BG); col_q.pack(side="left", padx=(0,6))
_mk(col_q, "Quantidade")
entry_cart_qtd = tk.Entry(col_q, width=9, bg=BTN, fg=TXT,
                           insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cart_qtd.insert(0, "100")
entry_cart_qtd.pack()

col_p = tk.Frame(frame_cart_form, bg=CART_BG); col_p.pack(side="left", padx=(0,6))
_mk(col_p, "Preço médio (R$)")
entry_cart_pm = tk.Entry(col_p, width=9, bg=BTN, fg=TXT,
                          insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cart_pm.insert(0, "30.00")
entry_cart_pm.pack()

col_d = tk.Frame(frame_cart_form, bg=CART_BG); col_d.pack(side="left", padx=(0,6))
_mk(col_d, "Data compra")
entry_cart_data = tk.Entry(col_d, width=11, bg=BTN, fg=TXT,
                            insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cart_data.insert(0, "01/01/2025")
entry_cart_data.pack()

col_b = tk.Frame(frame_cart_form, bg=CART_BG); col_b.pack(side="left", padx=(0,6))
_mk(col_b, " ")
tk.Button(col_b, text="＋ Adicionar", bg=CART_ACC, fg="#000000",
          font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
          command=_adicionar_posicao).pack()

lbl_cart_status = tk.Label(frame_cart, text="", bg=CART_BG, fg=ACCENT,
                             font=("Arial", 8), pady=2)
lbl_cart_status.pack()

# Tabela P&L
frame_cart_tabela = tk.Frame(frame_cart, bg=CART_BG)
frame_cart_tabela.pack(fill="x", padx=4, pady=(0,4))


# -- Separador visual entre ações e CDBs --
tk.Frame(frame_cart, bg=BTN, height=2).pack(fill="x", padx=10, pady=(8,0))

# Cabeçalho CDB
cab_cdb_cart = tk.Frame(frame_cart, bg="#0d0d0d")
cab_cdb_cart.pack(fill="x")
tk.Label(cab_cdb_cart, text="🏦  CDBs na Carteira", bg="#0d0d0d", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=5).pack(side="left", padx=12)

# Formulário CDB
frame_cdb_cart_form = tk.Frame(frame_cart, bg=CART_BG)
frame_cdb_cart_form.pack(fill="x", padx=10, pady=(6, 4))

def _mk_cdb(parent, texto):
    tk.Label(parent, text=texto, bg=CART_BG, fg="#aaaaaa",
             font=("Arial", 7)).pack(anchor="w")

cdb_c1 = tk.Frame(frame_cdb_cart_form, bg=CART_BG); cdb_c1.pack(side="left", padx=(0,6))
_mk_cdb(cdb_c1, "Nome / Banco")
entry_cdb_nome = tk.Entry(cdb_c1, width=14, bg=BTN, fg="#aaaaaa",
                           insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cdb_nome.insert(0, "ex: Nubank CDB")
entry_cdb_nome.bind("<FocusIn>",  lambda e: limpar_entry_placeholder(entry_cdb_nome, "ex: Nubank CDB"))
entry_cdb_nome.bind("<FocusOut>", lambda e: restaurar_placeholder(entry_cdb_nome, "ex: Nubank CDB"))
entry_cdb_nome.pack()

cdb_c2 = tk.Frame(frame_cdb_cart_form, bg=CART_BG); cdb_c2.pack(side="left", padx=(0,6))
_mk_cdb(cdb_c2, "Valor aplicado (R$)")
entry_cdb_valor = tk.Entry(cdb_c2, width=11, bg=BTN, fg=TXT,
                            insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cdb_valor.insert(0, "5000")
entry_cdb_valor.pack()

cdb_c3 = tk.Frame(frame_cdb_cart_form, bg=CART_BG); cdb_c3.pack(side="left", padx=(0,6))
_mk_cdb(cdb_c3, "% do CDI")
entry_cdb_pct = tk.Entry(cdb_c3, width=8, bg=BTN, fg=TXT,
                          insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cdb_pct.insert(0, "110")
entry_cdb_pct.pack()

cdb_c4 = tk.Frame(frame_cdb_cart_form, bg=CART_BG); cdb_c4.pack(side="left", padx=(0,6))
_mk_cdb(cdb_c4, "Data aplicação")
entry_cdb_data = tk.Entry(cdb_c4, width=11, bg=BTN, fg=TXT,
                           insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cdb_data.insert(0, "01/01/2025")
entry_cdb_data.pack()

cdb_c5 = tk.Frame(frame_cdb_cart_form, bg=CART_BG); cdb_c5.pack(side="left", padx=(0,6))
_mk_cdb(cdb_c5, "Vencimento (opc.)")
entry_cdb_venc = tk.Entry(cdb_c5, width=11, bg=BTN, fg="#aaaaaa",
                           insertbackground=TXT, font=("Arial", 9), justify="center")
entry_cdb_venc.insert(0, "DD/MM/AAAA")
entry_cdb_venc.bind("<FocusIn>",  lambda e: limpar_entry_placeholder(entry_cdb_venc, "DD/MM/AAAA"))
entry_cdb_venc.bind("<FocusOut>", lambda e: restaurar_placeholder(entry_cdb_venc, "DD/MM/AAAA"))
entry_cdb_venc.pack()

cdb_c6 = tk.Frame(frame_cdb_cart_form, bg=CART_BG); cdb_c6.pack(side="left", padx=(0,6))
_mk_cdb(cdb_c6, " ")
tk.Button(cdb_c6, text="＋ Adicionar CDB", bg=ACCENT, fg="#161616",
          font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
          command=_adicionar_cdb).pack()

lbl_cdb_status = tk.Label(frame_cart, text="", bg=CART_BG, fg=ACCENT,
                            font=("Arial", 8), pady=2)
lbl_cdb_status.pack()

# Tabela CDBs
frame_cdb_cart_tabela = tk.Frame(frame_cart, bg=CART_BG)
frame_cdb_cart_tabela.pack(fill="x", padx=4, pady=(0, 10))

# Gráfico evolução
frame_cart_grafico = tk.Frame(frame_cart, bg=CART_BG)
frame_cart_grafico.pack(fill="x", padx=4, pady=(0,4))

# -- Separador visual entre carteira básica e seções avançadas --
tk.Frame(frame_cart, bg=BTN, height=2).pack(fill="x", padx=10, pady=(8,0))

# ── Indicadores de Risco Avançados (Beta / Sharpe / Drawdown) ──
cab_risco = tk.Frame(frame_cart, bg="#0d0d0d")
cab_risco.pack(fill="x")
tk.Label(cab_risco, text="📐  Indicadores de Risco", bg="#0d0d0d", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=5).pack(side="left", padx=12)
frame_risco = tk.Frame(frame_cart, bg=CART_BG)
frame_risco.pack(fill="x", padx=4, pady=(4, 4))

# ── Comparativo com Benchmarks (Ibovespa / CDI) ──
cab_benchmark = tk.Frame(frame_cart, bg="#0d0d0d")
cab_benchmark.pack(fill="x")
tk.Label(cab_benchmark, text="📈  Carteira vs Benchmarks", bg="#0d0d0d", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=5).pack(side="left", padx=12)
frame_benchmark = tk.Frame(frame_cart, bg=CART_BG)
frame_benchmark.pack(fill="x", padx=4, pady=(4, 4))

# ── Alertas Automáticos ──
cab_alertas = tk.Frame(frame_cart, bg="#0d0d0d")
cab_alertas.pack(fill="x")
tk.Label(cab_alertas, text="🔔  Alertas", bg="#0d0d0d", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=5).pack(side="left", padx=12)
frame_alertas = tk.Frame(frame_cart, bg=CART_BG)
frame_alertas.pack(fill="x", padx=4, pady=(4, 4))

# ── Score de Diversificação ──
cab_score_div = tk.Frame(frame_cart, bg="#0d0d0d")
cab_score_div.pack(fill="x")
tk.Label(cab_score_div, text="🧭  Diversificação", bg="#0d0d0d", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=5).pack(side="left", padx=12)
frame_score_div = tk.Frame(frame_cart, bg=CART_BG)
frame_score_div.pack(fill="x", padx=4, pady=(4, 4))

# ── Resumo Executivo ──
cab_resumo = tk.Frame(frame_cart, bg="#0d0d0d")
cab_resumo.pack(fill="x")
tk.Label(cab_resumo, text="📝  Resumo Executivo", bg="#0d0d0d", fg=ACCENT,
         font=("Arial", 10, "bold"), pady=5).pack(side="left", padx=12)
frame_resumo = tk.Frame(frame_cart, bg=CART_BG)
frame_resumo.pack(fill="x", padx=4, pady=(4, 10))


# ======================================================
# ASSISTENTE DA CARTEIRA — motor de regras (sem custo, 100% local)
# ======================================================
# Responde perguntas comuns reaproveitando os cálculos já feitos pela carteira
# (P&L, alertas, score de diversificação, resumo executivo, indicadores de risco).
# Não usa nenhuma API paga — roda inteiramente offline.
#
# Gancho para o futuro: _ollama_disponivel() detecta se há um LLM local rodando
# (via Ollama, http://localhost:11434). Hoje ela só é usada para informar o status
# na resposta de fallback; se um dia for implementado o encaminhamento de perguntas
# livres para o modelo local, o ponto de entrada já está pronto aqui.

def _ollama_disponivel():
    """
    Verifica rapidamente se há um servidor Ollama local rodando.
    Não lança exceção nem trava a UI — apenas informa true/false.
    Hoje isso não é usado para gerar respostas (só motor de regras está ativo),
    fica pronto para quando o encaminhamento a um LLM local for implementado.
    """
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=0.3)
        return True
    except Exception:
        return False

# Palavras-chave por intenção — a primeira que bater "ganha"
_INTENCOES = [
    ("resumo",        ["resumo", "visao geral", "situacao", "analise minha", "analise geral", "como esta minha carteira"]),
    ("risco",         ["maior risco", "mais arriscado", "mais volatil", "risco da carteira", "qual o risco"]),
    ("cdi",           ["cdi", "renda fixa", "batendo", "bater o"]),
    ("diversificacao",["diversific", "concentra"]),
    ("vender",        ["vender", "reduzir posicao"]),
    ("alertas",       ["alerta", "atencao", "cuidado"]),
    ("cdb",           ["cdb"]),
    ("indicadores",   ["beta", "sharpe", "drawdown", "indicador"]),
    ("score",         ["score", "nota"]),
]

def _detectar_intencao(pergunta_normalizada):
    for intencao, palavras in _INTENCOES:
        if any(p in pergunta_normalizada for p in palavras):
            return intencao
    return None

def _resposta_sem_dados():
    return ("⚠ Ainda não tenho dados suficientes da sua carteira. Clique em "
            "\"↻ Atualizar\" no card Carteira Pessoal e tente novamente.")

def _responder_resumo():
    rows = _cache_analitico["rows"]
    if not rows:
        return _resposta_sem_dados()
    return _gerar_resumo_executivo(rows, _carteira)

def _responder_risco():
    rows = _cache_analitico["rows"]
    if not rows:
        return _resposta_sem_dados()
    # Usa volatilidade percentual do lucro como proxy simples de risco por ativo,
    # complementado pelo Beta/Drawdown já calculados quando disponíveis.
    indicadores = _cache_analitico["indicadores"]
    pior_dd = None
    for ticker, ind in indicadores.items():
        dd = ind.get("drawdown")
        if dd is not None and (pior_dd is None or dd < pior_dd[1]):
            pior_dd = (ticker, dd)
    if pior_dd:
        nome = nome_exibicao(pior_dd[0])
        return (f"📉 {nome} é o ativo com a queda mais acentuada em relação ao topo "
                f"histórico (drawdown de {pior_dd[1]:.1f}%) — é o ponto de maior risco "
                f"da sua carteira no momento.")
    # Fallback: maior variação negativa desde a compra
    pior = min(rows, key=lambda r: r["lucro_pct"])
    return (f"📉 {pior['nome']} é o ativo com pior desempenho desde a compra "
            f"({pior['lucro_pct']:+.2f}%) — vale reavaliar essa posição.")

def _responder_cdi():
    rows = _cache_analitico["rows"]
    if not rows:
        return _resposta_sem_dados()
    total_custo = sum(r["custo"] for r in rows)
    total_lucro = sum(r["lucro_rs"] for r in rows)
    total_pct   = (total_lucro / total_custo * 100) if total_custo > 0 else 0
    cdis = [_cdi_desde_compra(r["data_compra"]) for r in rows if _cdi_desde_compra(r["data_compra"]) is not None]
    cdi_medio = sum(cdis) / len(cdis) if cdis else None
    if cdi_medio is None:
        return f"Sua carteira rendeu {total_pct:+.2f}% até agora, mas não consegui calcular o CDI do período para comparar."
    diff = total_pct - cdi_medio
    if diff >= 0:
        return (f"✅ Sim! Sua carteira rendeu {total_pct:+.2f}% contra {cdi_medio:+.2f}% "
                f"do CDI no mesmo período médio — está {diff:.2f} pontos percentuais acima.")
    return (f"🔻 Não — sua carteira rendeu {total_pct:+.2f}% contra {cdi_medio:+.2f}% "
            f"do CDI no mesmo período médio — está {abs(diff):.2f} pontos percentuais abaixo.")

def _responder_diversificacao():
    if not _carteira:
        return _resposta_sem_dados()
    score, msg = _calcular_score_diversificacao(_carteira)
    return f"{msg} (nota {score}/10)"

def _responder_vender():
    rows = _cache_analitico["rows"]
    if not rows:
        return _resposta_sem_dados()
    candidatos = [r for r in rows if r["lucro_pct"] <= -8]
    if candidatos:
        pior = min(candidatos, key=lambda r: r["lucro_pct"])
        return (f"🔴 {pior['nome']} está {pior['lucro_pct']:+.2f}% desde a compra — é o "
                f"principal candidato a reavaliação. Isso não é uma recomendação de "
                f"investimento, só um apontamento baseado na posição atual.")
    return ("Nenhum ativo está em queda acentuada (-8% ou mais) no momento — não "
            "identifiquei um candidato claro à venda pelos critérios que uso.")

def _responder_alertas():
    rows = _cache_analitico["rows"]
    if not rows:
        return _resposta_sem_dados()
    alertas = _gerar_alertas_carteira(rows)
    linhas = [f"{icone} {texto}" for icone, texto, _cor in alertas]
    return "\n".join(linhas)

def _responder_cdb():
    if not _cdbs:
        return "Você ainda não tem CDBs cadastrados na carteira."
    total_aplicado = total_rend = 0.0
    for c in _cdbs:
        rend, total, _dias = _calcular_rendimento_cdb(c["valor"], c["pct_cdi"], c["data"])
        total_aplicado += c["valor"]
        total_rend     += rend
    rent_pct = (total_rend / total_aplicado * 100) if total_aplicado > 0 else 0
    return (f"🏦 Você tem {len(_cdbs)} CDB(s) cadastrado(s), totalizando "
            f"{_fmt_brl(total_aplicado)} aplicados, com rendimento acumulado de "
            f"{_fmt_brl(total_rend, forcar_sinal=True)} ({rent_pct:+.2f}%).")

def _responder_indicadores():
    indicadores = _cache_analitico["indicadores"]
    if not indicadores:
        return _resposta_sem_dados()
    linhas = []
    for ticker, ind in indicadores.items():
        beta = f"{ind['beta']:.2f}" if ind.get("beta") is not None else "N/D"
        sharpe = f"{ind['sharpe']:.2f}" if ind.get("sharpe") is not None else "N/D"
        dd = f"{ind['drawdown']:.1f}%" if ind.get("drawdown") is not None else "N/D"
        linhas.append(f"• {nome_exibicao(ticker)} — Beta {beta} | Sharpe {sharpe} | Drawdown {dd}")
    return "📐 Indicadores de risco por ativo:\n" + "\n".join(linhas)

def _responder_score():
    return _responder_diversificacao()

_RESPOSTAS_POR_INTENCAO = {
    "resumo":         _responder_resumo,
    "risco":          _responder_risco,
    "cdi":            _responder_cdi,
    "diversificacao": _responder_diversificacao,
    "vender":         _responder_vender,
    "alertas":        _responder_alertas,
    "cdb":            _responder_cdb,
    "indicadores":    _responder_indicadores,
    "score":          _responder_score,
}

def _responder_pergunta_carteira(pergunta):
    """
    Ponto de entrada do Assistente da Carteira. Roda 100% localmente, sem custo.
    Casamento por palavras-chave sobre os dados já calculados da carteira.
    """
    pergunta_norm = _normalizar_texto(pergunta)
    intencao = _detectar_intencao(pergunta_norm)
    if intencao is None:
        status_ollama = "🔌 Nenhum modelo de IA local detectado." if not _ollama_disponivel() else "🔌 Ollama detectado, mas ainda não configurado para responder perguntas livres."
        return (
            "🤔 Não reconheci essa pergunta no meu roteiro atual. Posso responder sobre: "
            "resumo da carteira, maior risco, se está batendo o CDI, diversificação, "
            "qual ativo considerar vender, alertas, CDBs e indicadores (Beta/Sharpe/Drawdown).\n\n"
            f"{status_ollama}"
        )
    return _RESPOSTAS_POR_INTENCAO[intencao]()


# ==============================
# INICIALIZAR CHECKBOXES PADRÃO — a partir dos "populares" do catálogo
# ==============================
for _ativo_pop in CATALOGO_ATIVOS:
    if not _ativo_pop["popular"]:
        continue
    ticker = _ativo_pop["ticker"] + ".SA"
    var = tk.BooleanVar(value=True)
    ativos_vars[ticker] = var
    ativos_ordem.append(ticker)
    _criar_checkbox(ticker, var)

# Atualiza a lista de resultados da busca (os populares recém-marcados somem da lista)
_renderizar_resultados_busca("")

# Mostra mensagem inicial no card de insights
_montar_insights([], frame_insights)

# Se já tem ações salvas, carrega tudo
try:
    if _carteira:
        _atualizar_carteira_ui()
    else:
        _renderizar_carteira({})
        _renderizar_secoes_vazias()
except Exception:
    pass

# Inicializa CDBs
try:
    _renderizar_cdbs()
except Exception:
    pass


# ======================================================
# UI — ASSISTENTE DA CARTEIRA (motor de regras, sem custo)
# ======================================================
ASSIST_BG    = BG
ASSIST_BORDA = ACCENT

frame_assist_outer = tk.Frame(frame_conteudo, bg=ASSIST_BORDA)
frame_assist_outer.pack(fill="x", pady=(10, 0))

frame_assist = tk.Frame(frame_assist_outer, bg=ASSIST_BG)
frame_assist.pack(fill="both", expand=True, padx=2, pady=2)

# Cabeçalho
cab_assist = tk.Frame(frame_assist, bg="#0d0d0d")
cab_assist.pack(fill="x")
tk.Label(cab_assist, text="🧭  Assistente da Carteira", bg="#0d0d0d", fg=ASSIST_BORDA,
         font=("Arial", 11, "bold"), pady=6).pack(side="left", padx=12)
tk.Label(cab_assist, text="100% local · sem custo · sem enviar dados para fora",
         bg="#0d0d0d", fg="#555555", font=("Arial", 8)).pack(side="left", padx=4)

# Campo de pergunta
frame_assist_input = tk.Frame(frame_assist, bg=ASSIST_BG)
frame_assist_input.pack(fill="x", padx=10, pady=(8, 4))

tk.Label(frame_assist_input, text="Sua pergunta:", bg=ASSIST_BG, fg="#aaaaaa",
         font=("Arial", 8)).pack(anchor="w")

frame_assist_row = tk.Frame(frame_assist_input, bg=ASSIST_BG)
frame_assist_row.pack(fill="x")

entry_assist = tk.Entry(frame_assist_row, bg=CARD, fg=TXT,
                    insertbackground=TXT, font=("Arial", 10),
                    relief="flat")
entry_assist.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
entry_assist.insert(0, "Ex: Estou batendo o CDI?")
entry_assist.bind("<FocusIn>",  lambda e: limpar_entry_placeholder(entry_assist, "Ex: Estou batendo o CDI?"))
entry_assist.bind("<FocusOut>", lambda e: restaurar_placeholder(entry_assist, "Ex: Estou batendo o CDI?"))
entry_assist.bind("<Return>", lambda e: _enviar_pergunta_assistente())

btn_assist = tk.Button(frame_assist_row, text="✦ Perguntar", bg=ASSIST_BORDA, fg=TXT,
                   font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
                   command=lambda: _enviar_pergunta_assistente())
btn_assist.pack(side="left")

# Sugestões rápidas
frame_assist_sugestoes = tk.Frame(frame_assist, bg=ASSIST_BG)
frame_assist_sugestoes.pack(fill="x", padx=10, pady=(0, 6))
tk.Label(frame_assist_sugestoes, text="Sugestões:", bg=ASSIST_BG, fg="#555555",
         font=("Arial", 7)).pack(side="left", padx=(0, 6))

_sugestoes_assist = [
    "Resumo da carteira",
    "Qual meu maior risco?",
    "Estou batendo o CDI?",
    "Devo diversificar?",
    "Qual ativo vender?",
    "Meus alertas",
]
for s in _sugestoes_assist:
    tk.Button(frame_assist_sugestoes, text=s, bg=BTN, fg="#aaaaaa",
              font=("Arial", 7), relief="flat", cursor="hand2",
              command=lambda txt=s: _sugestao_assistente(txt)).pack(side="left", padx=2)

# Área de resposta
frame_assist_resp = tk.Frame(frame_assist, bg=ASSIST_BG)
frame_assist_resp.pack(fill="x", padx=10, pady=(0, 10))

txt_assist = tk.Text(frame_assist_resp, bg=CARD, fg=TXT,
                 font=("Arial", 9), relief="flat", wrap="word",
                 height=6, state="disabled", padx=10, pady=8)
txt_assist.pack(fill="x")

scroll_assist = tk.Scrollbar(frame_assist_resp, command=txt_assist.yview, bg=BTN)
txt_assist.config(yscrollcommand=scroll_assist.set)

# Mensagem inicial
def _exibir_resposta_assistente(texto):
    txt_assist.config(state="normal")
    txt_assist.delete("1.0", "end")
    txt_assist.insert("end", texto)
    txt_assist.config(state="disabled")
    btn_assist.config(state="normal", text="✦ Perguntar")

def _sugestao_assistente(texto):
    entry_assist.delete(0, "end")
    entry_assist.insert(0, texto)
    entry_assist.config(fg=TXT)
    _enviar_pergunta_assistente()

def _enviar_pergunta_assistente():
    pergunta = entry_assist.get().strip()
    if not pergunta or pergunta == "Ex: Estou batendo o CDI?":
        return
    btn_assist.config(state="disabled", text="⏳ Consultando...")
    def _rodar():
        resposta = _responder_pergunta_carteira(pergunta)
        root.after(0, lambda: _exibir_resposta_assistente(resposta))
    threading.Thread(target=_rodar, daemon=True).start()

_exibir_resposta_assistente(
    "👋 Pergunte algo sobre sua carteira, ou use uma das sugestões acima.\n\n"
    "Esse assistente roda 100% localmente, sem custo e sem enviar seus dados "
    "para nenhum serviço externo."
)

root.mainloop()