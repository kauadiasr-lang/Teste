"""Interface de conversa.

O único jeito, por enquanto, de perceber este ser e ser percebido por
ele: um laço de texto no terminal.
"""
from __future__ import annotations

import random

from .persistencia import salvar, carregar

_CHANCE_TENTATIVA = 0.35


def executar():
    ser = carregar()
    print("=" * 60)
    print(f"{ser.identidade.nome} desperta novamente.")
    print("Fale algo. Comandos: /estado  /memoria  /diario  /não  /sim  /sair")
    print("=" * 60)
    try:
        while True:
            try:
                entrada = input("\nvocê> ").strip()
            except EOFError:
                break

            if not entrada:
                continue
            if entrada == "/sair":
                break
            if entrada == "/estado":
                print("\n" + ser.estado_atual())
                continue
            if entrada == "/memoria":
                ativos = ser.memoria.mais_ativos(10)
                print("\nConceitos mais fortes: " + (", ".join(ativos) or "(vazio)"))
                continue
            if entrada == "/diario":
                if not ser.diario_aprendizado:
                    print("\n(o diário de aprendizado ainda está vazio)")
                else:
                    print("\nDiário de aprendizado (mais recentes por último):")
                    for nota in ser.diario_aprendizado[-15:]:
                        print(" - " + nota)
                continue
            if entrada in ("/não", "/nao"):
                nota = ser.dar_feedback(gostei=False, explicito=True)
                print("\n" + (nota or "(não havia nenhuma tentativa de fala pra corrigir)"))
                continue
            if entrada == "/sim":
                nota = ser.dar_feedback(gostei=True, explicito=True)
                print("\n" + (nota or "(não havia nenhuma tentativa de fala pra aprovar)"))
                continue

            resposta = ser.responder(entrada)
            print(f"\n{ser.identidade.nome}> {resposta}")

            if random.random() < _CHANCE_TENTATIVA:
                tentativa = ser.tentar_falar()
                if tentativa:
                    print(f"\n{ser.identidade.nome} tenta dizer algo por conta própria:")
                    print(f'  "{tentativa}"')
                    print("  (faz sentido? diga /sim ou /não -- ou apenas continue falando)")
    finally:
        salvar(ser)
        print(f"\n{ser.identidade.nome} guarda o que viveu e se cala, até a próxima vez.")


if __name__ == "__main__":
    executar()
