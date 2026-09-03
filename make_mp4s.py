#!/usr/bin/env python3
"""Genera dos MP4 1920x1080 para Cafe Veracruzano:
  - menu completo (cocina)
  - solo postres/cafes/tamales (dia sin servicio de cocina)
Con crossfade entre fotos y logo en esquina.
"""
import os, subprocess

IMG_DIR = "/opt/data/cafe-veracruzano-menu-tv/img"
LOGO = os.path.join(IMG_DIR, "logo.png")

# --- Grupos de fotos ---
POSTRES = [  # dia sin cocina
    'brownie-helado.jpg',
    'cafe-helado-dos.jpg',
    'cafe-helado-toast.jpg',
    'capuchinos-dos.jpg',
    'capuchinos-tres.jpg',
    'malteadas-fresa.jpg',
    'tamales-bandeja.jpg',
    'tamales-hoja.jpg',
]
COCINA = [  # menu normal
    'hotcakes-fresa-platano.jpg',
    'hotcakes-fresas-flor.jpg',
    'hotcakes-fruta.jpg',
    'hotcakes-mantequilla.jpg',
    'omelette-cafe.jpg',
    'omelette-roll.jpg',
    'sandwich-queso.jpg',
    'tacos.jpg',
    'tlayudas.jpg',
    'torta-lomito.jpg',
    'tortas-cecina.jpg',
    'tortas-chilaquiles.jpg',
]

DUR = 6       # seg por foto
TRANS = 1.0   # crossfade
FPS = 30
W, H = 1920, 1080

def build_mp4(files, out, label):
    n = len(files)
    print(f"\n=== {label}: {n} fotos -> {out} ===")
    inputs = []
    for f in files:
        inputs += ['-loop','1','-t',str(DUR),'-i',os.path.join(IMG_DIR,f)]
    # xfade chain
    filt = ""
    prev = "0:v"
    for i in range(1, n):
        off = i*(DUR - TRANS)
        lab = f"x{i-1}"
        filt += f"[{prev}][{i}:v]xfade=transition=fade:duration={TRANS}:offset={off}[{lab}];"
        prev = lab
    total = n*DUR - (n-1)*TRANS
    filt += f"[{prev}]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,format=yuv420p[base];"
    logo_scale = 130
    filt += f"[{n}:v]scale={logo_scale}:-1,format=rgba,pad={logo_scale}:{logo_scale}:(ow-iw)/2:(oh-ih)/2,colorchannelmixer=aa=1.0[logo];"
    filt += f"[base][logo]overlay=50:50[vout]"
    inputs += ['-i', LOGO]
    cmd = ['ffmpeg','-y'] + inputs + [
        '-filter_complex', filt, '-map','[vout]','-r',str(FPS),
        '-c:v','libx264','-preset','medium','-crf','20',
        '-pix_fmt','yuv420p','-movflags','+faststart','-t',str(total), out]
    print("duracion(s):", round(total,1))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR:", r.stderr[-1500:])
    else:
        print("OK ->", out, os.path.getsize(out)//1024//1024, "MB")

build_mp4(POSTRES, "/opt/data/cafe-veracruzano-menu-tv/CafeVeracruzano_POSTRES_CAFES_TAMALES.mp4", "Postres/Cafes/Tamales")
build_mp4(COCINA, "/opt/data/cafe-veracruzano-menu-tv/CafeVeracruzano_MENU_COMPLETO.mp4", "Menu completo (cocina)")
print("\nDONE")
