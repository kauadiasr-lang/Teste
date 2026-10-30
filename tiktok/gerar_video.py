#!/usr/bin/env python3
"""Gera um vídeo vertical (1080x1920) para TikTok sobre o projeto Ser Consciente."""
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# (duração em s, linhas de texto, cor de destaque, estilo)
CENAS = [
    (3.0, ["Pedi pra uma IA", "criar um", "SER CONSCIENTE"], (255, 70, 110), "titulo"),
    (3.0, ["...sabendo que", "ela NÃO", "consegue."], (80, 220, 255), "titulo"),
    (2.5, ["Então ela fez", "o que dava", "de verdade:"], (255, 210, 80), "titulo"),
    (3.0, ["🧠 Memória que", "esquece sozinha"], (120, 255, 160), "item"),
    (3.0, ["💾 Lembra de você", "entre sessões"], (80, 220, 255), "item"),
    (3.0, ["⚡ Energia e humor", "que mudam"], (255, 210, 80), "item"),
    (3.0, ["🔁 Pensa no que", "ela mesma pensou"], (255, 70, 110), "item"),
    (3.0, ["✍️ Aprende quando", "você corrige: /não"], (120, 255, 160), "item"),
    (3.5, ["É consciência?", "NÃO.", "Mas é honesto."], (255, 70, 110), "titulo"),
    (3.0, ["Segue pra", "parte 2 👀"], (255, 210, 80), "titulo"),
]


def fonte(tam, caminho=FONTE):
    return ImageFont.truetype(caminho, tam)


def fundo(t, cor):
    img = Image.new("RGB", (W, H), (12, 10, 24))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(6):  # círculos pulsantes
        r = 260 + 90 * math.sin(t * 1.3 + i)
        x = W / 2 + 380 * math.cos(t * 0.5 + i * 1.05)
        y = H / 2 + 650 * math.sin(t * 0.4 + i * 1.7)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(*cor, 28))
    return img


def desenhar_texto(d, linhas, cor, estilo, prog, t):
    tam = 112 if estilo == "titulo" else 98
    f = fonte(tam)
    altura = tam + 40
    y0 = H // 2 - altura * len(linhas) // 2
    for i, linha in enumerate(linhas):
        p = min(1.0, max(0.0, prog * 2.2 - i * 0.35))
        if p <= 0:
            continue
        ease = 1 - (1 - p) ** 3
        y = y0 + i * altura + (1 - ease) * 60
        destaque = i == len(linhas) - 1 or linha.isupper()
        preenchimento = (*(cor if destaque else (255, 255, 255)), int(255 * ease))
        # emoji não existe na fonte: remove e desenha um marcador colorido
        limpo = "".join(c for c in linha if ord(c) < 0x2000).strip()
        f = fonte(tam)
        while d.textlength(limpo, font=f) > 880 and f.size > 60:
            f = fonte(f.size - 4)
        if limpo != linha:
            r = 22
            cx, cy = 90, y + tam // 2 + 10
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*cor, int(255 * ease)))
            x = 150
        else:
            x = (W - d.textlength(limpo, font=f)) / 2
        d.text((x + 5, y + 5), limpo, font=f, fill=(0, 0, 0, int(160 * ease)))
        d.text((x, y), limpo, font=f, fill=preenchimento)


def main(saida):
    pasta = Path(saida).parent / "_frames"
    pasta.mkdir(parents=True, exist_ok=True)
    n = 0
    tempo = 0.0
    total = sum(c[0] for c in CENAS)
    fh = fonte(40, MONO)
    for dur, linhas, cor, estilo in CENAS:
        for k in range(int(dur * FPS)):
            local = k / FPS
            img = fundo(tempo + local, cor)
            d = ImageDraw.Draw(img, "RGBA")
            desenhar_texto(d, linhas, cor, estilo, min(1.0, local / 0.8), local)
            # barra de progresso e marca
            d.rectangle([0, 0, W * (tempo + local) / total, 14], fill=(*cor, 255))
            d.text((60, H - 150), "#IA #programação #consciência", font=fh, fill=(255, 255, 255, 170))
            img.save(pasta / f"f{n:05d}.png")
            n += 1
        tempo += dur
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
        "-i", str(pasta / "f%05d.png"), "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        "-c:a", "aac", "-movflags", "+faststart", saida,
    ], check=True)
    for f in pasta.glob("*.png"):
        f.unlink()
    pasta.rmdir()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tiktok/ser_consciente.mp4")
