"""Draw the 22 November 2026 world-news poster with pure stdlib Python.

Writes a 1024x1024 PNG to the given path. No network, no input files, no
clock, no randomness, so two runs produce identical bytes.
"""

import struct
import zlib

W, H = 1024, 1024

CREAM = (246, 241, 227)
NAVY = (22, 38, 76)
RED = (192, 57, 43)
WHITE = (255, 255, 255)
INK = (28, 28, 28)
GREY = (110, 110, 100)
GOLD = (201, 162, 39)
TEAL = (15, 118, 110)
GREEN = (46, 125, 50)
ORANGE = (214, 106, 20)
PURPLE = (106, 66, 148)
STEEL = (58, 96, 140)
BROWN = (122, 74, 30)
DARKRED = (146, 32, 24)

# 5x7 bitmap font: '#' is on, '.' is off. Uppercase, digits, punctuation.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def rect_outline(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.set(xx, yy, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for a in range(t):
                self.set(x + a, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx - x

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centered(self, y, s, scale, color):
        w = self.text_width(s, scale)
        self.text((self.w - w) // 2, y, s, scale, color)


def wrap(text, max_chars):
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_globe(cv, x, y, s, color):
    cv.ring(x + s // 2, y + s // 2, s // 2 - 2, color, 4)
    cv.line(x + 4, y + s // 2, x + s - 4, y + s // 2, color, 3)
    cv.line(x + s // 2, y + 4, x + s // 2, y + s - 4, color, 3)
    cv.line(x + 8, y + s // 4, x + s - 8, y + s // 4, color, 2)
    cv.line(x + 8, y + 3 * s // 4, x + s - 8, y + 3 * s // 4, color, 2)


def draw_court(cv, x, y, s, color):
    cv.triangle(x + 6, y + 26, x + s - 6, y + 26, x + s // 2, y + 6, color)
    cv.rect(x + 6, y + 30, s - 12, 5, color)
    for cx in (x + 16, x + s // 2 - 3, x + s - 22):
        cv.rect(cx, y + 38, 6, s - 52, color)
    cv.rect(x + 6, y + s - 14, s - 12, 5, color)


def draw_tanker(cv, x, y, s, color):
    cv.rect(x + 10, y + s // 2, s - 20, 12, color)
    cv.rect(x + s - 34, y + s // 2 - 18, 22, 18, color)
    cv.rect(x + 18, y + s // 2 - 10, 14, 10, color)
    cv.rect(x + 36, y + s // 2 - 10, 14, 10, color)
    for wy in (y + s - 22, y + s - 12):
        for wx in range(x + 6, x + s - 6, 14):
            cv.line(wx, wy, wx + 8, wy, color, 3)


def draw_warship(cv, x, y, s, color):
    cv.triangle(x + 8, y + s // 2 + 8, x + s - 8, y + s // 2 + 8,
                x + s // 2, y + s // 2 - 22, color)
    cv.rect(x + s // 2 - 3, y + 14, 6, 22, color)
    cv.line(x + s // 2 - 18, y + 22, x + s // 2 + 18, y + 22, color, 3)
    for wy in (y + s - 20, y + s - 10):
        for wx in range(x + 6, x + s - 6, 14):
            cv.line(wx, wy, wx + 8, wy, color, 3)


def draw_cuffs(cv, x, y, s, color):
    cv.ring(x + 22, y + s // 2, 18, color, 5)
    cv.ring(x + s - 22, y + s // 2, 18, color, 5)
    cv.line(x + 22, y + s // 2 - 14, x + s - 22, y + s // 2 - 14, color, 4)


def draw_plane(cv, x, y, s, color):
    cv.line(x + 8, y + s // 2, x + s - 10, y + s // 2, color, 5)
    cv.triangle(x + s - 26, y + s // 2 - 26, x + s - 8, y + s // 2 - 4,
                x + s - 14, y + s // 2 + 2, color)
    cv.triangle(x + s // 2 - 6, y + s // 2, x + s // 2 + 10, y + s // 2,
                x + s // 2 - 2, y + s - 14, color)
    cv.triangle(x + 10, y + s // 2 - 2, x + 22, y + s // 2 - 2,
                x + 12, y + s // 2 - 18, color)


def draw_flame(cv, x, y, s, color):
    cv.triangle(x + s // 2 - 20, y + s - 18, x + s // 2 + 20, y + s - 18,
                x + s // 2, y + 8, color)
    cv.triangle(x + s // 2 - 10, y + s - 18, x + s // 2 + 10, y + s - 18,
                x + s // 2 - 6, y + s // 2, color)
    cv.rect(x + 8, y + s - 14, s - 16, 6, color)


def draw_boat(cv, x, y, s, color):
    cv.triangle(x + 10, y + s // 2, x + s - 10, y + s // 2,
                x + s // 2, y + s - 16, color)
    cv.line(x + s // 2, y + 12, x + s // 2, y + s // 2, color, 4)
    cv.triangle(x + s // 2, y + 14, x + s - 14, y + 30,
                x + s // 2, y + 30, color)
    for wy in (y + s - 12,):
        for wx in range(x + 6, x + s - 6, 14):
            cv.line(wx, wy, wx + 8, wy, color, 3)


def draw_missile(cv, x, y, s, color):
    cv.line(x + 16, y + s - 16, x + s - 16, y + 16, color, 6)
    cv.triangle(x + s - 26, y + 8, x + s - 8, y + 8,
                x + s - 8, y + 26, color)
    cv.triangle(x + 12, y + s - 24, x + 30, y + s - 8,
                x + 12, y + s - 8, color)
    for (sx, sy) in ((x + 14, y + 16), (x + 30, y + 34), (x + 52, y + 14)):
        cv.circle(sx, sy, 3, color)


ICONS = {
    'globe': draw_globe,
    'court': draw_court,
    'tanker': draw_tanker,
    'warship': draw_warship,
    'cuffs': draw_cuffs,
    'plane': draw_plane,
    'flame': draw_flame,
    'boat': draw_boat,
    'missile': draw_missile,
}

# (kicker, headline, summary, icon, icon colour)
STORIES = [
    ("THE HAGUE", "COURT: MYANMAR GUILTY OF GENOCIDE",
     "MYANMAR GUILTY OF GENOCIDE, WORLD COURT RULES.",
     'court', NAVY),
    ("GULF CRISIS", "TANKERS HIT NEAR HORMUZ",
     "TWO TANKERS HIT MINES, IRAN SAYS. TRUMP WEIGHS STRIKES.",
     'tanker', DARKRED),
    ("UKRAINE WAR", "KYIV SANK RUSSIAN WARSHIP",
     "DRONE ATTACK SANK RUSSIAN SHIP OFF LIBYA, KYIV SAYS.",
     'warship', STEEL),
    ("MEXICO", "CARTEL BOSS CAPTURED",
     "11 DEAD AS MEXICO SEIZES CARTEL BOSS.",
     'cuffs', PURPLE),
    ("USA", "DELTA OUTAGE DELAYS 1,600 FLIGHTS",
     "SYSTEM FAILURE GROUNDS US PLANES. NOT A HACK.",
     'plane', TEAL),
    ("INDONESIA", "FACTORY FIRE IN INDONESIA",
     "THREE DEAD, DOZENS MISSING AFTER FACTORY BLAZE.",
     'flame', ORANGE),
    ("NIGERIA", "BOAT CAPSIZES IN NIGERIA",
     "AT LEAST 24 DEAD ON THE WAY TO A FUNERAL.",
     'boat', GREEN),
    ("EUROPE", "RUSSIAN MISSILES LAND IN POLAND",
     "NATO CALLS IT A VIOLATION AS DRILLS RUN NEARBY.",
     'missile', BROWN),
]

LEAD_HEAD = "CLIMATE TALKS COLLAPSE"
LEAD_DECK = ("COP31 IN TURKEY ENDS WITH NO DEAL. FOSSIL FUELS LEFT "
             "UNMENTIONED AFTER OVERTIME TALKS.")


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def build_entry(path):
    cv = Canvas(W, H, CREAM)

    # Masthead.
    cv.rect(0, 0, W, 118, NAVY)
    cv.text_centered(14, "THE WORLD IN ONE DAY", 5, WHITE)
    cv.text_centered(78, "SUNDAY 22 NOVEMBER 2026", 3, GOLD)
    cv.rect(0, 118, W, 6, RED)

    # Lead story: COP31 collapse.
    lx, ly, lw, lh = 24, 138, W - 48, 216
    cv.rect(lx, ly, lw, lh, WHITE)
    cv.rect_outline(lx, ly, lw, lh, NAVY, 2)
    cv.text(lx + 20, ly + 16, "LEAD STORY  -  TURKEY", 2, RED)
    cv.text(lx + 20, ly + 46, LEAD_HEAD, 4, NAVY)
    deck = wrap(LEAD_DECK, 52)
    yy = ly + 108
    for line in deck:
        cv.text(lx + 20, yy, line, 2, INK)
        yy += 30
    # Globe pictogram on the right of the lead panel.
    gx, gy = lx + lw - 200, ly + 28
    cv.rect(gx, gy, 170, 160, (232, 240, 235))
    cv.rect_outline(gx, gy, 170, 160, TEAL, 2)
    draw_globe(cv, gx + 25, gy + 18, 120, TEAL)
    cv.text(gx + 22, gy + 138, "COP31", 2, TEAL)

    # Story grid: 2 columns x 4 rows.
    pw, ph, gap = 476, 142, 12
    x0, y0 = 24, 368
    for i, (kicker, head, summ, icon, color) in enumerate(STORIES):
        col = i % 2
        row = i // 2
        px = x0 + col * (pw + gap)
        py = y0 + row * (ph + gap)
        cv.rect(px, py, pw, ph, WHITE)
        cv.rect_outline(px, py, pw, ph, GREY, 1)
        cv.rect(px, py, 6, ph, color)
        ix, iy = px + 16, py + 21
        cv.rect(ix, iy, 100, 100, color)
        ICONS[icon](cv, ix, iy, 100, WHITE)
        tx = px + 130
        cv.text(tx, py + 12, kicker, 1, RED)
        head_lines = wrap(head, 27)
        yy = py + 30
        for line in head_lines[:2]:
            cv.text(tx, yy, line, 2, NAVY)
            yy += 28
        summ_lines = wrap(summ, 27)
        yy = py + 88
        for line in summ_lines[:2]:
            cv.text(tx, yy, line, 2, INK)
            yy += 26

    # Footer.
    cv.rect(0, 986, W, 2, NAVY)
    cv.text_centered(996, "ALL STORIES FIRST REPORTED ON 22 NOVEMBER 2026", 1, GREY)

    data = png_bytes(cv)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)
