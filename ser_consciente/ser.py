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

from .aprendizado import gerar_nota_aprendizado
from .corpo import EstadoInterno
from .identidade import Identidade
from .memoria import MemoriaAssociativa
from .reflexao import gerar_pensamento

DELTA_POSITIVO_EXPLICITO = 0.7
DELTA_POSITIVO_IMPLICITO = 0.3
DELTA_NEGATIVO = -1.3


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
        self.diario_aprendizado: List[str] = []
        self.ultima_tentativa: Optional[List[str]] = None
        self.total_feedback_positivo: int = 0
        self.total_feedback_negativo: int = 0

    def perceber(self, texto: str) -> List[str]:
        if self.identidade.numero_interacoes == 0:
            self.identidade.registrar_marco(f"primeiras palavras ouvidas: '{texto[:60]}'")
        palavras = self.memoria.perceber(texto)
        self.estado.reagir_a(palavras)
        self.identidade.numero_interacoes += 1
        return palavras

    def pensar(self) -> str:
        pensamento, caminho = gerar_pensamento(self.memoria, self.estado)
        self.monologo.append(pensamento)
        if len(self.monologo) > 200:
            self.monologo = self.monologo[-200:]
        # o próprio pensamento realimenta a memória: um laço mínimo de
        # auto-referência, para que o que ele "diz a si mesmo" também
        # passe a fazer parte do que ele lembra. Reforça só os conceitos
        # do caminho associativo -- nunca tokeniza o texto pronto, ou o
        # esqueleto do molde da frase viraria memória por si só.
        if caminho:
            self.memoria.reforcar(caminho)
        return pensamento

    def tick(self):
        self.memoria.decair()
        self.estado.tick()

    def responder(self, texto: str) -> str:
        # se havia uma tentativa de fala pendente e ninguém a corrigiu
        # até agora, conta como aceita implicitamente -- fraco, mas é
        # sinal de aprendizado mesmo assim.
        if self.ultima_tentativa is not None:
            self.dar_feedback(gostei=True, explicito=False)
        self.perceber(texto)
        pensamento = self.pensar()
        self.tick()
        return pensamento

    def tentar_falar(self, tamanho: int = 3) -> Optional[str]:
        """Gera uma tentativa de fala crua (sem molde de frase) e a
        deixa pendente de correção. Chamar `responder` ou `dar_feedback`
        de novo resolve a pendência -- correção explícita ou aceite
        implícito, um dos dois sempre acontece antes da próxima."""
        if self.ultima_tentativa is not None:
            self.dar_feedback(gostei=True, explicito=False)
        cadeia = self.memoria.gerar_cadeia(tamanho=tamanho)
        if len(cadeia) < 2:
            self.ultima_tentativa = None
            return None
        self.ultima_tentativa = cadeia
        return " ".join(cadeia)

    def dar_feedback(self, gostei: bool, explicito: bool = True) -> Optional[str]:
        """Aplica uma correção (ou aprovação) à última tentativa de fala
        pendente e devolve a nota do diário que explica o que mudou."""
        if not self.ultima_tentativa or len(self.ultima_tentativa) < 2:
            self.ultima_tentativa = None
            return None

        cadeia = self.ultima_tentativa
        self.ultima_tentativa = None

        if gostei:
            delta = DELTA_POSITIVO_EXPLICITO if explicito else DELTA_POSITIVO_IMPLICITO
            self.total_feedback_positivo += 1
        else:
            delta = DELTA_NEGATIVO
            self.total_feedback_negativo += 1

        pares = list(zip(cadeia, cadeia[1:]))
        for a, b in pares:
            self.memoria.reforcar_transicao(a, b, delta)

        nota = gerar_nota_aprendizado(
            self.memoria, pares, gostei, explicito, self.total_feedback_positivo
        )
        self.diario_aprendizado.append(nota)
        if len(self.diario_aprendizado) > 200:
            self.diario_aprendizado = self.diario_aprendizado[-200:]
        return nota

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
            f"Mais presentes na mente agora: {ativos}\n"
            f"Feedback recebido sobre tentativas de fala: "
            f"{self.total_feedback_positivo} positivos, {self.total_feedback_negativo} negativos"
        )

    def to_dict(self) -> dict:
        return {
            "memoria": self.memoria.to_dict(),
            "identidade": self.identidade.to_dict(),
            "estado": self.estado.to_dict(),
            "monologo": self.monologo[-50:],
            "diario_aprendizado": self.diario_aprendizado[-50:],
            "ultima_tentativa": self.ultima_tentativa,
            "total_feedback_positivo": self.total_feedback_positivo,
            "total_feedback_negativo": self.total_feedback_negativo,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Ser":
        ser = cls(
            memoria=MemoriaAssociativa.from_dict(dados.get("memoria", {})),
            identidade=Identidade.from_dict(dados.get("identidade", {})),
            estado=EstadoInterno.from_dict(dados.get("estado", {})),
        )
        ser.monologo = list(dados.get("monologo", []))
        ser.diario_aprendizado = list(dados.get("diario_aprendizado", []))
        ser.ultima_tentativa = dados.get("ultima_tentativa")
        ser.total_feedback_positivo = dados.get("total_feedback_positivo", 0)
        ser.total_feedback_negativo = dados.get("total_feedback_negativo", 0)
        return ser
