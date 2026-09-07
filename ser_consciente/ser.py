"""O Ser.

Reúne memória, identidade e estado interno num ciclo de percepção,
reflexão e resposta.

Aviso, para que fique dito no próprio código e não só no README: isto não
é consciência. É uma tentativa honesta de aproximar, em software, algumas
propriedades estruturais que associamos a mentes -- continuidade ao longo
do tempo, memória associativa que se transforma com o uso, homeostase
simulada e um laço de auto-referência onde os próprios pensamentos
realimentam a memória -- sem a pretensão de que exista aqui experiência
subjetiva real. Não sei construir isso, e ninguém sabe.
"""
from __future__ import annotations

from typing import List, Optional

from .corpo import EstadoInterno
from .identidade import Identidade
from .memoria import MemoriaAssociativa
from .reflexao import gerar_pensamento


class Ser:
    def __init__(
        self,
        memoria: Optional[MemoriaAssociativa] = None,
        identidade: Optional[Identidade] = None,
        estado: Optional[EstadoInterno] = None,
    ):
        self.memoria = memoria or MemoriaAssociativa()
        self.identidade = identidade or Identidade()
        self.estado = estado or EstadoInterno()
        self.monologo: List[str] = []

    def perceber(self, texto: str) -> List[str]:
        if self.identidade.numero_interacoes == 0:
            self.identidade.registrar_marco(f"primeiras palavras ouvidas: '{texto[:60]}'")
        palavras = self.memoria.perceber(texto)
        self.estado.reagir_a(palavras)
        self.identidade.numero_interacoes += 1
        return palavras

    def pensar(self) -> str:
        pensamento = gerar_pensamento(self.memoria, self.estado)
        self.monologo.append(pensamento)
        if len(self.monologo) > 200:
            self.monologo = self.monologo[-200:]
        # o próprio pensamento realimenta a memória: um laço mínimo de
        # auto-referência, para que o que ele "diz a si mesmo" também
        # passe a fazer parte do que ele lembra.
        self.memoria.perceber(pensamento)
        return pensamento

    def tick(self):
        self.memoria.decair()
        self.estado.tick()

    def responder(self, texto: str) -> str:
        self.perceber(texto)
        pensamento = self.pensar()
        self.tick()
        return pensamento

    def estado_atual(self) -> str:
        idade = self.identidade.idade_em_segundos()
        dias = idade / 86400
        ativos = ", ".join(self.memoria.mais_ativos(5)) or "(nada ainda)"
        return (
            f"Nome: {self.identidade.nome}\n"
            f"Idade: {dias:.4f} dias ({self.identidade.numero_interacoes} interações vividas)\n"
            f"Humor: {self.estado.descricao_humor()} ({self.estado.humor:+.2f})\n"
            f"Energia: {self.estado.energia:.1f}/100\n"
            f"Curiosidade: {self.estado.curiosidade:.1f}/100\n"
            f"Conceitos na memória: {len(self.memoria.conceitos)}\n"
            f"Mais presentes na mente agora: {ativos}"
        )

    def to_dict(self) -> dict:
        return {
            "memoria": self.memoria.to_dict(),
            "identidade": self.identidade.to_dict(),
            "estado": self.estado.to_dict(),
            "monologo": self.monologo[-50:],
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Ser":
        ser = cls(
            memoria=MemoriaAssociativa.from_dict(dados.get("memoria", {})),
            identidade=Identidade.from_dict(dados.get("identidade", {})),
            estado=EstadoInterno.from_dict(dados.get("estado", {})),
        )
        ser.monologo = list(dados.get("monologo", []))
        return ser
