"""
debate.py
Núcleo do sistema multiagente:
  1. O Proponente e o Oponente debatem durante várias rondas.
  2. O Juiz lê a transcrição completa e produz o julgamento.

Uso:
    python debate.py "Should I quit my job to do a master's degree?"
"""

import json
import os
import re
import sys
import time
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

import prompts

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

NUM_ROUNDS = 3        # número de rondas do debate
PAUSE_SECONDS = 3     # pausa entre chamadas para não passar os limites do plano gratuito
THINKING_LEVEL = "low"

client = genai.Client(api_key=API_KEY)


def call_llm(system_prompt, user_message, temperature=1.0):
    """Envia UMA mensagem ao modelo e devolve o texto da resposta.
    Cada chamada é independente: o modelo não guarda memória entre chamadas."""
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL),

                ),
            )
            time.sleep(PAUSE_SECONDS)
            return (response.text or "").strip()
        except Exception as error:
            if "404" in str(error):
                raise
            print(f"  [warning] {error}. Retrying in 30 seconds...")
            time.sleep(30)
    raise RuntimeError("The LLM call failed 5 times in a row.")


def build_message(decision, transcript, instruction):
    """Constrói a mensagem que um agente recebe: a decisão + o debate até agora.
    É aqui que garantimos que cada agente só vê os ARGUMENTOS do outro,
    nunca o system prompt do outro."""
    if transcript == "":
        transcript = "(ainda nada - és tu que abres o debate)"
    return (
        f"DECISÃO EM CAUSA:\n{decision}\n\n"
        f"DEBATE ATÉ AGORA:\n{transcript}\n\n"
        f"{instruction}"
    )

def run_debate(decision, num_rounds=NUM_ROUNDS):
    """Corre o debate e devolve a transcrição (texto) e a lista de intervenções."""
    transcript = ""
    turns = []

    for round_number in range(1, num_rounds + 1):
        for role, system_prompt in [("PROPONENT", prompts.PROPONENT),
                                    ("OPPONENT", prompts.OPPONENT)]:
            print(f"  Round {round_number} - {role} is speaking...")
            message = build_message(decision, transcript,
                                    f"É a tua vez ({role}, ronda {round_number}).")
            argument = call_llm(system_prompt, message)

            transcript += f"\n=== {role} (round {round_number}) ===\n{argument}\n"
            turns.append({"round": round_number, "role": role, "text": argument})

    return transcript, turns


def judge(decision, transcript, temperature=1.0):
    """O Juiz lê a transcrição completa e devolve o julgamento."""
    print("  The JUDGE is deciding...")
    message = build_message(decision, transcript, "Escreve agora o teu julgamento.")
    text = call_llm(prompts.JUDGE, message, temperature)
    return {
        "text": text,
        "verdict": extract_verdict(text),
        "unanswered_ids": extract_unanswered_ids(text),
    }


def extract_verdict(judgement_text):
    """Procura a linha 'VERDICT: ...' no fim do julgamento."""
    matches = re.findall(r"VERDICT:\s*\**\s*(FOR|AGAINST|UNSETTLED)", judgement_text.upper())
    if matches:
        return matches[-1]   
    return "PARSE_ERROR"     


def extract_unanswered_ids(judgement_text):
    """Procura a linha 'UNANSWERED_IDS: P2, O3' e devolve ['O3', 'P2']."""
    match = re.search(r"UNANSWERED_IDS:(.*)", judgement_text.upper())
    if not match:
        return []
    ids = re.findall(r"\b[PO]\d+\b", match.group(1))
    return sorted(set(ids))

def save_json(data, path):
    """Guarda um dicionário num ficheiro JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        decision = sys.argv[1]
    else:
        decision = input("Describe the decision you are considering: ")

    print("\nStarting the debate...")
    transcript, turns = run_debate(decision)
    judgement = judge(decision, transcript)

    print("\n================ TRANSCRIPT ================")
    print(transcript)
    print("\n================ JUDGEMENT =================")
    print(judgement["text"])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"results/single_run_{timestamp}.json"
    save_json({"decision": decision, "turns": turns,
               "transcript": transcript, "judgement": judgement}, path)
    print(f"\nSaved to {path}")