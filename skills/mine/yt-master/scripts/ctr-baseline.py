#!/usr/bin/env python3
"""ctr-baseline.py — read-only / cálculo.

Calcula o CTR (taxa de cliques) a partir de impressões e cliques e o compara
com a baseline do PRÓPRIO canal (a média de 90 dias). Reforça a regra do canal
Escola Para Youtubers: "CTR é relativo ao seu canal/nicho, não um alvo universal
de 5%". Não altera nenhum arquivo.

Uso:
  python3 ctr-baseline.py --impressoes 540000 --cliques 33000 --baseline 6.2
  python3 ctr-baseline.py --impressoes 100 --cliques 5            # alerta amostragem

Saída: diagnóstico em stdout (exit 0); erro de entrada em stderr (exit 1).
"""
import argparse
import sys

# Limiar editorial para lembrar incerteza; não é um teste de significância.
MIN_IMPRESSOES_CONFIAVEL = 1000


def main() -> int:
    p = argparse.ArgumentParser(description="Calcula CTR e compara com a baseline do canal.")
    p.add_argument("--impressoes", type=int, required=True, help="Número de impressões.")
    p.add_argument("--cliques", type=int, required=True, help="Número de cliques.")
    p.add_argument(
        "--baseline",
        type=float,
        default=None,
        help="Média de CTR de 90 dias do próprio canal, em %% (ex.: 6.2). Opcional.",
    )
    args = p.parse_args()

    if args.impressoes <= 0:
        print("ERRO: --impressoes deve ser > 0.", file=sys.stderr)
        return 1
    if args.cliques < 0 or args.cliques > args.impressoes:
        print("ERRO: --cliques deve estar entre 0 e --impressoes.", file=sys.stderr)
        return 1

    ctr = args.cliques / args.impressoes * 100
    print(f"CTR: {ctr:.2f}%  ({args.cliques:,} cliques / {args.impressoes:,} impressões)")

    if args.impressoes < MIN_IMPRESSOES_CONFIAVEL:
        print(
            f"⚠️  AMOSTRAGEM BAIXA (< {MIN_IMPRESSOES_CONFIAVEL} impressões): este CTR é "
            "uma observação com amostra pequena. Isso não prova inflação nem "
            "significância; compare público, origem do tráfego e janela de observação."
        )

    if args.baseline is not None:
        if args.baseline <= 0:
            print("ERRO: --baseline deve ser > 0 quando informada.", file=sys.stderr)
            return 1
        delta = ctr - args.baseline
        sinal = "acima" if delta >= 0 else "abaixo"
        print(
            f"Baseline do canal (90d): {args.baseline:.2f}%  →  este vídeo está "
            f"{abs(delta):.2f} ponto(s) {sinal} da sua média."
        )
        if delta >= 0:
            print("CTR observado igual ou acima da baseline; isoladamente isso não prova a qualidade do título/thumbnail.")
        else:
            print(
                "CTR observado abaixo da baseline. Compare público, origem do tráfego, "
                "formato e janela antes de atribuir a diferença ao título/thumbnail."
            )
    else:
        print(
            "Sem --baseline: compare SEMPRE com a média de 90 dias do próprio canal "
            "(Studio → Analytics → Conteúdo → Vídeos → 90 dias). Não existe alvo universal de 5%."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
