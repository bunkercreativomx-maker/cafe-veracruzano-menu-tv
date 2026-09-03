#!/usr/bin/env python3
"""Crea el encabezado de marca (banner aprobado por el cliente):
logo circular a la izquierda + 'CAFÉ' en crema + 'VERACRUZANO' en dorado
+ 'Son y sabor' cursiva debajo, sobre un degradado oscuro translúcido.
Guarda header.png 1920x260 listo para superponer en los videos y HTML.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# --- Fuentes ---
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FI = "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf"   # cursiva

W = 1920
H = 300

# --- Fondo: degradado oscuro translúcido (arriba -> abajo transparente) ---
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
top_alpha = 235
for y in range(H):
    t = y / H
    a = int(top_alpha * (1 - t) ** 1.4)
    d.line([(0, y), (W, y)], fill=(10, 6, 3, a))

# --- Logo circular a la izquierda ---
logo = Image.open("/opt/data/cafe-veracruzano-menu-tv/img/logo.png").convert("RGBA")
logo_size = int(H * 0.58)
logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
# enmascarar: recortar fondo negro exterior a transparente (logo es círculo)
# convertimos los píxeles fuera del círculo a transparente
mask = Image.new("L", logo.size, 0)
ImageDraw.Draw(mask).ellipse((0, 0, logo_size, logo_size), fill=255)
# borde dorado fino
border = logo_size * 0.98
logo_x = 40
logo_y = (H - logo_size) // 2
# fondo negro redondo detrás del logo (para que se vea el círculo)
btn = Image.new("RGBA", (logo_size, logo_size), (15, 10, 5, 235))
btn = Image.composite(btn, Image.new("RGBA", logo.size, (0,0,0,0)), mask)
img.paste(btn, (logo_x, logo_y), mask)
# recortar el fondo negro del logo a transparente, dejar solo el círculo verde
# copiar el logo (su zona circular)
img.alpha_composite(logo, (logo_x, logo_y))

# --- Textos ---
# CAFÉ en crema
f_cafe = ImageFont.truetype(FB, 78)
cafe_txt = "CAFÉ"
cafe_col = (243, 236, 226)          # crema
# VERACRUZANO en dorado, más grande
f_ver = ImageFont.truetype(FB, 96)
ver_txt = "VERACRUZANO"
ver_col = (217, 164, 65)            # dorado
# Son y sabor en cursiva
f_son = ImageFont.truetype(FI, 40)
son_txt = "Son y sabor"
son_col = (224, 199, 154)

# Centrar el bloque de textos respecto a la derecha del logo
block_x = logo_x + logo_size + 50
# medir anchos
w_cafe = d.textlength(cafe_txt, font=f_cafe)
w_ver = d.textlength(ver_txt, font=f_ver)
w_son = d.textlength(son_txt, font=f_son)
max_w = max(w_cafe, w_ver, w_son)

# Centrar verticalmente las 3 líneas (con margen superior extra para no cortar)
line_h_cafe = 95
line_h_ver = 110
line_h_son = 48
total_h = line_h_cafe + line_h_ver + line_h_son
y_start = (H - total_h) // 2 + 12

# dibujar con sombra para legibilidad
def shadow_text(d, xy, txt, font, col, shadow=(0,0,0,200)):
    x, y = xy
    d.text((x+3, y+3), txt, font=font, fill=shadow)
    d.text((x, y), txt, font=font, fill=col)

# CAFÉ (crema) - alineado izquierda dentro del bloque
shadow_text(d, (block_x, y_start), cafe_txt, f_cafe, (*cafe_col, 255))
# VERACRUZANO (dorado) debajo
shadow_text(d, (block_x, y_start + line_h_cafe), ver_txt, f_ver, (*ver_col, 255))
# Son y sabor cursiva
shadow_text(d, (block_x, y_start + line_h_cafe + line_h_ver), son_txt, f_son, (*son_col, 255))

out = "/opt/data/cafe-veracruzano-menu-tv/img/header.png"
img.save(out)
print("OK ->", out, img.size)