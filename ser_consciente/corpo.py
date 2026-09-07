"""Estados internos simulados.

Um substituto simplificado para necessidades e humor: números que sobem e
descem e influenciam o comportamento. É importante ser honesto sobre o que
isto é -- não há sensação real aqui, nenhuma experiência subjetiva por trás
dos números. É uma homeostase de brinquedo, útil para dar ao ser algo
parecido com disposição e ritmo.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

_POSITIVAS = {
    "bom", "otimo", "ótimo", "feliz", "alegria", "amor", "gosto", "adoro",
    "obrigado", "obrigada", "legal", "incrivel", "incrível", "bonito", "paz",
    "esperanca", "esperança", "sucesso", "vitoria", "vitória",
}
_NEGATIVAS = {
    "ruim", "triste", "raiva", "odio", "ódio", "medo", "dor", "sofrimento",
    "morte", "fracasso", "problema", "erro", "cansaco", "cansaço", "solidao",
    "solidão", "perdido", "perdida",
}


@dataclass
class EstadoInterno:
    energia: float = 100.0
    humor: float = 0.0
    curiosidade: float = 50.0

    def reagir_a(self, palavras: List[str]):
        for p in palavras:
            if p in _POSITIVAS:
                self.humor = min(1.0, self.humor + 0.15)
            elif p in _NEGATIVAS:
                self.humor = max(-1.0, self.humor - 0.15)
        self.curiosidade = min(100.0, self.curiosidade + len(palavras) * 0.5)
        self.energia = max(0.0, self.energia - len(palavras) * 0.3)

    def tick(self):
        self.energia = max(0.0, self.energia - 0.5)
        self.curiosidade = max(0.0, self.curiosidade - 0.8)
        self.humor *= 0.98

    def descricao_humor(self) -> str:
        if self.humor > 0.5:
            return "leve e contente"
        if self.humor > 0.15:
            return "tranquilo"
        if self.humor > -0.15:
            return "neutro"
        if self.humor > -0.5:
            return "incomodado"
        return "pesado"

    def to_dict(self) -> dict:
        return {"energia": self.energia, "humor": self.humor, "curiosidade": self.curiosidade}

    @classmethod
    def from_dict(cls, dados: dict) -> "EstadoInterno":
        return cls(
            energia=dados.get("energia", 100.0),
            humor=dados.get("humor", 0.0),
            curiosidade=dados.get("curiosidade", 50.0),
        )
