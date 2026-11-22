# Advogado do Diabo

Projeto do grupo 11 para a unidade curricular de Agentes Inteligentes e Sistemas Multiagentes.

O utilizador descreve uma decisão que está a ponderar e três agentes discutem-na. O Proponente argumenta a favor e o Oponente argumenta contra, durante três rondas. O Oponente não pode ceder. No fim, o Juiz lê o debate e diz que afirmações ficaram sem resposta, além de dar uma sentença.

Corremos o Juiz várias vezes sobre os mesmos casos para ver se chega sempre à mesma conclusão.

## Instalação

É preciso Python 3.10 ou mais recente e uma chave da API do Google Gemini (o plano gratuito chega).

```bash
git clone https://github.com/simaobaltazar/aism-project-group11.git
cd aism-project-group11
pip install -r requirements.txt
```

1. Criar uma chave em https://aistudio.google.com
2. Copiar o ficheiro `.env.example` para `.env` e pôr a chave em `GEMINI_API_KEY`.
3. Em `GEMINI_MODEL`, indicar o modelo a usar. Nas nossas experiências usámos `gemini-3.1-flash-lite`.

O `.env` está no `.gitignore`, por isso a chave não vai para o GitHub.

No Windows, se `python` não funcionar, usar `py` (por exemplo, `py debate.py`).

## Como executar

Um debate sobre uma decisão à escolha:

```bash
python debate.py "Devo comprar um carro?"
```

As experiências, uma decisão de cada vez por causa dos limites diários do plano gratuito:

```bash
python experiments.py 1
python experiments.py 2
python experiments.py 3
python experiments.py 4
```

A análise dos resultados:

```bash
python analyze.py
```

Um debate já guardado, mostrado no terminal:

```bash
python show_debate.py 1
```

Os dois últimos comandos não fazem chamadas à API.

## O que cada comando produz

- `debate.py` mostra o debate e o julgamento e guarda-os em `results/single_run_<data_hora>.json`.
- `experiments.py` cria `results/decision_<id>.json`. A experiência A julga o mesmo debate 5 vezes, a B repete o debate e o julgamento 3 vezes e a C pergunta a um único assistente, sem debate.
- `analyze.py` mostra a tabela-resumo e cria `results/summary.csv` e `results/agreement_chart.png`.
- `show_debate.py` mostra a decisão, as duas primeiras rondas e a sentença do Juiz.

## Estrutura

```
├── debate.py          # agentes, debate e Juiz
├── prompts.py         # instruções de cada agente e do baseline
├── experiments.py     # experiências A, B e C
├── analyze.py         # concordância, Jaccard e gráfico
├── show_debate.py     # mostra um debate guardado
├── list_models.py     # lista os modelos disponíveis para a chave
├── data/
│   └── decisions.json # as 4 decisões de teste
├── results/           # debates, julgamentos, tabela e gráfico
├── requirements.txt
├── .env.example       # exemplo do ficheiro com a chave
└── README.md
```

## Grupo

- Miguel Duarte, n.º 240000645
- Simão Baltazar, n.º 240001316
- Tomás António, n.º 240001360
