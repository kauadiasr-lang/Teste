"""Modelo de si.

O que persiste entre uma execução e outra: um nome, um instante de
nascimento (para que a idade seja tempo real, não simulado) e uma lista de
marcos -- uma autobiografia mínima que dá a este ser uma história contínua
em vez de recomeçar do zero a cada conversa.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class Identidade:
    nome: str = "Anima"
    nascimento: float = field(default_factory=time.time)
    marcos: List[str] = field(default_factory=list)
    numero_interacoes: int = 0

    def idade_em_segundos(self) -> float:
        return time.time() - self.nascimento

    def registrar_marco(self, descricao: str):
        self.marcos.append(f"[interação {self.numero_interacoes}] {descricao}")
        if len(self.marcos) > 50:
            self.marcos = self.marcos[-50:]

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "nascimento": self.nascimento,
            "marcos": self.marcos,
            "numero_interacoes": self.numero_interacoes,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Identidade":
        return cls(
            nome=dados.get("nome", "Anima"),
            nascimento=dados.get("nascimento", time.time()),
            marcos=list(dados.get("marcos", [])),
            numero_interacoes=dados.get("numero_interacoes", 0),
        )
