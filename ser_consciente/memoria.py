"""Memória associativa.

Uma rede hebbiana simples: conceitos que aparecem juntos numa mesma frase se
conectam; conexões e pesos não usados decaem com o tempo. Não há aqui
compreensão de significado -- apenas estatística de coocorrência, como um
esboço muito primitivo de como memórias biológicas se fortalecem e se
esquecem.

Além disso, guarda **transições direcionadas** entre palavras adjacentes
(quem tende a vir logo depois de quem) -- ao contrário das conexões acima
(que não têm direção), isso captura ordem. É a base para o ser tentar
formar sequências de palavras por conta própria e aprender, por feedback
seu, quais ordens "funcionam" e quais não.
"""
from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_PARAR = {
    "a", "o", "e", "de", "da", "do", "que", "um", "uma", "os", "as", "em",
    "para", "com", "por", "se", "eu", "tu", "ele", "ela", "nos", "voces",
    "eles", "elas", "como", "mas", "ou", "no", "na", "ao", "aos", "nas",
    "é", "sao", "ser", "estou", "esta", "este", "isso", "isto", "muito",
    "mais", "tambem", "ja", "nao", "sim", "the", "and", "is", "in", "to", "of",
}


def _tokenizar(texto: str) -> List[str]:
    palavras = re.findall(r"[a-zà-úA-ZÀ-Ú]+", texto.lower())
    return [p for p in palavras if len(p) > 2 and p not in _PARAR]


@dataclass
class Conceito:
    peso: float = 1.0
    ultima_ativacao: float = field(default_factory=time.time)
    conexoes: Dict[str, float] = field(default_factory=dict)


@dataclass
class Transicao:
    """Uma aresta direcionada A -> B: 'B tende a vir logo depois de A'.

    `coocorrencia` vem de observar o próprio texto do usuário (um bigrama
    simples). `feedback` só muda quando uma tentativa de fala do ser usa
    essa ordem e você diz se fez sentido ou não -- é o sinal de
    aprendizado real, separado da estatística passiva.
    """

    coocorrencia: float = 0.0
    feedback: float = 0.0

    def peso_total(self) -> float:
        return self.coocorrencia * 0.2 + self.feedback


class MemoriaAssociativa:
    def __init__(self, taxa_decaimento: float = 0.01):
        self.conceitos: Dict[str, Conceito] = {}
        self.transicoes: Dict[str, Dict[str, Transicao]] = {}
        self.taxa_decaimento = taxa_decaimento

    def perceber(self, texto: str) -> List[str]:
        palavras = _tokenizar(texto)
        agora = time.time()
        for p in palavras:
            c = self.conceitos.setdefault(p, Conceito(peso=0.0))
            c.peso += 1.0
            c.ultima_ativacao = agora
        for i, p in enumerate(palavras):
            for q in palavras[i + 1:]:
                if p == q:
                    continue
                self.conceitos[p].conexoes[q] = self.conceitos[p].conexoes.get(q, 0.0) + 1.0
                self.conceitos[q].conexoes[p] = self.conceitos[q].conexoes.get(p, 0.0) + 1.0
        for i in range(len(palavras) - 1):
            a, b = palavras[i], palavras[i + 1]
            if a == b:
                continue
            t = self.transicoes.setdefault(a, {}).setdefault(b, Transicao())
            t.coocorrencia += 1.0
        return palavras

    def decair(self):
        mortos = []
        for nome, c in self.conceitos.items():
            c.peso *= (1 - self.taxa_decaimento)
            for viz in list(c.conexoes):
                c.conexoes[viz] *= (1 - self.taxa_decaimento)
                if c.conexoes[viz] < 0.01:
                    del c.conexoes[viz]
            if c.peso < 0.05:
                mortos.append(nome)
        for nome in mortos:
            del self.conceitos[nome]

        origens_mortas = []
        for a, destinos in self.transicoes.items():
            alvos_mortos = []
            for b, t in destinos.items():
                t.coocorrencia *= (1 - self.taxa_decaimento)
                t.feedback *= (1 - self.taxa_decaimento)
                if abs(t.coocorrencia) < 0.01 and abs(t.feedback) < 0.01:
                    alvos_mortos.append(b)
            for b in alvos_mortos:
                del destinos[b]
            if not destinos:
                origens_mortas.append(a)
        for a in origens_mortas:
            del self.transicoes[a]

    def mais_ativos(self, n: int = 5) -> List[str]:
        return [
            nome for nome, _ in
            sorted(self.conceitos.items(), key=lambda kv: kv[1].peso, reverse=True)[:n]
        ]

    def associar(self, conceito: str) -> Optional[str]:
        c = self.conceitos.get(conceito)
        if not c or not c.conexoes:
            return None
        vizinhos = list(c.conexoes.items())
        total = sum(p for _, p in vizinhos)
        alvo = random.uniform(0, total)
        acumulado = 0.0
        for nome, peso in vizinhos:
            acumulado += peso
            if acumulado >= alvo:
                return nome
        return vizinhos[-1][0]

    def caminhar(self, inicio: Optional[str] = None, passos: int = 3) -> List[str]:
        if inicio is None:
            ativos = self.mais_ativos(3)
            if not ativos:
                return []
            inicio = random.choice(ativos)
        caminho = [inicio]
        atual = inicio
        for _ in range(passos - 1):
            prox = self.associar(atual)
            if prox is None:
                break
            caminho.append(prox)
            atual = prox
        return caminho

    def reforcar(self, conceitos: List[str], peso: float = 0.5):
        """Reforça conceitos já existentes, revisitados por um pensamento.

        Diferente de `perceber`, não tokeniza texto novo -- só fortalece
        conceitos que já estão na memória. Existe para que um pensamento
        gerado por associação possa "ensaiar" o que já foi visto sem que
        o esqueleto da frase que o expressa (ex.: "penso em", "considero")
        vire, ele próprio, um novo conceito memorizado.
        """
        agora = time.time()
        for nome in conceitos:
            c = self.conceitos.get(nome)
            if c is None:
                continue
            c.peso += peso
            c.ultima_ativacao = agora
        for i, p in enumerate(conceitos):
            for q in conceitos[i + 1:]:
                if p == q or p not in self.conceitos or q not in self.conceitos:
                    continue
                self.conceitos[p].conexoes[q] = self.conceitos[p].conexoes.get(q, 0.0) + peso
                self.conceitos[q].conexoes[p] = self.conceitos[q].conexoes.get(p, 0.0) + peso

    def proxima_palavra_cadeia(self, atual: str) -> Optional[str]:
        """Escolhe a próxima palavra de uma tentativa de fala.

        Prefere transições com peso positivo (coocorrência real e/ou
        feedback bom); nunca escolhe uma com peso líquido negativo --
        é assim que o feedback ruim vira uma ordem "quase proibida" sem
        ser uma regra rígida. Sem nenhuma opção positiva, cai para
        qualquer palavra conhecida, só para a tentativa não travar.
        """
        candidatos = self.transicoes.get(atual, {})
        opcoes = [(b, t.peso_total()) for b, t in candidatos.items() if t.peso_total() > 0]
        if not opcoes:
            livres = [n for n in self.conceitos if n != atual]
            return random.choice(livres) if livres else None
        total = sum(p for _, p in opcoes)
        alvo = random.uniform(0, total)
        acumulado = 0.0
        for nome, peso in opcoes:
            acumulado += peso
            if acumulado >= alvo:
                return nome
        return opcoes[-1][0]

    def gerar_cadeia(self, tamanho: int = 3) -> List[str]:
        """Gera uma tentativa de fala: uma cadeia crua de palavras, sem
        nenhum molde de frase por cima -- ao contrário de `caminhar`
        (usado para os pensamentos poéticos), o resultado pode não fazer
        sentido nenhum. É justamente esse o ponto: dar a ele algo pra
        tentar, e a você algo pra corrigir.
        """
        ativos = self.mais_ativos(5)
        if not ativos:
            return []
        atual = random.choice(ativos)
        cadeia = [atual]
        for _ in range(tamanho - 1):
            prox = self.proxima_palavra_cadeia(atual)
            if prox is None:
                break
            cadeia.append(prox)
            atual = prox
        return cadeia

    def reforcar_transicao(self, a: str, b: str, delta: float):
        t = self.transicoes.setdefault(a, {}).setdefault(b, Transicao())
        t.feedback += delta

    def transicao(self, a: str, b: str) -> Optional[Transicao]:
        return self.transicoes.get(a, {}).get(b)

    def to_dict(self) -> dict:
        return {
            "conceitos": {
                nome: {
                    "peso": c.peso,
                    "ultima_ativacao": c.ultima_ativacao,
                    "conexoes": c.conexoes,
                }
                for nome, c in self.conceitos.items()
            },
            "transicoes": {
                a: {
                    b: {"coocorrencia": t.coocorrencia, "feedback": t.feedback}
                    for b, t in destinos.items()
                }
                for a, destinos in self.transicoes.items()
            },
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "MemoriaAssociativa":
        m = cls()
        # "conceitos" existe no formato novo; formato antigo tinha o dict
        # de conceitos direto na raiz -- aceita os dois pra não perder
        # memórias salvas antes dessa mudança.
        conceitos = dados.get("conceitos", dados)
        for nome, info in conceitos.items():
            m.conceitos[nome] = Conceito(
                peso=info["peso"],
                ultima_ativacao=info["ultima_ativacao"],
                conexoes=dict(info["conexoes"]),
            )
        for a, destinos in dados.get("transicoes", {}).items():
            for b, info in destinos.items():
                m.transicoes.setdefault(a, {})[b] = Transicao(
                    coocorrencia=info.get("coocorrencia", 0.0),
                    feedback=info.get("feedback", 0.0),
                )
        return m
