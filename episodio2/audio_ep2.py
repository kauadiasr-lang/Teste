#!/usr/bin/env python3
"""Trilha e efeitos sonoros sintetizados (numpy) + mixagem da narração."""
import wave
from pathlib import Path

import numpy as np

import roteiro as R

SR = 44100
rng = np.random.default_rng(7)
N = int(R.DUR * SR)
CHAVES = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.0, "A": 440.0, "B": 493.88}


def hz(nome, oit=4):
    base = CHAVES[nome[0]] * (2 ** (oit - 4))
    if len(nome) > 1:
        base *= 2 ** (1 / 12) if nome[1] == "#" else 2 ** (-1 / 12)
    return base


def t_(d):
    return np.arange(int(d * SR)) / SR


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def decay(d, a=0.004, tau=0.15):
    t = t_(d)
    return np.minimum(1, t / a) * np.exp(-t / tau)


def pluck(f, d=0.3, tau=0.12):
    t = t_(d)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t)) * decay(d, tau=tau)


def square(f, d=0.2, tau=0.1):
    t = t_(d)
    return lp(np.sign(np.sin(2 * np.pi * f * t)), 6) * decay(d, tau=tau) * 0.5


def tri(f, d=0.3, tau=0.2):
    t = t_(d)
    return (2 / np.pi * np.arcsin(np.sin(2 * np.pi * f * t))) * decay(d, tau=tau)


def noise(d):
    return rng.standard_normal(int(d * SR))


def add(buf, t0, sig, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i < 0:
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * g


def swish(d=0.25):
    x = noise(d)
    x = x - lp(x, 40)
    x = lp(x, 3)
    return x * np.sin(np.pi * np.linspace(0, 1, len(x))) ** 2 * 0.5


def thud(d=0.35, f0=130):
    t = t_(d)
    return np.sin(2 * np.pi * (f0 * np.exp(-t * 8) + 40) * t) * decay(d, tau=0.09) + lp(noise(d), 60) * decay(d, tau=0.04) * 1.2


def puff(d=0.9):
    x = lp(noise(d), 50) * 4
    t = t_(d)
    return x * np.minimum(1, t / 0.05) * np.exp(-t / 0.3)


def cough(d=0.4):
    t = t_(d)
    x = lp(noise(d), 5) * 3 * (np.exp(-t / 0.05) + 0.7 * np.exp(-((t - 0.16) / 0.04) ** 2))
    return x + np.sin(2 * np.pi * 210 * t) * np.exp(-t / 0.08) * 0.4


def pop(d=0.14):
    t = t_(d)
    return np.sin(2 * np.pi * (700 * np.exp(-t * 20) + 200) * t) * decay(d, tau=0.04)


def boing(d=0.5):
    t = t_(d)
    f = 220 + 260 * np.sin(np.pi * t / d) + 18 * np.sin(2 * np.pi * 22 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)


def scrape(d):
    x = lp(noise(d), 18) * 5
    t = t_(d)
    return x * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * np.minimum(1, t / 0.1)


def ding(f=1318, d=1.2):
    t = t_(d)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t / 0.35)


def trombone(f0, f1, d):
    t = t_(d)
    f = np.linspace(f0, f1, len(t)) * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)
    return lp(x, 4) * np.minimum(1, t / 0.04) * np.exp(-t / (d * 0.9)) * 0.7


def clatter(d=0.7):
    out = np.zeros(int(d * SR))
    for k, tt in enumerate([0, 0.12, 0.22, 0.31, 0.38]):
        add(out, tt, thud(0.2, 220 - 20 * k), 0.8 - 0.12 * k)
    return out


def coro(f, d):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * f * m * t * (1 + 0.004 * np.sin(2 * np.pi * 5 * t + m))) / m for m in (1, 2, 3))
    return x * np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 0.8)


def musica_motivacional(buf, a, b):
    beat = 60 / 126
    prog = [("C", ["C", "E", "G"]), ("G", ["G", "B", "D"]), ("A", ["A", "C", "E"]), ("F", ["F", "A", "C"])]
    k = 0
    t = a
    while t < b:
        raiz, acorde = prog[(k // 2) % 4]
        add(buf, t, square(hz(raiz, 2), 0.2), 0.16)
        for j in range(2):
            n = acorde[(k * 2 + j) % 3]
            add(buf, t + j * beat / 2, square(hz(n, 5 if j else 4), 0.18, 0.08), 0.1)
        add(buf, t + beat / 2, lp(noise(0.05), 2) * decay(0.05, tau=0.015), 0.05)
        t += beat
        k += 1
    add(buf, b, square(hz("C", 4), 0.4, 0.2) + square(hz("E", 4), 0.4, 0.2) + square(hz("G", 4), 0.4, 0.2), 0.12)


def musica_suspense(buf, a, b):
    beat = 60 / 92
    notas = ["C", "D#", "G", "F", "D#", "D", "C", "G"]
    k, t = 0, a
    while t < b:
        n = notas[k % len(notas)]
        add(buf, t, pluck(hz(n.replace("D#", "E").replace("E", "E") if False else n, 2 if k % 3 else 3), 0.3, 0.1), 0.22)
        if k % 4 == 2:
            add(buf, t + beat / 2, pluck(hz("A", 5), 0.2, 0.05), 0.05)
        t += beat
        k += 1


def musica_leve(buf, a, b):
    beat = 60 / 112
    prog = ["C", "A", "F", "G"]
    mel = [["E", "G", "C", "G"], ["C", "E", "A", "E"], ["A", "C", "F", "C"], ["B", "D", "G", "D"]]
    k, t = 0, a
    while t < b:
        bar = (k // 4) % 4
        add(buf, t, tri(hz(prog[bar], 2), 0.4, 0.2), 0.22)
        add(buf, t, tri(hz(mel[bar][k % 4], 5), 0.25, 0.12), 0.12)
        add(buf, t + beat / 2, lp(noise(0.05), 2) * decay(0.05, tau=0.02), 0.04)
        t += beat
        k += 1


def musica_final(buf, a, b):
    beat = 60 / 84
    notas = ["A", "A", "E", "G", "A", "C", "B", "E"]
    k, t = 0, a
    while t < b:
        add(buf, t, pluck(hz(notas[k % 8], 2), 0.5, 0.15), 0.25)
        if k % 2 == 1:
            add(buf, t + beat / 2, lp(noise(0.04), 3) * decay(0.04, tau=0.012), 0.08)
        t += beat
        k += 1


def main():
    here = Path(__file__).parent
    musica = np.zeros(N)
    sfx = np.zeros(N)
    # relógio de parede na cena 1 (silêncio constrangedor)
    for k in range(1, 8):
        add(musica, k + 0.3, pluck(1500, 0.05, 0.01), 0.06)
    musica_motivacional(musica, 8.2, 17.3)
    add(musica, T := R.T_BROCHE_TRISTE, trombone(233, 220, 0.5), 0.5)
    add(musica, T + 0.55, trombone(220, 208, 0.5), 0.5)
    add(musica, T + 1.1, trombone(208, 196, 0.5), 0.5)
    add(musica, T + 1.65, trombone(196, 147, 1.4), 0.5)
    musica_suspense(musica, 21.0, 31.0)
    for f in (hz("C", 4), hz("E", 4), hz("G", 4), hz("B", 4), hz("C", 5)):
        add(musica, R.T_RELIQUIA[0], coro(f, 6.4), 0.07)
    musica_suspense(musica, 38.6, 40.8)
    musica_leve(musica, 40.8, 53.6)
    add(musica, 53.6, trombone(262, 131, 1.2), 0.4)
    musica_final(musica, 60.0, 85.0)

    # efeitos sonoros
    add(sfx, R.T_POEIRA_VASSOURA, puff(0.6), 0.3)
    add(sfx, R.T_POEIRA_VASSOURA + 0.05, thud(0.15, 200), 0.25)
    for k in range(8):
        add(sfx, 9.1 + 0.9 * k, swish(0.3), 0.55)
    for ts in R.S2_ARREMESSOS + R.S4_ARREMESSOS:
        add(sfx, ts - 0.1, swish(0.4), 0.45)
        add(sfx, ts + 0.6 if ts in R.S2_ARREMESSOS else ts + 0.55, thud(0.2, 160) if ts in R.S2_ARREMESSOS else pop(), 0.6)
    add(sfx, 17.4, ding(1568, 0.9), 0.25)
    add(sfx, 20.5, clatter(), 0.6)
    d0, d1 = R.T_ARRASTA
    for a_, b_ in ((22.7, 23.3), (23.6, 24.2), (24.4, 25.6)):
        add(sfx, a_, scrape(b_ - a_), 0.55)
    add(sfx, R.T_REVELA, puff(1.6), 0.8)
    add(sfx, R.T_REVELA + 0.05, thud(0.4, 90), 0.7)
    for c in R.TOSSES:
        add(sfx, c, cough(0.45), 0.9)
    add(sfx, R.T_RELIQUIA[0], ding(1318, 1.6), 0.3)
    add(sfx, R.T_RELIQUIA[0] + 0.2, ding(1976, 1.6), 0.2)
    add(sfx, R.T_MEIA_CAI + 0.35, thud(0.15, 300), 0.25)
    add(sfx, R.T_VASSOURA_PEGA, scrape(0.3), 0.3)
    add(sfx, R.T_VASSOURA_CAI_2, clatter(), 0.55)
    add(sfx, R.T_PULO[0], boing(0.6), 0.45)
    add(sfx, R.T_SOFA, thud(0.5, 120), 1.0)
    add(sfx, R.T_SOFA + 0.02, puff(1.8), 0.9)
    for c in (56.5, 57.0):
        add(sfx, c, cough(0.4), 0.85)
    add(sfx, 58.4, trombone(110, 82, 1.2), 0.45)
    for tt, f in zip(R.T_OPCOES, (880, 1046, 1175)):
        add(sfx, tt, ding(f, 0.7), 0.3)
        add(sfx, tt, pop(), 0.4)

    # narração (24 kHz -> 44,1 kHz) e ducking da música
    voz = np.zeros(N)
    duck = np.ones(N)
    for t0, nome, _ in R.NARRACAO:
        with wave.open(str(here / "voz" / f"{nome}.wav")) as w:
            sr = w.getframerate()
            x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768
        idx = np.linspace(0, len(x) - 1, int(len(x) * SR / sr))
        y = np.interp(idx, np.arange(len(x)), x)
        add(voz, t0, y, 1.0)
        i0, i1 = int(t0 * SR), int((t0 + len(y) / SR) * SR)
        duck[i0:i1] = 0.35
    duck = lp(duck, int(0.3 * SR))
    mix = musica * duck * 0.9 + sfx * (0.55 + 0.25 * (1 - duck)) + voz * 1.25
    mix[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    mix[-int(0.7 * SR):] *= np.linspace(1, 0, int(0.7 * SR))
    pico = np.max(np.abs(mix))
    mix = mix / pico * 0.89
    pcm = (mix * 32767).astype("<i2")
    with wave.open(str(here / "audio.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("audio ok", round(pico, 2))


if __name__ == "__main__":
    main()
