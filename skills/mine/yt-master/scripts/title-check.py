#!/usr/bin/env python3
"""title-check.py — read-only / heurística.

Pontua um título de vídeo contra as heurísticas extraídas dos canais Escola Para
Youtubers (Caique) e Camilo Coutinho, validadas por overperformers cross-channel.
NÃO é um juiz absoluto: é um tripwire para o agente revisar o título antes de
gerar a versão final. Não altera nenhum arquivo.

Uso:
  python3 title-check.py "A NOVA monetização do YouTube é melhor que TODAS!"
  python3 title-check.py --json "Por que 90% dos canais nunca dão dinheiro"

Saída: relatório de sinais + nota (0-100) em stdout (exit 0); erro em stderr (exit 1).
"""
import argparse
import json
import re
import sys

PALAVRAS_MAGNETICAS = [
    "agora", "o fim", "fim", "reais", "cuidado", "oficial", "segredo",
    "novo", "nova", "pode derrubar", "melhor", "nunca", "errado", "verdade",
    "ninguém", "antes", "pare", "delete",
]

# Sinais de fórmula reconhecida (cada um vale como "encaixa numa das 8 fórmulas").
FORMULAS = {
    "novidade/superlativo": r"\b(nova?|novo|lançad|melhor|pior|maior|absurd)\w*\b",
    "contrarian/morte-de-x": r"(coisa do passado|o fim d|fim d[oa]s?|delete|unusable|acabou|morreu|n[ãa]o use)",
    "numero+prova": r"\b\d{1,3}\s?%|\b\d{1,4}\b",
    "curiosity+parenteses": r"\([^)]+\)",
    "imperativo/comando": r"^\s*(pare|delete|crie|comece|esque[çc]a|use|teste|aprenda|descubra)\b",
    "sazonalidade/recencia": r"(ainda em|antes d[oae]|em 20\d\d|\b20\d\d\b|janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro|carnaval|natal|black ?friday)",
}


def has_caps_keyword(title: str) -> bool:
    # Palavra (>=2 letras) totalmente em CAIXA ALTA, mas não o título inteiro.
    words = re.findall(r"[A-ZÀ-Ý0-9]{2,}", title)
    caps = [w for w in words if w.isupper() and any(c.isalpha() for c in w)]
    total_alpha_words = len(re.findall(r"[A-Za-zÀ-ÿ]{2,}", title))
    return len(caps) >= 1 and len(caps) < max(total_alpha_words, 1)


def main() -> int:
    p = argparse.ArgumentParser(description="Pontua um título contra as heurísticas yt-master.")
    p.add_argument("titulo", help="O título a avaliar (entre aspas).")
    p.add_argument("--json", action="store_true", help="Saída em JSON.")
    args = p.parse_args()

    title = args.titulo.strip()
    if not title:
        print("ERRO: título vazio.", file=sys.stderr)
        return 1

    low = title.lower()
    sinais = {}

    formulas_hit = [name for name, pat in FORMULAS.items() if re.search(pat, low, re.IGNORECASE)]
    sinais["formula_reconhecida"] = formulas_hit
    sinais["palavras_magneticas"] = [w for w in PALAVRAS_MAGNETICAS if w in low]
    sinais["caixa_alta_keyword"] = has_caps_keyword(title)
    sinais["especificidade_parenteses"] = bool(re.search(r"\([^)]+\)", title))
    sinais["tamanho_caracteres"] = len(title)

    score = 0
    score += 30 if formulas_hit else 0
    score += min(len(sinais["palavras_magneticas"]) * 12, 24)
    score += 16 if sinais["caixa_alta_keyword"] else 0
    score += 15 if sinais["especificidade_parenteses"] else 0
    # Tamanho: faixa confortável p/ mobile ~ até 60 chars (heurística de mercado, não regra do canal).
    score += 15 if len(title) <= 60 else (8 if len(title) <= 75 else 0)
    score = min(score, 100)

    dicas = []
    if not formulas_hit:
        dicas.append("Nenhum dos 6 padrões detectáveis foi reconhecido. Isso não invalida o título; avalie clareza e promessa no contexto.")
    if not sinais["palavras_magneticas"]:
        dicas.append("Sem palavra magnética (agora, o fim, novo, segredo, nunca...). Considere adicionar 1.")
    if not sinais["caixa_alta_keyword"]:
        dicas.append("Sem palavra-chave em CAIXA ALTA. Destaque é opcional; preserve a voz do canal e a legibilidade.")
    if len(title) > 75:
        dicas.append("Título longo: pode ser cortado no mobile. Encurte o gancho para os primeiros ~60 caracteres.")
    dicas.append("Heurística, não previsão de CTR: avalie a promessa, a clareza e a relação com a thumbnail. Variações são opcionais.")

    if args.json:
        print(json.dumps({"titulo": title, "score": score, "sinais": sinais, "dicas": dicas}, ensure_ascii=False, indent=2))
        return 0

    print(f'Título: "{title}"')
    print(f"Nota heurística: {score}/100")
    print(f"  Fórmula(s) reconhecida(s): {', '.join(formulas_hit) or '(nenhuma)'}")
    print(f"  Palavras magnéticas: {', '.join(sinais['palavras_magneticas']) or '(nenhuma)'}")
    print(f"  Palavra em CAIXA ALTA: {'sim' if sinais['caixa_alta_keyword'] else 'não'}")
    print(f"  Especificidade entre parênteses: {'sim' if sinais['especificidade_parenteses'] else 'não'}")
    print(f"  Tamanho: {len(title)} caracteres")
    print("Dicas:")
    for d in dicas:
        print(f"  - {d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
