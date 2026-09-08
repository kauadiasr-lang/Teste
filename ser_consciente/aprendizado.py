"""Diário de aprendizado.

Gera as notas que explicam, em português simples, o que uma correção
(ou a ausência dela) acabou de mudar na memória. É importante ser
honesto sobre o que isto é: as frases vêm de moldes fixos, igual às
reflexões em `reflexao.py` -- não é o ser "raciocinando" livremente.
A diferença é que aqui o molde está sempre amarrado a um número que
realmente mudou (`memoria.reforcar_transicao`), então a nota nunca é
teatro solto -- ela sempre corresponde a um ajuste real de peso.
"""
from __future__ import annotations

import random
from typing import List, Tuple

from .memoria import MemoriaAssociativa

LIMIAR_CONTRASTE = 0.4

_NOTAS_NEGATIVAS = [
    "'{a} {b}' não fez sentido pra você. Vou evitar colocar '{b}' logo depois de '{a}'.",
    "Isso não colou -- '{b}' depois de '{a}' parece que não funciona.",
]
_NOTAS_POSITIVAS_EXPLICITAS = [
    "'{a} {b}' pareceu funcionar bem. Vou tentar repetir essa ordem.",
    "Você gostou de '{a} {b}'. Isso deve valer a pena repetir.",
]
_NOTAS_POSITIVAS_IMPLICITAS = [
    "Você não corrigiu '{a} {b}' -- acho que essa ordem faz sentido.",
    "Nenhuma correção depois de '{a} {b}'. Vou manter essa ordem por enquanto.",
]
_NOTAS_CONTRASTE = [
    "'{bom_a}' pode vir antes de '{bom_b}'! Mas não depois disso -- aprendi agora.",
    "Interessante: '{bom_a} {bom_b}' funciona, mas '{bom_b} {bom_a}' não. A ordem importa.",
]
_NOTAS_META = [
    "Isso pareceu bom pra você. O que parece bom, eu devo repetir.",
    "Reforçar o que você gosta parece fazer sentido -- vou tentar mais disso.",
    "Evitar o que incomoda parece tão importante quanto repetir o que funciona.",
]


def _nota_contraste(memoria: MemoriaAssociativa, a: str, b: str) -> str | None:
    """Detecta o caso 'A antes de B tudo bem, B antes de A não' -- em
    qualquer ordem em que as duas metades tenham sido aprendidas."""
    t_ab = memoria.transicao(a, b)
    t_ba = memoria.transicao(b, a)
    if t_ab and t_ba:
        if t_ab.feedback > LIMIAR_CONTRASTE and t_ba.feedback < -LIMIAR_CONTRASTE:
            return random.choice(_NOTAS_CONTRASTE).format(bom_a=a, bom_b=b)
        if t_ba.feedback > LIMIAR_CONTRASTE and t_ab.feedback < -LIMIAR_CONTRASTE:
            return random.choice(_NOTAS_CONTRASTE).format(bom_a=b, bom_b=a)
    return None


def gerar_nota_aprendizado(
    memoria: MemoriaAssociativa,
    pares: List[Tuple[str, str]],
    gostei: bool,
    explicito: bool,
    total_positivos: int,
) -> str:
    if not pares:
        return "(nada pra aprender aqui -- a tentativa era curta demais)"

    a, b = pares[0]

    contraste = _nota_contraste(memoria, a, b)
    if contraste:
        nota = contraste
    elif gostei:
        modelo = _NOTAS_POSITIVAS_EXPLICITAS if explicito else _NOTAS_POSITIVAS_IMPLICITAS
        nota = random.choice(modelo).format(a=a, b=b)
    else:
        nota = random.choice(_NOTAS_NEGATIVAS).format(a=a, b=b)

    if gostei and (total_positivos == 1 or total_positivos % 10 == 0):
        nota += " " + random.choice(_NOTAS_META)

    return nota
