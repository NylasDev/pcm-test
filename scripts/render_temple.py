"""Procedural render of a hexastyle Doric temple front (Delphi-like),
lit from the upper left, as a grayscale source for engrave.py."""
import sys
import numpy as np
from PIL import Image, ImageFilter

W, H = 1400, 1050
img = np.zeros((H, W), dtype=np.float32)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

# --- sky: light, slightly darker toward top-right for some hatch texture
sky = 0.93 - 0.10 * (1 - yy / H) * (xx / W)
img[:] = sky

L = np.array([-0.62, -0.35, 0.70], dtype=np.float32)
L /= np.linalg.norm(L)

def fill(mask, val):
    img[mask] = val if np.isscalar(val) else val[mask]

# geometry
cx = W * 0.54
n_col = 6
col_r0 = 44.0            # bottom radius
col_r1 = 37.0            # top radius (entasis taper)
spacing = 150.0
stylo_top = 830.0
col_top = 430.0
xs = [cx + (i - (n_col - 1) / 2) * spacing for i in range(n_col)]
left = xs[0] - col_r0 - 40
right = xs[-1] + col_r0 + 40

# --- ground plane
ground = (yy > 935)
img[ground] = (0.90 - 0.10 * ((yy - 935) / (H - 935)))[ground]

# --- cella wall behind colonnade (deep shadow)
wall = (xx > left + 18) & (xx < right - 18) & (yy > col_top) & (yy < stylo_top)
img[wall] = (0.20 + 0.10 * ((yy - col_top) / (stylo_top - col_top)))[wall]
# doorway even darker
door = (abs(xx - cx) < 70) & (yy > 560) & (yy < stylo_top)
img[door] = 0.07

# --- stylobate steps (3)
step_h = 35.0
for k in range(3):
    top = stylo_top + k * step_h
    ext = 26 * (k + 1)
    sx0, sx1 = left - ext, right + ext
    tread = (xx > sx0) & (xx < sx1) & (yy >= top) & (yy < top + 9)
    riser = (xx > sx0) & (xx < sx1) & (yy >= top + 9) & (yy < top + step_h)
    img[tread] = 0.90
    img[riser] = (0.55 + 0.08 * (xx - sx0) / (sx1 - sx0) * -1 + 0.04)[riser]
    # left end faces light, right end in shade
    endr = (xx > sx1 - 6) & (xx < sx1) & (yy >= top) & (yy < top + step_h)
    img[endr] = 0.40

# --- columns
def column(xc):
    t = np.clip((yy - col_top) / (stylo_top - col_top), 0, 1)
    r = col_r1 + (col_r0 - col_r1) * t
    u = (xx - xc) / r
    m = (abs(u) < 1) & (yy > col_top + 34) & (yy < stylo_top)
    nz = np.sqrt(np.clip(1 - u * u, 0, 1))
    theta = np.arcsin(np.clip(u, -1, 1))
    flutes = 0.5 + 0.5 * np.cos(theta * 20)
    diff = np.clip(u * L[0] + nz * L[2], 0, 1)
    val = 0.12 + 0.74 * diff
    val = val * (1 - 0.16 * (1 - flutes) * nz)
    img[m] = val[m]
    # cast shadow on stylobate tread to the right
    sh = (xx > xc + r * 0.2) & (xx < xc + r + 70) & (yy >= stylo_top) & (yy < stylo_top + 9)
    img[sh] = np.minimum(img[sh], 0.55)
    # capital: echinus (rounded) + abacus (block)
    ech = (yy > col_top + 12) & (yy <= col_top + 34)
    er = col_r1 + 18 * np.clip(1 - (yy - (col_top + 12)) / 22, 0, 1) ** 0.6
    ue = (xx - xc) / er
    me = ech & (abs(ue) < 1)
    nze = np.sqrt(np.clip(1 - ue * ue, 0, 1))
    de = np.clip(ue * L[0] + nze * L[2] - 0.15 * (yy - col_top - 12) / 22, 0, 1)
    img[me] = (0.20 + 0.72 * de)[me]
    ab = (yy > col_top) & (yy <= col_top + 12) & (abs(xx - xc) < col_r1 + 22)
    img[ab] = 0.82
    img[ab & (xx > xc + col_r1 + 16)] = 0.45

for xc in xs:
    column(xc)

# --- entablature
arch_top, arch_bot = col_top - 62, col_top
ent_l, ent_r = left - 10, right + 10
arch = (xx > ent_l) & (xx < ent_r) & (yy > arch_top) & (yy <= arch_bot)
img[arch] = 0.72
img[(xx > ent_l) & (xx < ent_r) & (yy > arch_bot - 6) & (yy <= arch_bot)] = 0.48
# taenia
img[(xx > ent_l) & (xx < ent_r) & (yy > arch_top) & (yy <= arch_top + 7)] = 0.90

frz_top = arch_top - 70
frz = (xx > ent_l) & (xx < ent_r) & (yy > frz_top) & (yy <= arch_top)
img[frz] = 0.58
# triglyphs over each column and between
tg_w = 40
centers = []
for i, xc in enumerate(xs):
    centers.append(xc)
    if i < len(xs) - 1:
        centers.append((xc + xs[i + 1]) / 2)
centers = [ent_l + tg_w / 2 + 2] + centers + [ent_r - tg_w / 2 - 2]
for c in centers:
    tg = frz & (abs(xx - c) < tg_w / 2)
    img[tg] = 0.80
    for g in (-10, 0, 10):
        groove = frz & (abs(xx - (c + g)) < 2.6) & (yy > frz_top + 8)
        img[groove] = 0.30
# cornice (projecting) with shadow beneath
cor_top = frz_top - 30
cor = (xx > ent_l - 26) & (xx < ent_r + 26) & (yy > cor_top) & (yy <= frz_top)
img[cor] = 0.70
img[(xx > ent_l - 26) & (xx < ent_r + 26) & (yy > frz_top - 8) & (yy <= frz_top)] = 0.40
shadow_under = (xx > ent_l) & (xx < ent_r) & (yy > frz_top) & (yy <= frz_top + 14)
img[shadow_under] = img[shadow_under] * 0.55
# mutules: small blocks under cornice
for c in centers:
    mb = (abs(xx - c) < 16) & (yy > frz_top - 8) & (yy <= frz_top)
    img[mb] = 0.62

# --- pediment
apex_y = cor_top - 210
ped_l, ped_r = ent_l - 26, ent_r + 26
half = (ped_r - ped_l) / 2
pcx = (ped_l + ped_r) / 2
slope = (cor_top - apex_y) / half
inside_outer = (yy > apex_y + slope * abs(xx - pcx)) & (yy <= cor_top) & (xx > ped_l) & (xx < ped_r)
img[inside_outer] = 0.66  # raking cornice band
inner_off = 34
inside_inner = (yy > apex_y + inner_off + slope * abs(xx - pcx)) & (yy <= cor_top - 14) & \
               (xx > ped_l + 40) & (xx < ped_r - 40)
img[inside_inner] = (0.50 + 0.10 * (xx - pcx) / half * -1)[inside_inner]
# shadow band under raking cornice inside tympanum
under = inside_inner & (yy < apex_y + inner_off + 14 + slope * abs(xx - pcx))
img[under] = img[under] * 0.55
# central sun-disc relief in tympanum (Apollo)
d = np.sqrt((xx - pcx) ** 2 + (yy - (cor_top - 70)) ** 2) / 44
disc = inside_inner & (d < 1)
nzd = np.sqrt(np.clip(1 - d * d, 0, 1))
ux = (xx - pcx) / 44
uy = (yy - (cor_top - 70)) / 44
img[disc] = np.clip(0.15 + 0.8 * (ux * L[0] + uy * L[1] + nzd * L[2]), 0.1, 0.95)[disc]
for k in range(16):
    ang = k * np.pi / 8
    rx = pcx + np.cos(ang) * 64
    ry = (cor_top - 70) + np.sin(ang) * 64 * 0.9
    ray = inside_inner & (np.sqrt((xx - rx) ** 2 + (yy - ry) ** 2) < 8)
    img[ray] = 0.82
# soft vignette + slight blur so hatching follows tones, not pixel edges
img = np.clip(img, 0, 1)
im = Image.fromarray((img * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
im.save(sys.argv[1])
print("saved", sys.argv[1], im.size)
