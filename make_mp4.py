#!/usr/bin/env python3
"""Genera la cadena de filtros xfade (crossfade) para N imágenes y
construye el comando ffmpeg que produce el MP4 1920x1080.
"""
import os, subprocess, sys

IMG_DIR = "/opt/data/cafe-veracruzano-menu-tv/img"
LOGO = "/opt/data/cafe-veracruzano-menu-tv/img/logo.png"
OUT = "/opt/data/cafe-veracruzano-menu-tv/Cafe_Veracruzano_Menu.mp4"

# Todas las fotos en orden
files = sorted(f for f in os.listdir(IMG_DIR) if f.endswith('.jpg') and f != 'logo.png')
n = len(files)
DUR = 6        # segundos por foto
TRANS = 1.0    # duración del crossfade
FPS = 30
W, H = 1920, 1080

print(f"{n} fotos, {DUR}s cada una, crossfade {TRANS}s")

# --- Entradas: cada imagen como stream de video ---
inputs = []
for f in files:
    inputs += ['-loop','1','-t',str(DUR),'-i',os.path.join(IMG_DIR,f)]

# --- Filtro xfade encadenado ---
# La primera entrada es el stream 0. Cada xfade toma el resultado anterior
# y la siguiente entrada. offset acumulado = i*(DUR - TRANS)
filt = ""
prev = "0:v"
total = DUR
for i in range(1, n):
    off = i*(DUR - TRANS)
    label = f"x{i-1}"
    filt += f"[{prev}][{i}:v]xfade=transition=fade:duration={TRANS}:offset={off}[{label}];"
    prev = label
total = n*DUR - (n-1)*TRANS

# --- Escalar a 1920x1080 + overlay del logo en esquina sup-izq ---
filt += f"[{prev}]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,format=yuv420p[base];"
# logo redimensionado y con fondo blanco (round) en esquina
logo_scale = 140
filt += f"[{n}:v]scale={logo_scale}:-1,format=rgba,pad={logo_scale}:{logo_scale}:(ow-iw)/2:(oh-ih)/2,colorchannelmixer=aa=1.0[logo];"
filt += f"[base][logo]overlay=60:60[vout]"

inputs += ['-i', LOGO]  # índice n

cmd = ['ffmpeg','-y'] + inputs + [
    '-filter_complex', filt,
    '-map','[vout]','-r',str(FPS),
    '-c:v','libx264','-preset','medium','-crf','20',
    '-pix_fmt','yuv420p','-movflags','+faststart',
    '-t',str(total),
    OUT
]

print("Duracion total (s):", round(total,1))
print("CMD:", ' '.join(cmd)[:300], "...")
r = subprocess.run(cmd, capture_output=True, text=True)
print("EXIT:", r.returncode)
if r.returncode != 0:
    print(r.stderr[-2000:])
else:
    print("OK ->", OUT, os.path.getsize(OUT)//1024//1024, "MB")
