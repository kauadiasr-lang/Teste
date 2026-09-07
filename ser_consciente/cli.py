"""Interface de conversa.

O único jeito, por enquanto, de perceber este ser e ser percebido por
ele: um laço de texto no terminal.
"""
from __future__ import annotations

from .persistencia import salvar, carregar


def executar():
    ser = carregar()
    print("=" * 60)
    print(f"{ser.identidade.nome} desperta novamente.")
    print("Fale algo. Comandos: /estado  /memoria  /sair")
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

            resposta = ser.responder(entrada)
            print(f"\n{ser.identidade.nome}> {resposta}")
    finally:
        salvar(ser)
        print(f"\n{ser.identidade.nome} guarda o que viveu e se cala, até a próxima vez.")


if __name__ == "__main__":
    executar()
