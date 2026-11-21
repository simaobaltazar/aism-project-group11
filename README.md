# Engineered Disagreement: Proponent vs Opponent + Judge

A multi-agent system where a user describes a decision they are considering. A **Proponent** agent argues for it, an **Opponent** agent argues against it (and is forbidden to concede) over three rounds, and a **Judge** agent reads the full transcript and reports the strongest points on each side, the claims that were never answered, and what information would settle the question. We then test whether the Judge is consistent when run several times.

## Installation

Requirements: Python 3.10 or newer and a free Google Gemini API key.

```bash
git clone <repository-url>
cd aism-project-groupXX
pip install -r requirements.txt
```

1. Create a free API key at https://aistudio.google.com
2. Copy `.env.example` to `.env` and paste your key into `GEMINI_API_KEY`.
3. In `.env`, set `GEMINI_MODEL` to a model ID listed in Google AI Studio (for example a Flash model).

The `.env` file is listed in `.gitignore` and is never uploaded.

## How to run

Run a single debate on any decision:

```bash
python debate.py "Should I quit my job to start a master's degree?"
```

Run the experiments for one decision from `data/decisions.json` (one at a time, to stay within the free-tier daily limits):

```bash
python experiments.py 1
python experiments.py 2
python experiments.py 3
python experiments.py 4
```

Analyse all results:

```bash
python analyze.py
```

## Expected output

- `debate.py` prints the debate transcript and the Judge's judgement, and saves them to `results/single_run_<timestamp>.json`.
- `experiments.py` saves `results/decision_<id>.json` with experiments A (one debate judged 5 times), B (full pipeline 3 times) and C (single-assistant baseline).
- `analyze.py` prints a summary table and saves `results/summary.csv` and `results/agreement_chart.png`.

## Repository structure

```
├── debate.py          # agents, debate loop and judge
├── prompts.py         # system prompts of the three agents and the baseline
├── experiments.py     # experiments A, B and C for one decision
├── analyze.py         # verdict agreement, Jaccard similarity, chart
├── data/
│   └── decisions.json # the decisions used as test cases
├── results/           # generated transcripts, judgements, table and chart
├── requirements.txt
├── .env.example       # template for the API key
└── README.md
```

## Group members

- Name 1
- Name 2
