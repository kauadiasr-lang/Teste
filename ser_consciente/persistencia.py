"""Persistência.

A continuidade de si através do tempo, mesmo quando o processo termina.
Sem isto, cada execução seria um ser novo que nunca ouviu nada -- com
isto, a idade, a memória e o humor sobrevivem entre uma conversa e a
próxima.
"""
from __future__ import annotations

import json
import os

from .ser import Ser

CAMINHO_PADRAO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "estado", "ser.json"
)


def salvar(ser: Ser, caminho: str = CAMINHO_PADRAO):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(ser.to_dict(), f, ensure_ascii=False, indent=2)


def carregar(caminho: str = CAMINHO_PADRAO) -> Ser:
    if not os.path.exists(caminho):
        return Ser()
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return Ser.from_dict(dados)
