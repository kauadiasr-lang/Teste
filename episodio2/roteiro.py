"""Linha do tempo compartilhada entre imagem e áudio do episódio 2."""
import math

DUR = 86.0

# (início em s, arquivo da narração, texto)
NARRACAO = [
    (0.4, "n1", "Vocês decidiram que o Roberto deveria terminar de limpar a casa. "
                "Uma escolha simples. Afinal, o que poderia dar errado?"),
    (9.0, "n2", "Pela primeira vez em dois anos, Roberto demonstrou iniciativa. "
                "A casa, por sua vez, demonstrou resistência."),
    (26.4, "n3", "Ele descobriu que limpar a casa não era uma tarefa. "
                 "Era uma investigação arqueológica."),
    (44.0, "n4", "Depois de muito esforço, Roberto conseguiu uma conquista histórica: "
                 "agora a casa parecia habitada por uma pessoa, e não por um fenômeno climático."),
    (61.0, "n5", "Dia 2 de 15. A casa está quase limpa. Roberto está quase derrotado. "
                 "Mas ainda existe um problema..."),
    (74.0, "n6", "Comente 1 ou 2. A opção mais votada decide o próximo episódio."),
]

T_POEIRA_VASSOURA = 7.0   # montinho de poeira cai da vassoura
T_ARRASTA = (22.0, 25.6)  # Roberto puxa o armário
T_REVELA = 25.8           # nuvem de poeira atrás do armário
TOSSES = (26.9, 27.9, 28.9)
T_RELIQUIA = (32.4, 38.2)
T_MEIA_CAI = 39.0
S2_ARREMESSOS = [11.0, 13.2, 15.4]
S4_ARREMESSOS = [41.9 + 1.1 * i for i in range(9)]
T_VASSOURA_CAI_1 = 20.5
T_VASSOURA_PEGA = 41.0
T_VASSOURA_CAI_2 = 53.6
T_PULO = (55.2, 56.0)
T_SOFA = 56.0
T_OPCOES = (67.6, 68.9, 70.2)
T_BROCHE_TRISTE = 18.7


def xs2(t):
    """Posição horizontal de Roberto varrendo no episódio (cena 2)."""
    amp = max(0.0, min(1.0, (t - 8.4) / 1.2))
    return 540 + 130 * amp * math.sin(2 * math.pi * (t - 9) / 3.8)
