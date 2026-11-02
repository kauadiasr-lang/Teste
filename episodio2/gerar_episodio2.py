#!/usr/bin/env python3
"""Imagem do episódio 2 de "15 Dias Para Não Voltar Para o Interior".

Animação 2D desenhada quadro a quadro com Pillow, vertical 9:16.
Uso:
    gerar_episodio2.py video.mp4        # gera o vídeo completo (usa audio.wav ao lado)
    gerar_episodio2.py --teste 5 12 30  # salva quadros de teste nos instantes dados
"""
import math
import random
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import roteiro as R

W, H = 1080, 1920
OW, OH = 720, 1280
FPS = 24
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OUT = (40, 28, 38)
SKIN = (240, 190, 150)
SKIN_D = (222, 168, 128)
HAIR = (72, 46, 36)
SHIRT = (242, 188, 52)
PANTS = (104, 112, 134)
SLIPPER = (150, 96, 70)
WALL = (234, 208, 164)
WALL_D = (214, 184, 140)
FLOOR = (150, 100, 70)
FLOOR_L = (200, 146, 102)
WOOD = (166, 112, 72)
SOFA = (62, 128, 118)
SOFA_D = (46, 98, 92)

CAB_Y0, CAB_Y1, CAB_W = 640, 1290, 320
SOFA_X0, SOFA_X1 = 640, 1040
BAG = (300, 1640)
LYING_1 = (700, 1515)


# ---------------------------------------------------------------- utilidades
def ss(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def kf(t, pts):
    if t <= pts[0][0]:
        return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t < t1:
            return v0 + (v1 - v0) * ss((t - t0) / (t1 - t0))
    return pts[-1][1]


def lerp(a, b, u):
    return a + (b - a) * u


def font(sz):
    return ImageFont.truetype(BOLD, sz)


def ell(d, cx, cy, rx, ry, fill, out=OUT, w=7):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=out, width=w)


def rrect(d, x0, y0, x1, y1, r, fill, out=OUT, w=7):
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=out, width=w)


def thick(d, pts, w, col, ow=7):
    for c, ww in ((OUT, w + 2 * ow), (col, w)):
        d.line(pts, fill=c, width=int(ww), joint="curve")
        r = ww / 2
        for e in (pts[0], pts[-1]):
            d.ellipse([e[0] - r, e[1] - r, e[0] + r, e[1] + r], fill=c)


def ik(s, t, l1, l2, sign):
    dx, dy = t[0] - s[0], t[1] - s[1]
    dist = max(1.0, min(math.hypot(dx, dy), l1 + l2 - 1e-3))
    a = math.atan2(dy, dx)
    cb = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    b = math.acos(max(-1.0, min(1.0, cb)))
    ang = a + sign * b
    el = (s[0] + l1 * math.cos(ang), s[1] + l1 * math.sin(ang))
    return el, (s[0] + dist * math.cos(a), s[1] + dist * math.sin(a))


def layer_paint(img, color, fn):
    mask = Image.new("L", img.size, 0)
    fn(ImageDraw.Draw(mask))
    img.paste(color, (0, 0), mask)


# ------------------------------------------------------------------ cenário
def make_bg():
    img = Image.new("RGB", (W, H), WALL)
    d = ImageDraw.Draw(img)
    # parede com faixa mais escura em baixo
    d.rectangle([0, 900, W, 1290], fill=WALL_D)
    for x in range(0, W, 120):
        d.line([(x, 0), (x, 900)], fill=(226, 198, 154), width=3)
    # sujeira atrás do armário (revelada na cena 3)
    d.rectangle([40, CAB_Y0, 225, 1300], fill=(176, 160, 138))
    rng = random.Random(3)
    for _ in range(70):
        x, y = rng.randint(50, 215), rng.randint(CAB_Y0 + 20, 1290)
        r = rng.randint(8, 30)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(150 + rng.randint(-15, 10), 134, 112))
    # chão em perspectiva
    d.rectangle([0, 1290, W, H], fill=FLOOR)
    vp = (540, 700)
    for k in range(-14, 15):
        x1 = 540 + k * 230
        d.line([(vp[0] + (x1 - vp[0]) * 0.18, 1290), (x1, H)], fill=(128, 84, 58), width=4)
    y = 1290
    step = 40
    while y < H:
        d.line([(0, y), (W, y)], fill=(128, 84, 58), width=3)
        step *= 1.16
        y += step
    d.rectangle([0, 1262, W, 1296], fill=(110, 76, 56), outline=OUT, width=5)
    # janela
    rrect(d, 120, 280, 440, 720, 14, (150, 215, 240), w=9)
    d.line([(280, 280), (280, 720)], fill=OUT, width=9)
    d.line([(120, 500), (440, 500)], fill=OUT, width=9)
    ell(d, 200, 400, 36, 22, (255, 255, 255), out=(255, 255, 255), w=1)
    ell(d, 360, 380, 50, 26, (255, 255, 255), out=(255, 255, 255), w=1)
    d.polygon([(90, 270), (200, 270), (150, 730), (90, 730)], fill=(196, 92, 82), outline=OUT, width=6)
    d.polygon([(470, 270), (360, 270), (410, 730), (470, 730)], fill=(196, 92, 82), outline=OUT, width=6)
    # quadro torto
    d.polygon([(640, 330), (810, 300), (830, 470), (660, 500)], fill=(120, 80, 60), outline=OUT, width=7)
    d.polygon([(662, 350), (792, 326), (808, 452), (678, 476)], fill=(168, 205, 170), outline=OUT, width=5)
    d.polygon([(690, 450), (730, 390), (770, 440), (790, 420), (800, 452), (678, 476)], fill=(96, 150, 100))
    # teia no canto
    for k in range(5):
        a = math.radians(90 + k * 18)
        d.line([(W, 0), (W + 330 * math.cos(a) * 1.0, 330 * math.sin(a))], fill=(250, 245, 235), width=3)
    for r in (90, 170, 250):
        pts = [(W + r * math.cos(math.radians(90 + k * 18)), r * math.sin(math.radians(90 + k * 18)))
               for k in range(5)]
        d.line(pts, fill=(250, 245, 235), width=3)
    # sofá
    rrect(d, SOFA_X0, 960, SOFA_X1, 1260, 60, SOFA)
    rrect(d, SOFA_X0 - 30, 1090, SOFA_X0 + 70, 1350, 36, SOFA_D)
    rrect(d, SOFA_X1 - 70, 1090, SOFA_X1 + 30, 1350, 36, SOFA_D)
    rrect(d, SOFA_X0 + 60, 1190, SOFA_X1 - 60, 1340, 30, SOFA)
    d.line([(840, 1200), (840, 1330)], fill=OUT, width=5)
    d.rectangle([SOFA_X0 + 40, 1338, SOFA_X0 + 80, 1370], fill=OUT)
    d.rectangle([SOFA_X1 - 80, 1338, SOFA_X1 - 40, 1370], fill=OUT)
    # luz da janela no chão
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).polygon([(160, 1300), (420, 1300), (700, 1900), (60, 1900)], fill=40)
    img.paste((255, 240, 190), (0, 0), glow)
    return img


def make_pile():
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(fg)
    cols = [(200, 70, 70), (70, 100, 180), (236, 236, 232), (80, 150, 100), (242, 188, 52),
            (150, 80, 160), (60, 60, 70), (230, 130, 60)]
    rng = random.Random(11)
    for i in range(16):
        x = 900 + rng.randint(-120, 120) * (1 - i / 22)
        y = 1760 - i * 11 - rng.randint(0, 30)
        ell(d, x, y, rng.randint(70, 110), rng.randint(36, 56), cols[i % len(cols)], w=6)
    for x, y, ang, c in [(800, 1620, 20, (200, 70, 70)), (990, 1610, -25, (70, 100, 180)),
                         (880, 1560, 5, (236, 236, 232))]:
        a = math.radians(ang)
        thick(d, [(x, y), (x + 70 * math.cos(a), y - 30 + 50 * math.sin(a))], 38, c, 6)
    ell(d, 930, 1600, 60, 34, (80, 150, 100), w=6)
    sock(d, 1000, 1565, 0.55)
    return fg


def sock(d, x, y, sc=1.0, rot=0.0):
    pts = [(-22, -60), (22, -60), (22, 4), (52, 24), (50, 54), (-8, 54), (-22, 20)]
    c, s_ = math.cos(rot), math.sin(rot)
    pp = [(x + sc * (px * c - py * s_), y + sc * (px * s_ + py * c)) for px, py in pts]
    d.polygon(pp, fill=(236, 236, 232), outline=OUT, width=max(3, int(6 * sc)))
    for k in range(3):
        yy = -44 + k * 18
        a = (x + sc * (-22 * c - yy * s_), y + sc * (-22 * s_ + yy * c))
        b = (x + sc * (22 * c - yy * s_), y + sc * (22 * s_ + yy * c))
        d.line([a, b], fill=(210, 60, 60), width=max(3, int(7 * sc)))


# ---------------------------------------------------------------- objetos
def draw_item(d, kind, x, y):
    if kind == "book":
        rrect(d, x - 50, y - 18, x + 50, y + 18, 5, (190, 70, 70), w=6)
        d.line([(x - 50, y - 6), (x + 50, y - 6)], fill=(250, 240, 220), width=6)
    elif kind == "box":
        rrect(d, x - 55, y - 45, x + 55, y + 45, 6, (206, 160, 100), w=6)
        d.line([(x, y - 45), (x, y + 45)], fill=(236, 220, 180), width=14)
    elif kind == "bottle":
        rrect(d, x - 20, y - 8, x + 20, y + 52, 12, (90, 170, 120), w=6)
        rrect(d, x - 9, y - 50, x + 9, y - 6, 4, (90, 170, 120), w=6)
    elif kind == "can":
        rrect(d, x - 24, y - 34, x + 24, y + 34, 8, (200, 70, 60), w=6)
        d.line([(x - 24, y - 12), (x + 24, y - 12)], fill=(240, 230, 220), width=6)
    elif kind == "paper":
        d.polygon([(x - 38, y - 30), (x + 34, y - 40), (x + 44, y + 28), (x - 30, y + 38)],
                  fill=(250, 248, 240), outline=OUT, width=5)
        d.line([(x - 22, y - 12), (x + 26, y - 18)], fill=(150, 150, 160), width=4)
        d.line([(x - 20, y + 8), (x + 28, y + 2)], fill=(150, 150, 160), width=4)
    elif kind == "pizza":
        d.polygon([(x - 60, y - 30), (x + 60, y - 36), (x + 64, y + 30), (x - 56, y + 36)],
                  fill=(222, 178, 110), outline=OUT, width=6)
        ell(d, x, y, 18, 14, (200, 60, 50), w=4)


S2_ITEMS = ["book", "box", "bottle"]
S4_ITEMS = ["can", "paper", "box", "bottle", "pizza", "paper", "can", "bottle", "paper"]


def cab_off(t):
    return kf(t, [(22.0, 0), (22.7, 0), (23.1, 60), (23.4, 55), (24.0, 120), (24.3, 114), (25.6, 180)])


def xs4(t):
    return 560 + 250 * math.sin(2 * math.pi * (t - 41) / 9.0) * ss((t - 41) / 1.2)


def build_items():
    items = []
    for i, (k, ts) in enumerate(zip(S2_ITEMS, R.S2_ARREMESSOS)):
        sx = R.xs2(ts) + (-120 if i % 2 == 0 else 120)
        items.append(dict(kind=k, src=(sx, 1560 + 20 * i), dst=(70 + 100 * i, CAB_Y0 - 30),
                          ts=ts, te=ts + 0.7, cab=True, arc=300))
    rng = random.Random(5)
    for i, (k, ts) in enumerate(zip(S4_ITEMS, R.S4_ARREMESSOS)):
        sx = max(90, min(720, xs4(ts) + rng.choice([-110, 110])))
        items.append(dict(kind=k, src=(sx, 1740 + rng.randint(0, 90)), dst=BAG,
                          ts=ts, te=ts + 0.6, cab=False, arc=340))
    return items


ITEMS = build_items()


def item_pos(it, t):
    if t < it["ts"]:
        return it["src"]
    if t < it["te"]:
        u = (t - it["ts"]) / (it["te"] - it["ts"])
        if it["cab"]:
            dx, dy = 40 + cab_off(t) + it["dst"][0], it["dst"][1]
        else:
            dx, dy = it["dst"]
        return (lerp(it["src"][0], dx, u), lerp(it["src"][1], dy, u) - it["arc"] * math.sin(math.pi * u))
    if it["cab"]:
        return (40 + cab_off(t) + it["dst"][0], it["dst"][1])
    return None


# ----------------------------------------------------------------- Roberto
EXPR = {
    "deadpan": dict(open=0.85, lid=0.35, brow=(0, 0), mouth="flat"),
    "determined": dict(open=1.0, lid=0.0, brow=(16, -4), mouth="grin"),
    "proud": dict(open=0.7, lid=0.25, brow=(-4, -12), mouth="smile"),
    "strain": dict(open=0.5, lid=0.4, brow=(20, 0), mouth="grit"),
    "cough": dict(open=0.35, lid=0.5, brow=(14, 4), mouth="open"),
    "awe": dict(open=1.25, lid=0.0, brow=(-8, -20), mouth="o"),
    "tired": dict(open=0.7, lid=0.55, brow=(-10, 6), mouth="frown"),
    "happy": dict(open=0.6, lid=0.3, brow=(-4, -8), mouth="smile"),
    "stare": dict(open=1.0, lid=0.0, brow=(0, -6), mouth="flat"),
    "dread": dict(open=1.1, lid=0.1, brow=(-16, -14), mouth="wavy"),
}


def rob(t):
    s = dict(x=540, fy=1500, hipy=None, lean=0.0, bob=0.0, expr="deadpan", look=(0, 0), sweat=False,
             hl=None, hr=None, gx=110, sit=False, broom_held=False, cough=0.0, sock=None)
    if t < 8:
        s.update(broom_held=True, bob=4 * math.sin(t * 2.2))
        s["look"] = (kf(t, [(0, 0), (1.2, 0), (1.8, -1), (3, -1), (3.6, 1), (4.8, 1), (5.4, 0)]),
                     kf(t, [(0, 0), (4.9, 0), (5.5, 1), (8, 1)]))
        if 6.5 <= t < 7.2:
            s["gx"] = 110 + 28 * math.sin((t - 6.5) * 38) * (1 - (t - 6.5) / 0.7)
    elif t < 20.5:
        s["broom_held"] = True
        p = (t - 9) / 0.9
        amp = ss((t - 8.5) / 1.0)
        gx2 = 170 * amp * math.sin(2 * math.pi * p) if t >= 9 else 110
        s["expr"] = "determined" if t < 17.0 else ("proud" if t < 19.2 else "deadpan")
        if t < 17.0:
            s["x"] = R.xs2(t)
            s["gx"] = gx2
            s["lean"] = gx2 * 0.12
            s["bob"] = -14 * abs(math.sin(math.pi * p)) if t >= 9 else 0
        else:
            s["x"] = kf(t, [(17.0, R.xs2(17.0)), (18.5, 540)])
            s["gx"] = 130 + (gx2 - 130) * (1 - ss((t - 17.0) / 0.6))
            s["bob"] = 5 * math.sin(t * 3)
            if t < 19.2:
                s["hr"] = (s["x"] + 100, s["fy"] - 250)
        for ts in R.S2_ARREMESSOS:
            if ts - 0.3 <= t <= ts + 0.25:
                s["hr"] = (s["x"] - 120, s["fy"] - 640)
        s["look"] = (kf(t, [(19.0, 0), (19.5, 1), (20.0, -1), (20.5, 0)]), 0.3 if t > 19 else 0)
    elif t < 41.0:
        s = rob_s3(t, s)
    elif t < 53.6:
        s["broom_held"] = True
        s["x"] = xs4(t)
        p = (t - 41) / 0.8
        amp = ss((t - 41) / 0.8)
        s["gx"] = 140 * amp * math.sin(2 * math.pi * p)
        s["lean"] = s["gx"] * 0.1
        s["bob"] = -10 * abs(math.sin(math.pi * p)) * amp
        s["expr"] = "determined" if t < 47 else ("tired" if t < 51.5 else "happy")
        s["sweat"] = 47 <= t
        for ts in R.S4_ARREMESSOS:
            if ts - 0.3 <= t <= ts + 0.2:
                s["hr"] = (s["x"] - 100, s["fy"] - 560)
        if t >= 51.5:
            s["hr"] = (s["x"] + 100, s["fy"] - 250)
    elif t < 55.2:
        s["x"] = kf(t, [(54.0, xs4(53.6)), (55.2, 790)])
        s["fy"] = kf(t, [(54.0, 1500), (55.2, 1470)])
        s["expr"] = "tired"
        s["sweat"] = True
        s["look"] = (0.8, 0.0)
        s["bob"] = 6 * math.sin(t * 7)
    elif t < R.T_SOFA:
        u = (t - 55.2) / (R.T_SOFA - 55.2)
        s["x"] = lerp(790, 830, ss(u))
        s["fy"] = 1470 - 230 * math.sin(math.pi * u)
        s["expr"] = "happy"
        s["hl"] = (s["x"] - 150, s["fy"] - 520)
        s["hr"] = (s["x"] + 150, s["fy"] - 520)
    else:
        s = rob_sit(t, s)
    return s


def rob_s3(t, s):
    """Cena 3 (puxa o armário, tosse, relíquia) e a volta até a vassoura."""
    s["sock"] = None
    if t < 20.6:
        s["broom_held"] = t < R.T_VASSOURA_CAI_1
        s["expr"] = "deadpan"
        s["x"] = 540
    elif t < 22.0:
        s["x"] = kf(t, [(20.6, 540), (22.0, 440)])
        s["fy"] = kf(t, [(20.6, 1500), (22.0, 1430)])
        s["expr"] = "determined"
        s["bob"] = 6 * math.sin(t * 9)
    elif t < 25.6:
        off = cab_off(t)
        s["x"], s["fy"] = 440 + off, 1430
        s["lean"] = 25
        s["expr"] = "strain"
        s["sweat"] = True
        cab_r = 360 + off
        s["hl"], s["hr"] = (cab_r - 4, 1040), (cab_r - 4, 1130)
        s["bob"] = 5 * math.sin(t * 20)
    elif t < 31.0:
        s["x"], s["fy"] = 620, 1430
        s["expr"] = "awe" if t < 26.4 else "cough"
        jerk = sum(math.exp(-(t - c) * 6) * math.sin((t - c) * 26) for c in R.TOSSES if t >= c)
        s["lean"] = 18 * jerk
        s["bob"] = 8 * abs(jerk)
        s["cough"] = jerk
        if t >= 26.4:
            s["hl"] = (s["x"] - 8, s["fy"] - 470)
            s["hr"] = (s["x"] + 130 + 30 * math.sin(t * 14), s["fy"] - 500)
        s["look"] = (0, 0.4)
    elif t < 39.4:
        s["x"] = kf(t, [(31.0, 620), (32.0, 262)])
        s["fy"] = 1430
        s["hl"] = (s["x"] - 110, s["fy"] - 240)
        if t < 31.6:
            s["expr"] = "tired"
            s["bob"] = 5 * math.sin(t * 9)
        elif t < 32.4:
            s["expr"] = "awe"
            s["hr"] = (170, 1270)
            s["lean"] = -30 * ss((t - 31.6) / 0.5)
        elif t < 38.6:
            s["expr"] = "awe"
            u = ss((t - 32.4) / 1.0)
            s["hr"] = (lerp(170, s["x"] + 40, u), lerp(1270, s["fy"] - 730, u) + 6 * math.sin(t * 4) * u)
            s["look"] = (0.2, -1)
            s["sock"] = "hand"
        else:
            s["expr"] = "deadpan"
            u = ss((t - 38.6) / 0.6)
            s["hr"] = (s["x"] + 40, lerp(s["fy"] - 730, s["fy"] - 250, u))
            s["sock"] = "hand" if t < R.T_MEIA_CAI else None
            s["look"] = (0, 0)
    else:
        s["x"] = kf(t, [(39.4, 262), (41.0, 570)])
        s["fy"] = kf(t, [(39.4, 1430), (41.0, 1500)])
        s["expr"] = "determined"
        s["bob"] = 6 * math.sin(t * 9)
    if t >= R.T_MEIA_CAI and t < 39.4:
        s["sock"] = None
    return s


def rob_sit(t, s):
    s["sit"] = True
    s["x"] = 830
    s["hipy"] = 1215
    u = t - R.T_SOFA
    s["bob"] = -24 * math.exp(-u * 4.5) * math.cos(u * 16) if u < 1.8 else 4 * math.sin(t * 1.8)
    if t < 57.6:
        s["expr"] = "cough"
        jerk = sum(math.exp(-(t - c) * 6) * math.sin((t - c) * 26) for c in (56.5, 57.0) if t >= c)
        s["lean"] = 14 * jerk
        s["cough"] = jerk
        s["hl"] = (s["x"] - 10, s["hipy"] - 470)
        s["hr"] = (s["x"] + 150 + 25 * math.sin(t * 12), s["hipy"] - 380)
        s["look"] = (0, 0.6)
    elif t < 62.6:
        s["expr"] = "deadpan"
        s["look"] = (kf(t, [(57.6, 0), (58.4, 0), (59.2, 0)]), kf(t, [(57.6, 0.6), (59.2, 0)]))
    else:
        s["expr"] = "stare" if t < 63.0 else "dread"
        s["look"] = (kf(t, [(62.6, 0), (64.0, 0.45)]), kf(t, [(62.6, 0), (64.0, 1.0)]))
        s["sweat"] = t > 66
        if t > 80:
            s["bob"] = 7 * math.sin((t - 80) * 1.6)
    return s


# ------------------------------------------------------------- desenho Roberto
def broom_geom(t):
    """(G, u, comprimento, modo): ponto no chão, direção do cabo, e se está na mão."""
    def held(tt):
        r = rob(tt)
        g = (r["x"] + r["gx"], r["fy"] + 15)
        anchor = (r["x"] + 70 + r["lean"], r["fy"] - 320 + r["bob"])
        dx, dy = anchor[0] - g[0], anchor[1] - g[1]
        n = math.hypot(dx, dy)
        return g, (dx / n, dy / n), n, anchor

    def lying(g):
        return g, (-1.0, -0.04)

    def blend(g0, u0, g1, u1, k):
        a0, a1 = math.atan2(u0[1], u0[0]), math.atan2(u1[1], u1[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        a = a0 + da * k
        return (lerp(g0[0], g1[0], k), lerp(g0[1], g1[1], k)), (math.cos(a), math.sin(a))

    c1, c2 = R.T_VASSOURA_CAI_1, R.T_VASSOURA_CAI_2
    if t < c1 or R.T_VASSOURA_PEGA + 0.4 <= t < c2:
        g, u, n, anchor = held(t)
        return g, u, 560, "mao", anchor, n
    if c1 <= t < c1 + 0.45:
        g0, u0, _, _ = held(c1)
        g, u = blend(g0, u0, *lying(LYING_1), ss((t - c1) / 0.45))
        return g, u, 560, "solta", None, 0
    if t < R.T_VASSOURA_PEGA:
        return LYING_1, (-1.0, -0.04), 560, "chao", None, 0
    if t < R.T_VASSOURA_PEGA + 0.4:
        g1, u1, _, _ = held(R.T_VASSOURA_PEGA + 0.4)
        g, u = blend(LYING_1, (-1.0, -0.04), g1, u1, ss((t - R.T_VASSOURA_PEGA) / 0.4))
        return g, u, 560, "solta", None, 0
    g0, u0, _, _ = held(c2)
    lg = (g0[0], 1530)
    if t < c2 + 0.45:
        g, u = blend(g0, u0, lg, (-1.0, -0.04), ss((t - c2) / 0.45))
        return g, u, 560, "solta", None, 0
    return lg, (-1.0, -0.04), 560, "chao", None, 0


def draw_broom(d, g, u, length):
    n = (-u[1], u[0])
    top = (g[0] + u[0] * length, g[1] + u[1] * length)
    thick(d, [g, top], 20, (176, 128, 80), ow=5)
    base = [(g[0] - n[0] * 78, g[1] - n[1] * 78), (g[0] + n[0] * 78, g[1] + n[1] * 78),
            (g[0] + u[0] * 100 + n[0] * 34, g[1] + u[1] * 100 + n[1] * 34),
            (g[0] + u[0] * 100 - n[0] * 34, g[1] + u[1] * 100 - n[1] * 34)]
    d.polygon(base, fill=(176, 154, 104), outline=OUT, width=6)
    for k in range(-3, 4):
        a = (g[0] + n[0] * k * 20, g[1] + n[1] * k * 20)
        b = (a[0] + u[0] * 60, a[1] + u[1] * 60)
        d.line([a, b], fill=(120, 104, 70), width=4)
    # poeira acumulada nas cerdas
    ell(d, g[0] + u[0] * 70, g[1] + u[1] * 70, 42, 18, (170, 168, 164), out=(120, 118, 114), w=3)


def arms_geom(s, hands):
    x, lean = s["x"], s["lean"]
    hip = s["hipy"] if s["hipy"] else s["fy"] - 240
    hip += s["bob"]
    sy = hip - 180
    sl = (x - 88 + lean, sy + 24)
    sr = (x + 88 + lean, sy + 24)
    hl, hr = hands
    el, hl = ik(sl, hl, 150, 150, 1)
    er, hr = ik(sr, hr, 150, 150, -1)
    return sl, el, hl, sr, er, hr


def default_hands(s):
    x, lean = s["x"], s["lean"]
    hip = (s["hipy"] if s["hipy"] else s["fy"] - 240) + s["bob"]
    if s["sit"]:
        return (x - 110, hip + 40), (x + 110, hip + 40)
    sw = 14 * math.sin(s["x"] * 0.06)
    return (x - 110 + lean, hip - 40 + sw), (x + 110 + lean, hip - 40 - sw)


def draw_face(d, cx, cy, s, t):
    e = EXPR[s["expr"]]
    for ex in (-1, 1):
        ecx, ecy = cx + ex * 42, cy - 14
        rx, ry = 29, 34 * e["open"]
        ell(d, ecx, ecy, rx, ry, (255, 255, 255), w=5)
        px = ecx + s["look"][0] * 12
        py = ecy + s["look"][1] * min(12, ry * 0.5)
        d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=OUT)
        d.ellipse([px - 4, py - 7, px + 1, py - 2], fill=(255, 255, 255))
        if e["lid"] > 0:
            ly = ecy - ry + 2 * ry * e["lid"]
            d.rectangle([ecx - rx + 2, ecy - ry - 3, ecx + rx - 2, ly], fill=SKIN)
            d.line([(ecx - rx, ly), (ecx + rx, ly)], fill=OUT, width=6)
        tilt, rise = e["brow"]
        by = cy - 78 + rise
        outer = (cx + ex * 76, by - tilt * 0.5)
        inner = (cx + ex * 14, by + tilt * 0.5)
        d.line([outer, inner], fill=HAIR, width=14)
    ell(d, cx, cy + 22, 14, 11, SKIN_D, w=5)
    my = cy + 68
    m = e["mouth"]
    shake = 5 * math.sin(t * 40) if s["cough"] else 0
    if m == "flat":
        d.line([(cx - 28, my), (cx + 28, my - 3)], fill=OUT, width=8)
    elif m == "smile":
        d.chord([cx - 42, my - 34, cx + 42, my + 30], 0, 180, fill=(120, 40, 50), outline=OUT, width=6)
    elif m == "grin":
        d.chord([cx - 50, my - 36, cx + 50, my + 36], 0, 180, fill=(250, 250, 250), outline=OUT, width=6)
        d.line([(cx - 48, my), (cx + 48, my)], fill=OUT, width=5)
    elif m == "grit":
        rrect(d, cx - 36, my - 14, cx + 36, my + 16, 8, (250, 250, 250), w=6)
        d.line([(cx, my - 14), (cx, my + 16)], fill=OUT, width=4)
    elif m == "open":
        ell(d, cx + shake, my + 8, 26, 32 + 4 * abs(shake), (110, 30, 40), w=6)
        ell(d, cx + shake, my + 24, 16, 10, (220, 90, 100), out=(220, 90, 100), w=1)
    elif m == "o":
        ell(d, cx, my + 6, 16, 22, (110, 30, 40), w=6)
    elif m == "frown":
        d.arc([cx - 32, my - 4, cx + 32, my + 44], 200, 340, fill=OUT, width=8)
    elif m == "wavy":
        pts = [(cx - 34 + k * 17, my + (6 if k % 2 else -6)) for k in range(5)]
        d.line(pts, fill=OUT, width=7, joint="curve")
    if s["sweat"]:
        dx, dy = cx + 106, cy - 60 + (t * 30) % 40
        d.polygon([(dx, dy - 26), (dx - 14, dy + 6), (dx, dy + 18), (dx + 14, dy + 6)],
                  fill=(150, 210, 250), outline=OUT, width=4)


def draw_head(d, cx, cy, s, t):
    ell(d, cx - 104, cy + 6, 20, 28, SKIN)
    ell(d, cx + 104, cy + 6, 20, 28, SKIN)
    ell(d, cx, cy, 105, 112, SKIN)
    rng = random.Random(2)
    for _ in range(26):
        a = rng.uniform(0.15, math.pi - 0.15)
        r = rng.uniform(60, 98)
        px, py = cx + r * math.cos(a), cy + 30 + r * 0.8 * math.sin(a)
        if py > cy + 38:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(120, 90, 76))
    d.chord([cx - 112, cy - 124, cx + 112, cy + 112], 196, 344, fill=HAIR, outline=OUT, width=6)
    for k, (ox, oy, hh) in enumerate([(-80, -96, 50), (-40, -118, 62), (0, -124, 56), (44, -118, 64), (84, -92, 48)]):
        d.polygon([(cx + ox - 22, cy + oy + 22), (cx + ox + 4 + (k - 2) * 4, cy + oy - hh), (cx + ox + 26, cy + oy + 22)],
                  fill=HAIR, outline=OUT, width=5)
    draw_face(d, cx, cy, s, t)


def draw_rob(img, d, s, t):
    x, fy, lean = s["x"], s["fy"], s["lean"]
    bob = s["bob"]
    sit = s["sit"]
    hip = (s["hipy"] if sit else fy - 240) + bob
    sy = hip - 180
    hy = sy - 118
    # pernas
    v = 0.0
    if not sit:
        v = abs(rob(t + 0.04)["x"] - rob(t - 0.04)["x"]) / 0.08
        amp = min(1.0, v / 160)
        ph = (x * 0.045)
        for side in (-1, 1):
            w = math.sin(ph + (0 if side < 0 else math.pi))
            fx = x + side * 52 + w * 46 * amp
            ffy = fy - max(0.0, w) * 34 * amp
            thick(d, [(x + side * 46, hip + 10), (fx, ffy - 14)], 46, PANTS)
            ell(d, fx + side * 8, ffy - 4, 44, 22, SLIPPER, w=6)
    else:
        for side in (-1, 1):
            ell(d, x + side * 62, hip + 24, 62, 44, PANTS)
            thick(d, [(x + side * 66, hip + 50), (x + side * 70, hip + 190)], 46, PANTS)
            ell(d, x + side * 76, hip + 226, 44, 22, SLIPPER, w=6)
    # tronco
    rrect(d, x - 104 + lean * 0.5, sy - 10, x + 104 + lean * 0.5, hip + 34, 64, SHIRT)
    d.arc([x - 38 + lean, sy - 4, x + 38 + lean, sy + 50], 20, 160, fill=OUT, width=6)
    d.line([(x - 40, sy + 150), (x + 30, sy + 140)], fill=(214, 160, 36), width=5)
    # cabeça
    draw_head(d, x + lean, hy, s, t)
    # vassoura na mão
    g, u, length, mode, anchor, n = broom_geom(t)
    held = s["broom_held"] and mode == "mao"
    hands = list(default_hands(s))
    if held:
        hands[0] = anchor
        hands[1] = (g[0] + u[0] * n * 0.5, g[1] + u[1] * n * 0.5)
        # mão livre/override
        if s["hl"]:
            hands[0] = s["hl"]
        if s["hr"]:
            hands[1] = s["hr"]
            hands[0] = anchor
    else:
        if s["hl"]:
            hands[0] = s["hl"]
        if s["hr"]:
            hands[1] = s["hr"]
    if mode == "mao" and s["broom_held"]:
        draw_broom(d, g, u, length)
    sl, el, hl, sr, er, hr = arms_geom(s, tuple(hands))
    thick(d, [sl, el, hl], 40, SKIN if False else SHIRT, ow=7)
    # antebraço pele
    for a, b in ((el, hl), (er, hr)):
        pass
    thick(d, [sr, er, hr], 40, SHIRT, ow=7)
    for e_, h_ in ((el, hl), (er, hr)):
        thick(d, [((e_[0] * 2 + h_[0]) / 3, (e_[1] * 2 + h_[1]) / 3), h_], 34, SKIN, ow=6)
        ell(d, h_[0], h_[1], 28, 28, SKIN, w=6)
    return hl, hr


# ----------------------------------------------------------------- efeitos
PUFFS = []


def build_puffs():
    P = PUFFS
    P.append((R.T_POEIRA_VASSOURA, 650, 1520, 10, 70, 1.4))
    for k in range(8):
        t0 = 9.45 + 0.9 * k
        g = broom_geom(t0)[0]
        P.append((t0, g[0], g[1], 5, 60, 0.9))
    P.append((R.T_REVELA, 130, 1190, 46, 190, 2.4))
    P.append((R.T_MEIA_CAI, 300, 1440, 8, 60, 1.0))
    for k in range(12):
        t0 = 41.4 + 0.8 * k
        g = broom_geom(t0)[0]
        P.append((t0, g[0], g[1], 4, 55, 0.8))
    P.append((R.T_SOFA, 830, 1200, 70, 250, 2.6))


def draw_puffs(img, t):
    def fn(m):
        for i, (t0, x, y, n, spread, life) in enumerate(PUFFS):
            age = t - t0
            if age < 0 or age > life:
                continue
            rng = random.Random(i * 100)
            for k in range(n):
                th = rng.uniform(-math.pi * 0.97, -math.pi * 0.03)
                dist = spread * (1 - math.exp(-age * 1.7)) * rng.uniform(0.4, 1.0)
                px = x + math.cos(th) * dist * 1.1
                py = y + math.sin(th) * dist - 34 * age * rng.uniform(0.5, 1.2)
                r = (22 + 44 * math.sqrt(age)) * rng.uniform(0.7, 1.2)
                a = 150 * (1 - age / life) ** 1.2 * min(1.0, age / 0.08)
                m.ellipse([px - r, py - r, px + r, py + r], fill=int(a))
    layer_paint(img, (176, 162, 142), fn)


def star(d, x, y, r, fill):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.3
        a = math.radians(k * 45 - 90)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def draw_sparkles(d, cx, cy, t, n, rad, cols=((255, 250, 200), (255, 255, 255))):
    for k in range(n):
        rng = random.Random(k)
        a = rng.uniform(0, 6.28)
        r = rng.uniform(0.3, 1.0) * rad
        ph = (t * 1.6 + rng.random()) % 1.0
        size = 26 * math.sin(math.pi * ph)
        if size > 2:
            star(d, cx + r * math.cos(a), cy + r * math.sin(a) * 0.7, size, cols[k % 2])


def draw_relic(img, d, pos, t):
    k = ss((t - R.T_RELIQUIA[0]) / 0.8) * (1 - ss((t - R.T_RELIQUIA[1] + 0.6) / 0.6))
    if k <= 0:
        return
    rot = t * 0.35

    def rays(m):
        for i in range(12):
            a = rot + i * math.pi / 6
            w = 0.1
            pts = [pos, (pos[0] + 1400 * math.cos(a - w), pos[1] + 1400 * math.sin(a - w)),
                   (pos[0] + 1400 * math.cos(a + w), pos[1] + 1400 * math.sin(a + w))]
            m.polygon(pts, fill=int(85 * k))
        for r, a in ((200, 60), (130, 90), (70, 120)):
            m.ellipse([pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r], fill=int(a * k))
    layer_paint(img, (255, 232, 140), rays)
    draw_sparkles(d, pos[0], pos[1], t, 14, 190)


# ------------------------------------------------------------ cenário dinâmico
MARKS = []


def build_marks():
    rng = random.Random(9)
    for _ in range(18):
        MARKS.append((rng.randint(60, 1020), rng.randint(1380, 1880), rng.randint(40, 90)))
    for _ in range(9):
        MARKS.append((rng.randint(60, 1020), rng.randint(1380, 1860), -1))  # bolinhas de poeira


def patch_dims(t):
    rx = 300 * ss((t - 8.6) / 8.6) if t < 41.5 else 300 + 470 * ss((t - 42) / 10)
    if t < 8.6:
        rx = 0
    return rx, rx * 0.42


def inside_patch(x, y, rx, ry):
    return rx > 0 and ((x - 540) / rx) ** 2 + ((y - 1590) / max(ry, 1)) ** 2 < 1.0


def draw_floor_state(img, d, t):
    rx, ry = patch_dims(t)

    def fn(m):
        for x, y, r in MARKS:
            if r > 0 and not inside_patch(x, y, rx, ry):
                m.ellipse([x - r * 1.4, y - r * 0.5, x + r * 1.4, y + r * 0.5], fill=70)
    layer_paint(img, (88, 66, 52), fn)
    for x, y, r in MARKS:
        if r < 0 and not inside_patch(x, y, rx, ry):
            for dx, dy, rr in ((0, 0, 20), (22, -4, 15), (-20, 4, 13)):
                ell(d, x + dx, y + dy, rr, rr * 0.7, (178, 174, 168), out=(130, 126, 120), w=3)
    if rx > 4:
        d.ellipse([540 - rx, 1590 - ry, 540 + rx, 1590 + ry], fill=FLOOR_L)
        d.ellipse([540 - rx * 0.92, 1590 - ry * 0.9, 540 + rx * 0.92, 1590 + ry * 0.9], outline=(224, 170, 126), width=5)
        if 17.0 < t < 20.4 or 51.8 < t < 54.4:
            draw_sparkles(d, 540, 1590, t, 10, rx * 0.8)


def draw_cabinet(d, t):
    x0 = 40 + cab_off(t)
    rrect(d, x0, CAB_Y0, x0 + CAB_W, CAB_Y1, 14, WOOD)
    rrect(d, x0 + 18, CAB_Y0 + 60, x0 + CAB_W // 2 - 4, CAB_Y1 - 30, 8, (186, 130, 86), w=5)
    rrect(d, x0 + CAB_W // 2 + 4, CAB_Y0 + 60, x0 + CAB_W - 18, CAB_Y1 - 30, 8, (186, 130, 86), w=5)
    ell(d, x0 + CAB_W // 2 - 20, 980, 10, 10, (60, 40, 30), w=3)
    ell(d, x0 + CAB_W // 2 + 20, 980, 10, 10, (60, 40, 30), w=3)
    d.rectangle([x0 + 4, CAB_Y0 - 10, x0 + CAB_W - 4, CAB_Y0 + 8], fill=(190, 186, 178))  # poeira no topo
    d.rectangle([x0, CAB_Y0, x0 + CAB_W, CAB_Y0 + 3], fill=OUT)


def draw_reveal_things(d, t):
    """Objetos esquecidos atrás do armário (recibo, moeda) e a meia."""
    d.polygon([(70, 1262), (112, 1252), (122, 1290), (80, 1298)], fill=(250, 248, 240), outline=OUT, width=4)
    d.line([(82, 1268), (110, 1262)], fill=(150, 150, 160), width=3)
    ell(d, 205, 1280, 14, 10, (230, 190, 70), w=4)


def draw_bag(d, t):
    if t < 40.7 or t > 70:
        return
    n = sum(1 for it in ITEMS if not it["cab"] and t >= it["te"])
    pop = ss((t - 40.7) / 0.25)
    sc = (1 + 0.025 * n) * pop
    x, y = BAG
    w, h = 90 * sc, 120 * sc
    d.polygon([(x - w, y + 40), (x - w * 0.7, y - h), (x + w * 0.7, y - h), (x + w, y + 40)],
              fill=(40, 44, 56), outline=OUT, width=6)
    ell(d, x, y + 40, w, 26 * sc, (40, 44, 56), w=6)
    ell(d, x, y - h, w * 0.5, 22 * sc, (70, 74, 88), w=5)
    d.polygon([(x - 12, y - h - 10), (x - 30, y - h - 50), (x + 6, y - h - 24), (x + 32, y - h - 52), (x + 14, y - h - 8)],
              fill=(40, 44, 56), outline=OUT, width=4)


# ------------------------------------------------------------------- câmera
def cam(t):
    if t < 8.6:
        s = kf(t, [(0, 1.0), (4, 1.0), (6.6, 1.35), (8.6, 1.4)])
        return s, 540, kf(t, [(0, 960), (4, 960), (6.6, 1150)])
    if t < 17.0:
        return 1.45, 540 + (R.xs2(t) - 540) * 0.6, 1250
    if t < 22:
        s = kf(t, [(17.0, 1.45), (19.4, 1.0)])
        return s, kf(t, [(17.0, 540), (19.4, 540)]), kf(t, [(17.0, 1250), (19.4, 960), (21.5, 960)])
    if t < 32.4:
        s = kf(t, [(21.5, 1.0), (24, 1.2), (26, 1.25), (31, 1.25), (32.4, 1.7)])
        cx = kf(t, [(21.5, 540), (24, 400), (26, 350), (31, 350), (32.4, 260)])
        cy = kf(t, [(21.5, 960), (24, 1150), (26, 1150), (31, 1150), (32.4, 1000)])
        return s, cx, cy
    if t < 54.5:
        s = kf(t, [(32.4, 1.7), (38, 1.7), (40.2, 1.0)])
        cx = kf(t, [(32.4, 260), (38, 260), (40.2, 540)])
        cy = kf(t, [(32.4, 1000), (38, 950), (40.2, 960)])
        return s, cx, cy
    s = kf(t, [(54.5, 1.0), (56.5, 1.25), (62, 1.3), (67, 1.15), (86, 1.15)])
    cx = kf(t, [(54.5, 540), (56.5, 810), (62, 830), (67, 800)])
    cy = kf(t, [(54.5, 960), (56.5, 1250), (62, 1180), (67, 930), (86, 930)])
    return s, cx, cy


# --------------------------------------------------------------- legendas
def build_cues():
    cues = []
    from wave import open as wopen
    for t0, nome, texto in R.NARRACAO:
        with wopen(str(Path(__file__).parent / "voz" / f"{nome}.wav")) as w:
            dur = w.getnframes() / w.getframerate()
        palavras = texto.split()
        grupos, cur = [], []
        for p in palavras:
            cur.append(p)
            if len(cur) >= 5 or p[-1] in ".?:":
                grupos.append(" ".join(cur))
                cur = []
        if cur:
            grupos.append(" ".join(cur))
        pesos = [len(g) + 6 for g in grupos]
        total = sum(pesos)
        a = t0
        for g, p in zip(grupos, pesos):
            b = a + dur * p / total
            cues.append((a, b, g))
            a = b
    return cues


def wrap(dr, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if dr.textlength(trial, font=f) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def draw_text_c(dr, cx, y, text, f, fill=(255, 255, 255), stroke=8):
    w = dr.textlength(text, font=f)
    dr.text((cx - w / 2, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(20, 14, 24))


def draw_overlay(out, t, cues):
    dr = ImageDraw.Draw(out)
    f = font(50)
    for a, b, g in cues:
        if a - 0.05 <= t <= b + 0.08:
            lines = wrap(dr, g, f, 620)
            y = 1030 - 30 * len(lines)
            for ln in lines:
                draw_text_c(dr, OW / 2, y, ln, f)
                y += 62
            break
    # selo do dia
    k = 1 - ss((t - 66.6) / 0.5)
    if k > 0 and t > 0.3:
        fb = font(34)
        txt = "DIA 2 DE 15"
        w = dr.textlength(txt, font=fb)
        sh = 120 * (1 - k)
        rrect(dr, OW / 2 - w / 2 - 28, 56 - sh, OW / 2 + w / 2 + 28, 118 - sh, 28, (242, 188, 52), w=5)
        dr.text((OW / 2 - w / 2, 66 - sh), txt, font=fb, fill=OUT)
    # votação
    if t >= R.T_OPCOES[0] - 0.1:
        u0 = ss((t - R.T_OPCOES[0]) / 0.4)
        ft = font(46)
        rrect(dr, 40, 60 - 200 * (1 - u0), OW - 40, 190 - 200 * (1 - u0), 34, (30, 24, 52), out=(242, 188, 52), w=6)
        draw_text_c(dr, OW / 2, 78 - 200 * (1 - u0), "Qual deve ser", ft, stroke=0)
        draw_text_c(dr, OW / 2, 128 - 200 * (1 - u0), "o próximo passo?", ft, (242, 188, 52), stroke=0)
        for i, (tt, num, l1, l2, col) in enumerate([
            (R.T_OPCOES[1], "1", "Terminar de", "organizar a casa", (80, 200, 170)),
            (R.T_OPCOES[2], "2", "Cuidar das roupas", "acumuladas", (240, 120, 100))]):
            u = ss((t - tt) / 0.35)
            if u <= 0:
                continue
            y0 = 220 + i * 180 - (1 - u) * 80
            rrect(dr, 40 + (1 - u) * -400, y0, OW - 40 + (1 - u) * -400, y0 + 150, 30, (30, 24, 52), out=col, w=7)
            ell(dr, 112 + (1 - u) * -400, y0 + 75, 46, 46, col, w=5)
            draw_text_c(dr, 112 + (1 - u) * -400, y0 + 36, num, font(62), fill=(30, 24, 52), stroke=0)
            fo = font(37)
            dr.text((176 + (1 - u) * -400, y0 + 28), l1, font=fo, fill=(255, 255, 255))
            dr.text((176 + (1 - u) * -400, y0 + 78), l2, font=fo, fill=(255, 255, 255))
    # fade final
    if t > R.DUR - 0.7:
        k = (t - (R.DUR - 0.7)) / 0.7
        out.paste((0, 0, 0), (0, 0), Image.new("L", out.size, int(255 * min(1, k))))
    if t < 0.4:
        out.paste((0, 0, 0), (0, 0), Image.new("L", out.size, int(255 * (1 - t / 0.4))))


# ------------------------------------------------------------------- quadro
BG = PILE = CUES = None


def init():
    global BG, PILE, CUES
    BG = make_bg()
    PILE = make_pile()
    build_marks()
    build_puffs()
    CUES = build_cues()


def render(t):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    draw_floor_state(img, d, t)
    draw_cabinet(d, t)
    if t >= R.T_REVELA - 0.3:
        draw_reveal_things(d, t)
    # sock no chão atrás do armário até ser pega
    s = rob(t)
    sock_pos = None
    if t < 32.2:
        sock(d, 170, 1262, 0.55, 0.3)
    elif t >= R.T_MEIA_CAI and t < 60:
        sock(d, 300, 1470, 0.55, 1.2)
    # vassoura deitada atrás de Roberto
    g, u, length, mode, _, _ = broom_geom(t)
    if mode in ("chao", "solta"):
        draw_broom(d, g, u, length)
    for it in ITEMS:
        p = item_pos(it, t)
        if p:
            draw_item(d, it["kind"], p[0], p[1])
    draw_bag(d, t)
    # relíquia: raios por trás
    hands_pre = None
    if R.T_RELIQUIA[0] - 1 < t < R.T_RELIQUIA[1] + 1:
        hl_, hr_ = (s["hl"] or default_hands(s)[0]), (s["hr"] or default_hands(s)[1])
        _, _, _, _, _, hrp = arms_geom(s, (hl_, hr_))
        draw_relic(img, d, (hrp[0], hrp[1] - 40), t)
    hl, hr = draw_rob(img, d, s, t)
    if s["sock"] == "hand":
        sock(d, hr[0], hr[1] - 36, 0.7, 0.15)
    draw_puffs(img, t)
    img.paste(PILE, (0, 0), PILE)
    sc, cx, cy = cam(t)
    cw, ch = W / sc, H / sc
    cx = min(max(cx, cw / 2), W - cw / 2)
    cy = min(max(cy, ch / 2), H - ch / 2)
    out = img.resize((OW, OH), Image.LANCZOS, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
    draw_overlay(out, t, CUES)
    return out


def render_file(args):
    i, pasta = args
    render(i / FPS).save(Path(pasta) / f"f{i:05d}.jpg", quality=95)
    return i


def main():
    here = Path(__file__).parent
    if sys.argv[1] == "--teste":
        init()
        tempos = [float(x) for x in sys.argv[2:]]
        frames = [render(t) for t in tempos]
        cols = 4
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * OW // 2, rows * OH // 2))
        for k, fr in enumerate(frames):
            sheet.paste(fr.resize((OW // 2, OH // 2)), ((k % cols) * OW // 2, (k // cols) * OH // 2))
        sheet.save(here / "_teste.png")
        return
    saida = Path(sys.argv[1])
    pasta = here / "_frames"
    pasta.mkdir(exist_ok=True)
    n = int(R.DUR * FPS)
    with Pool(4, initializer=init) as pool:
        for k, _ in enumerate(pool.imap_unordered(render_file, [(i, pasta) for i in range(n)], chunksize=8)):
            if k % 200 == 0:
                print(f"{k}/{n}", flush=True)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(pasta / "f%05d.jpg"),
        "-i", str(here / "audio.wav"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(saida)], check=True)
    for f in pasta.glob("*.jpg"):
        f.unlink()
    pasta.rmdir()


if __name__ == "__main__":
    main()
