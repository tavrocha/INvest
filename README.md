# 📊 INvest

> Plataforma desktop de análise de ações da B3 com IA consultora multi-LLM, carteira pessoal, histórico de patrimônio e simuladores financeiros.

**Autor:** Vinícius Tavares Rocha  
**Tecnologias:** Python · Tkinter · yFinance · Matplotlib · SQLite3 · Claude · GPT-4o · Gemini

---

## ✨ Funcionalidades

### 📈 Análise de Ações
- Gráfico interativo com **tooltip**, **Médias Móveis (MM20/MM50)** e modo **Base 100**
- Tabela de análise com retorno, volatilidade, variação do dia e classificação de risco
- Exportação de gráficos em **PNG** e **PDF**
- Cotações em tempo real de **BTC, USD, EUR, GBP, JPY** e outras moedas vs BRL
- Atualização automática a cada **5 minutos**

### 💼 Carteira Pessoal
- Registro de ações com quantidade, preço médio e data de compra
- Tabela **P&L** (Profit & Loss) com lucro/prejuízo em R$ e %
- Comparativo automático com o **CDI** do período
- Indicador de tendência (↑ Alta / ↓ Queda / → Lateral)
- Gráfico de evolução do patrimônio com linha de custo
- Indicadores de risco avançados (Beta, Sharpe, Drawdown Máximo)
- Comparativo Carteira vs Ibovespa vs CDI (Base 100)
- Alertas automáticos (quedas/altas acentuadas, concentração setorial, abaixo do CDI)
- Score de Diversificação
- Resumo Executivo automático da carteira

### 🏦 CDBs na Carteira
- Registro de investimentos em CDB com % do CDI
- Campo de vencimento com alertas automáticos (⚠ próximo do vencimento)
- Cálculo de rendimento acumulado em R$ e %

### 🗄️ Histórico de Patrimônio (SQLite3)
- Registro automático diário do patrimônio no banco de dados local
- Evita duplicatas — atualiza o snapshot do dia se já existir
- Histórico consultável dos últimos 90 dias
- Base para gráficos de evolução histórica

### 🧠 Inteligência do Período
- 10 insights automáticos: top performer, menor retorno, maior risco, mais estável, visão geral, tendências, score da carteira, comparativo CDI, concentração setorial e melhor mês

### 🤖 IA Consultora Multi-LLM
Pipeline inteligente com **fallback automático** entre 3 IAs:

```
Claude Sonnet (Anthropic)
        ↓ sem crédito?
GPT-4o-mini (OpenAI)
        ↓ sem crédito?
Gemini 1.5 Flash (Google) — gratuito
```

- **GPT-4o-mini** processa os dados brutos da carteira → JSON estruturado
- **Claude Sonnet** analisa o JSON → resposta qualitativa personalizada
- Sugestões rápidas de perguntas
- Indicadores de status das chaves em tempo real

### 📐 Simuladores Financeiros
- **Simulador de CDB** — calcula valor final e lucro dado valor, % CDI e dias
- **Calculadora de Meta** — calcula tempo necessário ou aporte mensal para atingir uma meta

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.10 ou superior
- pip

### Windows (instalação automática)
```bash
git clone https://github.com/seuusuario/INvest.git
cd INvest
setup.bat
```

### Manual
```bash
git clone https://github.com/seuusuario/INvest.git
cd INvest
pip install -r requirements.txt
cp .env.example .env
# Edite o .env com suas chaves de API
python app_investimentos.py
```

---

## ⚙️ Configuração

Copie `.env.example` para `.env` e preencha com suas chaves:

```env
ANTHROPIC_API_KEY=sk-ant-...   # https://console.anthropic.com
OPENAI_API_KEY=sk-...          # https://platform.openai.com
GOOGLE_API_KEY=AIza...         # https://aistudio.google.com (gratuito)
```

> **As chaves de IA são opcionais.** Todas as funcionalidades de gráfico, carteira, simuladores e cotações funcionam sem elas. A IA consultora fica disponível conforme as chaves configuradas.

---

## 📁 Estrutura do Projeto

```
INvest/
├── app_investimentos.py    # Aplicação principal
├── requirements.txt        # Dependências Python
├── setup.bat               # Instalador Windows
├── rodar.bat                # Atalho para iniciar a aplicação
├── .env.example             # Modelo de configuração
├── .env                      # Suas chaves (não commitar!)
├── .gitignore                # Ignora .env e dados locais
├── carteira.json             # Carteira salva localmente (auto-gerado)
├── carteira_cdbs.json        # CDBs salvos localmente (auto-gerado)
└── historico.db               # Banco SQLite com histórico (auto-gerado)
```

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| `Python 3.10+` | Linguagem principal |
| `Tkinter` | Interface gráfica desktop |
| `yFinance` | Dados de ações e cotações |
| `Matplotlib` | Gráficos interativos |
| `SQLite3` | Histórico de patrimônio |
| `python-dotenv` | Gerenciamento de variáveis de ambiente |
| `Anthropic Claude` | IA consultora — análise qualitativa |
| `OpenAI GPT-4o-mini` | IA consultora — processamento de dados |
| `Google Gemini` | IA consultora — fallback gratuito |

---

## 📌 Observações

- Os dados de ações são obtidos via **Yahoo Finance** (yFinance) — dados podem ter atraso de 15 minutos
- O arquivo `.env` **nunca deve ser commitado** no GitHub
- O banco `historico.db` e os JSONs são criados automaticamente na primeira execução
- Testado em **Windows 10/11** com Python 3.11 e 3.13

---

## 📄 Licença

MIT License — sinta-se livre para usar, modificar e distribuir.