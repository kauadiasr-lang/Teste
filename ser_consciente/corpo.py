"""Estados internos simulados.

Um substituto simplificado para necessidades e humor: números que sobem e
descem e influenciam o comportamento. É importante ser honesto sobre o que
isto é -- não há sensação real aqui, nenhuma experiência subjetiva por trás
dos números. É uma homeostase de brinquedo, útil para dar ao ser algo
parecido com disposição e ritmo.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
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

# pontos de energia recuperados por segundo real de ausência: descansar
# (o tempo passando sem que nada seja percebido) restaura energia, do
# mesmo jeito que ouvir palavras a consome.
_TAXA_RECUPERACAO_ENERGIA = 0.2
_CUSTO_METABOLICO_TICK = 0.5


@dataclass
class EstadoInterno:
    energia: float = 100.0
    humor: float = 0.0
    curiosidade: float = 50.0
    ultima_atualizacao: float = field(default_factory=time.time)

    def reagir_a(self, palavras: List[str]):
        for p in palavras:
            if p in _POSITIVAS:
                self.humor = min(1.0, self.humor + 0.15)
            elif p in _NEGATIVAS:
                self.humor = max(-1.0, self.humor - 0.15)
        self.curiosidade = min(100.0, self.curiosidade + len(palavras) * 0.5)
        self.energia = max(0.0, self.energia - len(palavras) * 0.3)

    def tick(self):
        agora = time.time()
        ausencia = max(0.0, agora - self.ultima_atualizacao)
        self.energia = min(100.0, self.energia + ausencia * _TAXA_RECUPERACAO_ENERGIA)
        self.energia = max(0.0, self.energia - _CUSTO_METABOLICO_TICK)
        self.curiosidade = max(0.0, self.curiosidade - 0.8)
        self.humor *= 0.98
        self.ultima_atualizacao = agora

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
        return {
            "energia": self.energia,
            "humor": self.humor,
            "curiosidade": self.curiosidade,
            "ultima_atualizacao": self.ultima_atualizacao,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "EstadoInterno":
        return cls(
            energia=dados.get("energia", 100.0),
            humor=dados.get("humor", 0.0),
            curiosidade=dados.get("curiosidade", 50.0),
            ultima_atualizacao=dados.get("ultima_atualizacao", time.time()),
        )
