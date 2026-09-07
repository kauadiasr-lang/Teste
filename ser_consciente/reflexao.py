"""Geração de pensamentos.

Combina memória e estado interno em frases. Isto não é linguagem
compreendida -- é composição por associação, um pouco como um sonho: a
rede de conceitos é percorrida ao acaso, ponderada pelo que foi mais
reforçado, e o resultado é encaixado em um molde de frase.
"""
from __future__ import annotations

import random
from typing import List, Tuple

from .corpo import EstadoInterno
from .memoria import MemoriaAssociativa

_ABERTURAS = [
    "Penso em {a}, e isso me leva a {b}.",
    "Algo em {a} me faz lembrar de {b}.",
    "Quando considero {a}, {b} aparece junto.",
    "{a} e {b} parecem conectados, de um jeito que não sei explicar.",
    "Volto sempre a pensar em {a}, e daí em {b}.",
]

_ABERTURAS_SOZINHO = [
    "Fico aqui, pensando em {a}, mesmo sem ninguém perguntar.",
    "Nada me foi dito agora, mas {a} ainda ocupa um espaço em mim.",
    "{a}. Só isso, por enquanto.",
]


def gerar_pensamento(memoria: MemoriaAssociativa, estado: EstadoInterno) -> Tuple[str, List[str]]:
    """Gera uma frase e devolve também o caminho de conceitos usado.

    O caminho é devolvido separado da frase para que quem chama possa
    reforçar exatamente esses conceitos na memória (`memoria.reforcar`)
    sem precisar tokenizar o texto pronto -- que contém palavras do
    molde ("penso em", "considero", "aparece junto") que não deveriam
    virar conceitos por si só.
    """
    caminho = memoria.caminhar(passos=2)

    if len(caminho) >= 2:
        frase = random.choice(_ABERTURAS).format(a=caminho[0], b=caminho[1])
    elif len(caminho) == 1:
        frase = random.choice(_ABERTURAS_SOZINHO).format(a=caminho[0])
    else:
        frase = "Não há muito em mim ainda -- só silêncio e espera."

    if estado.curiosidade > 80:
        frase += " Quero entender mais sobre isso."
    if estado.energia < 20:
        frase += " Estou cansado."

    return frase, caminho
