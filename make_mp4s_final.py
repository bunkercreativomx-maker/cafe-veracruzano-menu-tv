#!/usr/bin/env python3
"""Genera dos MP4 (720p, H.264 Main, max compatibilidad) para Cafe Veracruzano.
SOLO imagenes, SIN logo ni texto de marca.
"""
import os, subprocess

IMG_DIR = "/opt/data/cafe-veracruzano-menu-tv/img"
OUT_DIR = "/opt/data/cafe-veracruzano-menu-tv/videos_final"
os.makedirs(OUT_DIR, exist_ok=True)

POSTRES = [
    'brownie-helado.jpg','cafe-helado-dos.jpg','cafe-helado-toast.jpg',
    'capuchinos-dos.jpg','capuchinos-tres.jpg','malteadas-fresa.jpg',
    'tamales-bandeja.jpg','tamales-hoja.jpg',
]
COCINA = [
    'hotcakes-fresa-platano.jpg','hotcakes-fresas-flor.jpg','hotcakes-fruta.jpg',
    'hotcakes-mantequilla.jpg','omelette-cafe.jpg','omelette-roll.jpg',
    'sandwich-queso.jpg','tacos.jpg','tlayudas.jpg','torta-lomito.jpg',
    'tortas-cecina.jpg','tortas-chilaquiles.jpg',
]

DUR = 6
TRANS = 1.0
FPS = 30
W, H = 1280, 720

def build_mp4(files, out, label):
    n = len(files)
    print(f"\n=== {label}: {n} fotos -> {out} ===")
    inputs = []
    for f in files:
        inputs += ['-loop','1','-t',str(DUR),'-i',os.path.join(IMG_DIR,f)]
    filt = ""
    prev = "0:v"
    for i in range(1, n):
        off = i*(DUR - TRANS)
        lab = f"x{i-1}"
        filt += f"[{prev}][{i}:v]xfade=transition=fade:duration={TRANS}:offset={off}[{lab}];"
        prev = lab
    total = n*DUR - (n-1)*TRANS
    filt += f"[{prev}]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,format=yuv420p[vout]"
    cmd = ['ffmpeg','-y'] + inputs + [
        '-filter_complex', filt, '-map','[vout]','-r',str(FPS),
        '-c:v','libx264','-profile:v','main','-level','3.1','-preset','medium','-crf','21',
        '-pix_fmt','yuv420p','-movflags','+faststart','-t',str(total), out]
    print("duracion(s):", round(total,1))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR:", r.stderr[-2000:])
    else:
        print("OK ->", out, os.path.getsize(out)//1024//1024, "MB")

build_mp4(POSTRES, os.path.join(OUT_DIR,"CafeVeracruzano_POSTRES_CAFES_TAMALES.mp4"), "Postres/Cafes/Tamales (solo imagenes)")
build_mp4(COCINA, os.path.join(OUT_DIR,"CafeVeracruzano_MENU_COMPLETO.mp4"), "Menu completo (solo imagenes)")
print("\nDONE")