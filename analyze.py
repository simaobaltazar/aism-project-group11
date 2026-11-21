"""
analyze.py
Lê os resultados em results/decision_*.json e calcula:
  - a concordância dos veredictos (experiências A e B)
  - a semelhança das "afirmações sem resposta" na experiência A (índice de Jaccard)
Gera uma tabela (results/summary.csv) e um gráfico (results/agreement_chart.png).

Uso:
    python analyze.py
"""

import csv
import glob
import json
from collections import Counter
from itertools import combinations

import matplotlib.pyplot as plt


def agreement_rate(verdicts):
    """Fração de veredictos iguais ao mais frequente.
    Ex.: [FOR, FOR, FOR, AGAINST, FOR] -> 4/5 = 0.8"""
    most_common_count = Counter(verdicts).most_common(1)[0][1]
    return most_common_count / len(verdicts)


def jaccard(set_a, set_b):
    """Semelhança entre dois conjuntos: |interseção| / |união|. Vai de 0 a 1."""
    if not set_a and not set_b:
        return 1.0
    return len(set_a & set_b) / len(set_a | set_b)


def mean_pairwise_jaccard(list_of_id_lists):
    """Média do Jaccard entre todos os pares de julgamentos."""
    pairs = list(combinations(list_of_id_lists, 2))
    scores = [jaccard(set(a), set(b)) for a, b in pairs]
    return sum(scores) / len(scores)


rows = []
for path in sorted(glob.glob("results/decision_*.json")):
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    # Experiência A: o mesmo debate julgado várias vezes
    judgements_a = data["experiment_a"]["judgements"]
    verdicts_a = [j["verdict"] for j in judgements_a]
    ids_a = [j["unanswered_ids"] for j in judgements_a]

    # Experiência B: debates diferentes sobre a mesma decisão
    verdicts_b = [run["judgement"]["verdict"] for run in data["experiment_b"]]

    rows.append({
        "decision_id": data["decision"]["id"],
        "title": data["decision"]["title"],
        "verdicts_A": " ".join(verdicts_a),
        "agreement_A": round(agreement_rate(verdicts_a), 2),
        "unanswered_jaccard_A": round(mean_pairwise_jaccard(ids_a), 2),
        "verdicts_B": " ".join(verdicts_b),
        "agreement_B": round(agreement_rate(verdicts_b), 2),
    })

if not rows:
    print("No results found. Run experiments.py first.")
    raise SystemExit

# Tabela: imprimir no ecrã e guardar em CSV
with open("results/summary.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

for row in rows:
    print(row)

# Gráfico: concordância A vs B para cada decisão
labels = [row["title"] for row in rows]
positions = range(len(rows))
width = 0.35

plt.figure(figsize=(9, 5))
plt.bar([p - width / 2 for p in positions], [r["agreement_A"] for r in rows], width,
        label="A: same debate, judge repeated")
plt.bar([p + width / 2 for p in positions], [r["agreement_B"] for r in rows], width,
        label="B: full pipeline repeated")
plt.xticks(list(positions), labels, rotation=15)
plt.ylim(0, 1.05)
plt.ylabel("Verdict agreement (fraction of runs)")
plt.xlabel("Decision")
plt.title("How consistent is the judge?")
plt.legend()
plt.tight_layout()
plt.savefig("results/agreement_chart.png", dpi=150)
print("\nSaved results/summary.csv and results/agreement_chart.png")
