"""
experiments.py
Corre as experiências para UMA decisão do ficheiro data/decisions.json:

  A) Mesmo debate, Juiz repetido várias vezes  -> mede a variância só do Juiz
  B) Pipeline completo repetido várias vezes   -> mede a variância total (debate + Juiz)
  C) Baseline: um único assistente "prestável" -> para comparar com o debate

Uso:
    python experiments.py 1      (corre a decisão com id 1)

Corre-se uma decisão de cada vez para não ultrapassar o limite diário do plano gratuito.
"""

import json
import sys

import prompts
from debate import call_llm, judge, run_debate, save_json

JUDGE_REPEATS = 5      # experiência A: quantas vezes o Juiz avalia o MESMO debate
PIPELINE_REPEATS = 3   # experiência B: quantas vezes repetimos tudo do início


def load_decision(decision_id):
    """Lê a decisão com o id pedido a partir do ficheiro de dados."""
    with open("data/decisions.json", encoding="utf-8") as file:
        decisions = json.load(file)
    for item in decisions:
        if item["id"] == decision_id:
            return item
    raise ValueError(f"There is no decision with id {decision_id}")


def experiment_a(decision):
    """A: um único debate, julgado várias vezes."""
    print("\n[Experiment A] One debate, judged several times")
    transcript, turns = run_debate(decision)
    judgements = []
    for i in range(JUDGE_REPEATS):
        print(f" Judgement {i + 1}/{JUDGE_REPEATS}")
        judgements.append(judge(decision, transcript))
    return {"transcript": transcript, "turns": turns, "judgements": judgements}


def experiment_b(decision):
    """B: o pipeline completo (debate + juiz) repetido várias vezes."""
    print("\n[Experiment B] Full pipeline repeated")
    runs = []
    for i in range(PIPELINE_REPEATS):
        print(f" Run {i + 1}/{PIPELINE_REPEATS}")
        transcript, turns = run_debate(decision)
        runs.append({"transcript": transcript, "judgement": judge(decision, transcript)})
    return runs


def experiment_c(decision):
    """C: baseline - o que diria um assistente normal, sem debate?"""
    print("\n[Experiment C] Single helpful assistant (baseline)")
    message = f"Estou a ponderar esta decisão: {decision}\nO que achas?"
    return call_llm(prompts.BASELINE, message)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python experiments.py <decision_id>")
        sys.exit(1)

    item = load_decision(int(sys.argv[1]))
    print(f"Decision {item['id']}: {item['text']}")

    results = {
        "decision": item,
        "experiment_a": experiment_a(item["text"]),
        "experiment_b": experiment_b(item["text"]),
        "baseline": experiment_c(item["text"]),
    }

    path = f"results/decision_{item['id']}.json"
    save_json(results, path)
    print(f"\nDone. Results saved to {path}")